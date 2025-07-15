# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi import config as c

yaml_conf = b'''
gnmi_version: 0.9.0
target: localhost:50051
metadata:
    username: admin
    password: ""

get:
    prefix: /interfaces
    paths:
        - /interface[name=Ethernet3/1]/state/counters
    type: all
    encoding: json
'''

def test_conf_load():
    _ = c.load(c.yaml_loader, yaml_conf)
    # pprint(cnf)