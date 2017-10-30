##############################################################################
# Copyright (c) 2015 Huawei Technologies Co.,Ltd. and others
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################
from __future__ import absolute_import
import logging
import subprocess

import yardstick.ssh as ssh
from yardstick.benchmark.scenarios.availability.attacker.baseattacker import \
    BaseAttacker

LOG = logging.getLogger(__name__)


def _execute_shell_command(command, stdin=None):
    """execute shell script with error handling"""
    exitcode = 0
    output = []
    try:
        output = subprocess.check_output(command, stdin=stdin, shell=True)
    except Exception:
        exitcode = -1
        LOG.error("exec command '%s' error:\n ", command, exc_info=True)

    return exitcode, output


class BaremetalAttacker(BaseAttacker):
    __attacker_type__ = 'bare-metal-down'

    def setup(self):
        LOG.debug("config:%s context:%s", self._config, self._context)
        host = self._context.get(self._config['host'], None)

        self.connection = ssh.SSH.from_node(host, defaults={"user": "root"})
        self.connection.wait(timeout=600)
        LOG.debug("ssh host success!")

        jump_host_name = self._config.get("jump_host", None)
        self.jump_connection = None
        if jump_host_name is not None:
            jump_host = self._context.get(jump_host_name, None)

            LOG.debug("jump_host ip:%s user:%s", jump_host['ip'], jump_host['user'])
            self.jump_connection = ssh.SSH.from_node(
                jump_host,
                # why do we allow pwd for password?
                defaults={"user": "root", "password": jump_host.get("pwd")}
            )
            self.jump_connection.wait(timeout=600)
            LOG.debug("ssh jump host success!")

        self.host_ip = host['ip']

        self.ipmi_ip = host.get("ipmi_ip", None)
        self.ipmi_user = host.get("ipmi_user", "root")
        self.ipmi_pwd = host.get("ipmi_pwd", None)

        self.fault_cfg = BaseAttacker.attacker_cfgs.get('bare-metal-down')
        self.check_script = self.get_script_fullpath(
            self.fault_cfg['check_script'])
        self.inject_script = self.get_script_fullpath(self.fault_cfg['inject_script'])
        self.recovery_script = self.get_script_fullpath(
            self.fault_cfg['recovery_script'])

        if self.check():
            self.setup_done = True

    def check(self):
        with open(self.check_script, "r") as stdin_file:
            exit_status, stdout, stderr = self.connection.execute(
                "sudo /bin/sh -s {0} -W 10".format(self.host_ip),
                stdin=stdin_file)

        LOG.debug("check ret: %s out:%s err:%s",
                  exit_status, stdout, stderr)
        if not stdout or "running" not in stdout:
            LOG.info("the host (ipmi_ip:%s) is not running!", self.ipmi_ip)
            return False

        return True

    def inject_fault(self):
        LOG.info("Inject fault START")
        cmd = "sudo /bin/bash -s {0} {1} {2} {3}".format(
            self.ipmi_ip, self.ipmi_user, self.ipmi_pwd, "off")
        with open(self.inject_script, "r") as stdin_file:
            if self.jump_connection is not None:
                LOG.info("Power off node via IPMI")
                self.jump_connection.execute(cmd, stdin=stdin_file)
            else:
                _execute_shell_command(cmd, stdin=stdin_file)
        LOG.info("Inject fault END")

    def recover(self):
        LOG.info("Recover fault START")
        cmd = "sudo /bin/bash -s {0} {1} {2} {3}".format(
            self.ipmi_ip, self.ipmi_user, self.ipmi_pwd, "on")
        with open(self.recovery_script, "r") as stdin_file:
            if self.jump_connection is not None:
                self.jump_connection.execute(cmd, stdin=stdin_file)
            else:
                _execute_shell_command(cmd, stdin=stdin_file)
        LOG.info("Recover fault END")


def _test():  # pragma: no cover
    host = {
        "ipmi_ip": "10.20.0.5",
        "ipmi_user": "root",
        "ipmi_pwd": "123456",
        "ip": "10.20.0.5",
        "user": "root",
        "key_filename": "/root/.ssh/id_rsa"
    }
    context = {"node1": host}
    attacker_cfg = {
        'fault_type': 'bear-metal-down',
        'host': 'node1',
    }
    ins = BaremetalAttacker(attacker_cfg, context)
    ins.setup()
    ins.inject_fault()


if __name__ == '__main__':  # pragma: no cover
    _test()
