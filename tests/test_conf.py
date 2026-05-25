# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.config import Config, load_config_file

def test_conf_load():
    _ = load_config_file("tests/config.yaml")
    # pprint(cnf)