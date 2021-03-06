##############################################################################
# Copyright (c) 2017 Huawei Technologies Co.,Ltd and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

from __future__ import print_function
from __future__ import absolute_import

import logging

from yardstick.benchmark.scenarios import base
import yardstick.common.openstack_utils as op_utils

LOG = logging.getLogger(__name__)


class CreateRouter(base.Scenario):
    """Create an OpenStack router"""

    __scenario_type__ = "CreateRouter"

    def __init__(self, scenario_cfg, context_cfg):
        self.scenario_cfg = scenario_cfg
        self.context_cfg = context_cfg
        self.options = self.scenario_cfg['options']

        self.openstack = self.options.get("openstack_paras", None)

        self.neutron_client = op_utils.get_neutron_client()

        self.setup_done = False

    def setup(self):
        """scenario setup"""

        self.setup_done = True

    def run(self, result):
        """execute the test"""

        if not self.setup_done:
            self.setup()

        openstack_paras = {'router': self.openstack}
        router_id = op_utils.create_neutron_router(self.neutron_client,
                                                   openstack_paras)
        if router_id:
            result.update({"network_create": 1})
            LOG.info("Create router successful!")
        else:
            result.update({"network_create": 0})
            LOG.error("Create router failed!")

        check_result = router_id

        try:
            keys = self.scenario_cfg.get('output', '').split()
        except KeyError:
            pass
        else:
            values = [check_result]
            return self._push_to_outputs(keys, values)
