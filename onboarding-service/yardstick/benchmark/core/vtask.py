
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
from collections import OrderedDict

import yaml
import atexit
import ipaddress
import time
import logging
import uuid
import collections

from six.moves import filter
from jinja2 import Environment

from yardstick.benchmark.core.task import *
from yardstick.benchmark.contexts.base import Context
from yardstick.benchmark.runners import base as base_runner
from yardstick.common.yaml_loader import yaml_load
from yardstick.dispatcher.base import Base as DispatcherBase
from yardstick.common.task_template import TaskTemplate
from yardstick.common import utils
from yardstick.common import constants
from yardstick.common.html_template import report_template

def _is_background_scenario(scenario):
    if "run_in_background" in scenario:
        return scenario["run_in_background"]
    else:
        return False


class VTask(Task):

    def __init__(self):
        Task.__init__(self)
        self.arr_scenarios = []
        self.run_in_parallels = []

    def pre_start(self, args, **kwargs):
        atexit.register(self.atexit_handler)
        task_id = getattr(args, 'task_id')
        self.task_id = task_id if task_id else str(uuid.uuid4())
        self._set_log()
        try:
            output_config = utils.parse_ini_file(config_file)
        except Exception:
            # all error will be ignore, the default value is {}
            output_config = {}

        self._init_output_config(output_config)
        self._set_output_config(output_config, args.output_file)
        LOG.debug('Output configuration is: %s', output_config)

        self._set_dispatchers(output_config)

        # update dispatcher list
        if 'file' in output_config['DEFAULT']['dispatcher']:
            result = {'status': 0, 'result': {}}
            utils.write_json_to_file(args.output_file, result)

        total_start_time = time.time()
        parser = TaskParser(args.inputfile[0])
        if args.suite:
            # 1.parse suite, return suite_params info
            task_files, task_args, task_args_fnames = \
                parser.parse_suite()
        else:
            task_files = [parser.path]
            task_args = [args.task_args]
            task_args_fnames = [args.task_args_file]

            LOG.debug("task_files:%s, task_args:%s, task_args_fnames:%s",
                  task_files, task_args, task_args_fnames)

        if args.parse_only:
            sys.exit(0)

        return task_files, task_args, task_args_fnames, parser


    def do_onboard(self, task_files, task_args, task_args_fnames, parser):
        for i in range(0, len(task_files)):
            one_task_start_time = time.time()
            parser.path = task_files[i]
            scenarios, run_in_parallel, meet_precondition, contexts = \
                parser.parse_task(self.task_id, task_args[i],
                                  task_args_fnames[i])

            self.contexts.extend(contexts)
            self.arr_scenarios.append(scenarios)
            self.run_in_parallels.append(run_in_parallel)

            if not meet_precondition:
                LOG.info("meet_precondition is %s, please check envrionment",
                         meet_precondition)
                continue

            """Deploys context and calls runners"""
            for context in self.contexts:
                context.deploy()


    def do_benchmark(self, args, task_files_):
        testcases = {}
        parser = TaskParser(args.inputfile[0])
        if args.suite:
            # 1.parse suite, return suite_params info
            task_files, task_args, task_args_fnames = \
                parser.parse_suite()
        else:
            task_files = [parser.path]

        try:
            output_config = utils.parse_ini_file(config_file)
        except Exception:
            # all error will be ignore, the default value is {}
            output_config = {}

        total_start_time = time.time()

        for i in range(0, len(task_files)):
            one_task_start_time = time.time()
            case_name = os.path.splitext(os.path.basename(task_files[i]))[0]
            try:
                data = self._run(self.arr_scenarios[i], self.run_in_parallels[i], args.output_file)
            except KeyboardInterrupt:
                raise
            except Exception:
                LOG.error('Testcase: "%s" FAILED!!!', case_name, exc_info=True)
                testcases[case_name] = {'criteria': 'FAIL', 'tc_data': []}
            else:
                LOG.info('Testcase: "%s" SUCCESS!!!', case_name)
                testcases[case_name] = {'criteria': 'PASS', 'tc_data': data}

            if args.keep_deploy:
                # keep deployment, forget about stack
                # (hide it for exit handler)
                self.contexts = []
            else:
                for context in self.contexts[::-1]:
                    context.undeploy()
                self.contexts = []

            one_task_end_time = time.time()
            LOG.info("Task %s finished in %d secs", task_files[i],
                     one_task_end_time - one_task_start_time)

        result = self._get_format_result(testcases)
        LOG.info('-----------------------------------------------------')
        LOG.info(result)
        LOG.info('------------------------------')
        self._do_output(output_config, result)
        self._generate_reporting(result)

        total_end_time = time.time()
        LOG.info("Total finished in %d secs",
                 total_end_time - total_start_time)

        scenario = self.arr_scenarios[len(self.arr_scenarios) - 1][0]
        LOG.info("To generate report, execute command "
                 "'yardstick report generate %(task_id)s %(tc)s'", scenario)
        LOG.info("Task ALL DONE, exiting")
        return result


    def _run(self, scenarios, run_in_parallel, output_file):
        background_runners = []
        result = []
        # Start all background scenarios
        for scenario in filter(_is_background_scenario, scenarios):
            scenario["runner"] = dict(type="Duration", duration=1000000000)
            runner = self.run_one_scenario(scenario, output_file)
            background_runners.append(runner)

        runners = []
        if run_in_parallel:
            for scenario in scenarios:
                if not _is_background_scenario(scenario):
                    runner = self.run_one_scenario(scenario, output_file)
                    runners.append(runner)

            # Wait for runners to finish
            for runner in runners:
                status = runner_join(runner, self.outputs, result)
                if status != 0:
                    raise RuntimeError(
                        "{0} runner status {1}".format(runner.__execution_type__, status))
                LOG.info("Runner ended, output in %s", output_file)
        else:
            # run serially
            for scenario in scenarios:
                if not _is_background_scenario(scenario):
                    runner = self.run_one_scenario(scenario, output_file)
                    status = runner_join(runner, self.outputs, result)
                    if status != 0:
                        LOG.error('Scenario NO.%s: "%s" ERROR!',
                                  scenarios.index(scenario) + 1,
                                  scenario.get('type'))
                        raise RuntimeError(
                            "{0} runner status {1}".format(runner.__execution_type__, status))
                    LOG.info("Runner ended, output in %s", output_file)

        # Abort background runners
        for runner in background_runners:
            runner.abort()

        # Wait for background runners to finish
        for runner in background_runners:
            status = runner.join(self.outputs, result, JOIN_TIMEOUT)
            if status is None:
                # Nuke if it did not stop nicely
                base_runner.Runner.terminate(runner)
                runner.join(self.outputs, result, JOIN_TIMEOUT)
            base_runner.Runner.release(runner)

            print("Background task ended")
        return result