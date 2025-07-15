# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import json

from gnmi.proto import gnmi_pb2 as pb
from gnmi.models.encoding import Encoding
from gnmi.models.model_data import ModelData
from gnmi.models.capabilities import CapabilityResponse
from gnmi.util import get_gnmi_constant

# gnmic -a localhost:6030 -u admin --insecure capabilities --format json | jq '.["supported-models"] | map(select(.name | startswith("arista") | not))'
supported_models = b'''[
  {
    "name": "openconfig-mpls-types",
    "organization": "OpenConfig working group",
    "version": "3.5.0"
  },
  {
    "name": "openconfig-mpls",
    "organization": "OpenConfig working group",
    "version": "3.6.0"
  },
  {
    "name": "openconfig-spanning-tree",
    "organization": "OpenConfig working group",
    "version": "0.3.1"
  },
  {
    "name": "openconfig-procmon",
    "organization": "OpenConfig working group",
    "version": "0.4.0"
  },
  {
    "name": "openconfig-platform-cpu",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "openconfig-macsec-types",
    "organization": "OpenConfig working group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-ospf-types",
    "organization": "OpenConfig working group",
    "version": "0.1.3"
  },
  {
    "name": "gnsi-authz",
    "organization": "Google LLC"
  },
  {
    "name": "openconfig-if-sdn-ext",
    "organization": "OpenConfig working group",
    "version": "0.2.0"
  },
  {
    "name": "openconfig-transport-types",
    "organization": "OpenConfig working group",
    "version": "1.1.0"
  },
  {
    "name": "openconfig-terminal-device",
    "organization": "OpenConfig working group",
    "version": "1.9.2"
  },
  {
    "name": "openconfig-platform-fabric",
    "organization": "OpenConfig working group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-network-instance-l3",
    "organization": "OpenConfig working group",
    "version": "2.0.0"
  },
  {
    "name": "openconfig-aaa-types",
    "organization": "OpenConfig working group",
    "version": "0.4.1"
  },
  {
    "name": "openconfig-aft-summary",
    "organization": "OpenConfig working group",
    "version": "0.2.0"
  },
  {
    "name": "gnsi-credentialz",
    "organization": "Google LLC"
  },
  {
    "name": "openconfig-openflow",
    "organization": "OpenConfig working group",
    "version": "0.1.2"
  },
  {
    "name": "openconfig-mpls-ldp",
    "organization": "OpenConfig working group",
    "version": "3.2.1"
  },
  {
    "name": "openconfig-platform-controller-card",
    "organization": "OpenConfig working group",
    "version": "0.2.0"
  },
  {
    "name": "openconfig-system",
    "organization": "OpenConfig working group",
    "version": "2.3.0"
  },
  {
    "name": "gnsi-certz",
    "organization": "Google LLC"
  },
  {
    "name": "openconfig-evpn-types",
    "organization": "OpenConfig working group",
    "version": "0.2.0"
  },
  {
    "name": "openconfig-bgp-types",
    "organization": "OpenConfig working group",
    "version": "6.1.0"
  },
  {
    "name": "openconfig-aft-types",
    "organization": "OpenConfig Working Group",
    "version": "1.2.0"
  },
  {
    "name": "openconfig-if-poe",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "openconfig-gnsi",
    "organization": "OpenConfig Working Group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-ospfv2",
    "organization": "OpenConfig working group",
    "version": "0.5.2"
  },
  {
    "name": "openconfig-lldp-types",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "ietf-inet-types",
    "organization": "IETF NETMOD (NETCONF Data Modeling Language) Working Group"
  },
  {
    "name": "openconfig-platform-software",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "openconfig-lacp",
    "organization": "OpenConfig working group",
    "version": "2.1.0"
  },
  {
    "name": "openconfig-macsec",
    "organization": "OpenConfig working group",
    "version": "1.1.1"
  },
  {
    "name": "openconfig-defined-sets",
    "organization": "OpenConfig working group",
    "version": "1.0.0"
  },
  {
    "name": "openconfig-if-aggregate",
    "organization": "OpenConfig working group",
    "version": "2.4.4"
  },
  {
    "name": "openconfig-relay-agent",
    "organization": "OpenConfig working group",
    "version": "0.1.2"
  },
  {
    "name": "openconfig-local-routing",
    "organization": "OpenConfig working group",
    "version": "2.0.1"
  },
  {
    "name": "openconfig-segment-routing",
    "organization": "OpenConfig working group",
    "version": "0.4.1"
  },
  {
    "name": "ietf-netconf",
    "organization": "IETF NETCONF (Network Configuration) Working Group"
  },
  {
    "name": "openconfig-if-ip",
    "organization": "OpenConfig working group",
    "version": "3.6.0"
  },
  {
    "name": "openconfig-programming-errors",
    "organization": "OpenConfig working group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-hercules-qos",
    "organization": "OpenConfig Hercules Working Group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-routing-policy",
    "organization": "OpenConfig working group",
    "version": "3.4.2"
  },
  {
    "name": "openconfig-ospf-policy",
    "organization": "OpenConfig working group",
    "version": "0.1.3"
  },
  {
    "name": "openconfig-messages",
    "organization": "OpenConfig working group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-icmpv6-types",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "openconfig-openflow-types",
    "organization": "OpenConfig working group",
    "version": "0.2.0"
  },
  {
    "name": "openconfig-p4rt",
    "organization": "OpenConfig Working Group",
    "version": "1.0.0"
  },
  {
    "name": "openconfig-platform-fan",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "openconfig-igmp",
    "organization": "OpenConfig working group",
    "version": "0.3.1"
  },
  {
    "name": "openconfig-icmpv4-types",
    "organization": "OpenConfig working group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-platform-types",
    "organization": "OpenConfig working group",
    "version": "1.9.0"
  },
  {
    "name": "openconfig-yang-types",
    "organization": "OpenConfig working group",
    "version": "1.0.0"
  },
  {
    "name": "openconfig-license",
    "organization": "OpenConfig working group",
    "version": "0.2.0"
  },
  {
    "name": "openconfig-segment-routing-types",
    "organization": "OpenConfig working group",
    "version": "0.2.0"
  },
  {
    "name": "ietf-yang-metadata",
    "organization": "IETF NETMOD (NETCONF Data Modeling Language) Working Group"
  },
  {
    "name": "ietf-interfaces",
    "organization": "IETF NETMOD (Network Modeling) Working Group"
  },
  {
    "name": "openconfig-hercules-platform",
    "organization": "OpenConfig Hercules Working Group",
    "version": "0.2.0"
  },
  {
    "name": "openconfig-metadata",
    "organization": "OpenConfig working group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-system-grpc",
    "organization": "OpenConfig working group",
    "version": "1.1.0"
  },
  {
    "name": "openconfig-igmp-types",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "openconfig-system-controlplane",
    "organization": "OpenConfig working group",
    "version": "0.2.0"
  },
  {
    "name": "openconfig-lldp",
    "organization": "OpenConfig working group",
    "version": "0.2.1"
  },
  {
    "name": "openconfig-inet-types",
    "organization": "OpenConfig working group",
    "version": "0.7.0"
  },
  {
    "name": "openconfig-alarm-types",
    "organization": "OpenConfig working group",
    "version": "0.2.1"
  },
  {
    "name": "openconfig-extensions",
    "organization": "OpenConfig working group",
    "version": "0.6.0"
  },
  {
    "name": "openconfig-if-tunnel",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "openconfig-rib-bgp-types",
    "organization": "OpenConfig working group",
    "version": "0.5.0"
  },
  {
    "name": "openconfig-isis-types",
    "organization": "OpenConfig working group",
    "version": "0.6.0"
  },
  {
    "name": "openconfig-srte-policy",
    "organization": "OpenConfig working group",
    "version": "0.2.3"
  },
  {
    "name": "openconfig-interfaces",
    "organization": "OpenConfig working group",
    "version": "3.7.2"
  },
  {
    "name": "openconfig-qos",
    "organization": "OpenConfig working group",
    "version": "0.11.2"
  },
  {
    "name": "openconfig-system-logging",
    "organization": "OpenConfig working group",
    "version": "0.7.0"
  },
  {
    "name": "iana-if-type",
    "organization": "IANA"
  },
  {
    "name": "openconfig-platform",
    "organization": "OpenConfig working group",
    "version": "0.30.0"
  },
  {
    "name": "openconfig-isis-flex-algo",
    "organization": "Arista Networks <https://arista.com/>",
    "version": "0.6.1"
  },
  {
    "name": "openconfig-telemetry",
    "organization": "OpenConfig working group",
    "version": "0.5.1"
  },
  {
    "name": "openconfig-types",
    "organization": "OpenConfig working group",
    "version": "1.0.0"
  },
  {
    "name": "openconfig-gnsi-acctz",
    "organization": "OpenConfig Working Group",
    "version": "0.3.0"
  },
  {
    "name": "openconfig-vlan-types",
    "organization": "OpenConfig working group",
    "version": "3.2.0"
  },
  {
    "name": "openconfig-isis-lsdb-types",
    "organization": "OpenConfig working group",
    "version": "0.4.2"
  },
  {
    "name": "openconfig-system-terminal",
    "organization": "OpenConfig working group",
    "version": "0.3.1"
  },
  {
    "name": "openconfig-rib-bgp-ext",
    "organization": "OpenConfig working group",
    "version": "0.6.0"
  },
  {
    "name": "openconfig-rib-bgp",
    "organization": "OpenConfig working group",
    "version": "0.9.0"
  },
  {
    "name": "openconfig-network-instance-types",
    "organization": "OpenConfig working group",
    "version": "0.9.3"
  },
  {
    "name": "openconfig-system-utilization",
    "organization": "OpenConfig working group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-telemetry-types",
    "organization": "OpenConfig working group",
    "version": "0.4.2"
  },
  {
    "name": "openconfig-isis",
    "organization": "OpenConfig working group",
    "version": "1.7.0"
  },
  {
    "name": "openconfig-acl",
    "organization": "OpenConfig working group",
    "version": "1.3.3"
  },
  {
    "name": "openconfig-qos-types",
    "organization": "OpenConfig working group",
    "version": "0.2.1"
  },
  {
    "name": "openconfig-platform-pipeline-counters",
    "organization": "OpenConfig working group",
    "version": "0.5.1"
  },
  {
    "name": "openconfig-sampling",
    "organization": "OpenConfig working group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-aaa",
    "organization": "OpenConfig working group",
    "version": "1.0.0"
  },
  {
    "name": "openconfig-platform-healthz",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "openconfig-packet-match-types",
    "organization": "OpenConfig working group",
    "version": "1.3.3"
  },
  {
    "name": "openconfig-platform-linecard",
    "organization": "OpenConfig working group",
    "version": "1.2.0"
  },
  {
    "name": "openconfig-network-instance",
    "organization": "OpenConfig working group",
    "version": "4.4.1"
  },
  {
    "name": "openconfig-if-ethernet",
    "organization": "OpenConfig working group",
    "version": "2.14.0"
  },
  {
    "name": "openconfig-pf-srte",
    "organization": "OpenConfig working group",
    "version": "0.2.0"
  },
  {
    "name": "openconfig-pim",
    "organization": "OpenConfig working group",
    "version": "0.4.4"
  },
  {
    "name": "openconfig-pcep",
    "organization": "OpenConfig working group",
    "version": "0.1.1"
  },
  {
    "name": "openconfig-aft-network-instance",
    "organization": "OpenConfig working group",
    "version": "0.3.1"
  },
  {
    "name": "ietf-yang-types",
    "organization": "IETF NETMOD (NETCONF Data Modeling Language) Working Group"
  },
  {
    "name": "openconfig-mpls-sr",
    "organization": "OpenConfig working group",
    "version": "3.0.1"
  },
  {
    "name": "openconfig-policy-types",
    "organization": "OpenConfig working group",
    "version": "3.3.0"
  },
  {
    "name": "ietf-netconf-monitoring",
    "organization": "IETF NETCONF (Network Configuration) Working Group"
  },
  {
    "name": "openconfig-isis-policy",
    "organization": "OpenConfig working group",
    "version": "0.8.0"
  },
  {
    "name": "openconfig-evpn",
    "organization": "OpenConfig working group",
    "version": "0.11.0"
  },
  {
    "name": "vlan-translation",
    "organization": "Arista Networks"
  },
  {
    "name": "openconfig-platform-transceiver",
    "organization": "OpenConfig working group",
    "version": "0.16.0"
  },
  {
    "name": "openconfig-packet-match",
    "organization": "OpenConfig working group",
    "version": "2.1.0"
  },
  {
    "name": "openconfig-platform-psu",
    "organization": "OpenConfig working group",
    "version": "0.2.1"
  },
  {
    "name": "openconfig-bfd",
    "organization": "OpenConfig working group",
    "version": "0.3.0"
  },
  {
    "name": "openconfig-pim-types",
    "organization": "OpenConfig working group",
    "version": "0.1.2"
  },
  {
    "name": "openconfig-keychain",
    "organization": "OpenConfig working group",
    "version": "0.5.0"
  },
  {
    "name": "openconfig-platform-port",
    "organization": "OpenConfig working group",
    "version": "1.0.1"
  },
  {
    "name": "openconfig-bgp",
    "organization": "OpenConfig working group",
    "version": "9.8.0"
  },
  {
    "name": "openconfig-vlan",
    "organization": "OpenConfig working group",
    "version": "3.2.2"
  },
  {
    "name": "openconfig-keychain-types",
    "organization": "OpenConfig working group",
    "version": "0.3.1"
  },
  {
    "name": "openconfig-bgp-policy",
    "organization": "OpenConfig working group",
    "version": "8.1.0"
  },
  {
    "name": "openconfig-hercules-interfaces",
    "organization": "OpenConfig Hercules Working Group",
    "version": "0.2.0"
  },
  {
    "name": "openconfig-alarms",
    "organization": "OpenConfig working group",
    "version": "0.3.2"
  },
  {
    "name": "openconfig-platform-integrated-circuit",
    "organization": "OpenConfig working group",
    "version": "0.3.1"
  },
  {
    "name": "openconfig-spanning-tree-types",
    "organization": "OpenConfig working group",
    "version": "0.4.1"
  },
  {
    "name": "openconfig-mpls-rsvp",
    "organization": "OpenConfig working group",
    "version": "4.0.1"
  },
  {
    "name": "openconfig-policy-forwarding",
    "organization": "OpenConfig working group",
    "version": "0.6.1"
  },
  {
    "name": "openconfig-aft",
    "organization": "OpenConfig working group",
    "version": "2.8.0"
  },
  {
    "name": "openconfig-flexalgo",
    "organization": "OpenConfig working group",
    "version": "0.1.0"
  },
  {
    "name": "openconfig-sampling-sflow",
    "organization": "OpenConfig working group",
    "version": "1.0.0"
  }
]
'''

supported_encodings = b'''[
    "JSON",
    "JSON_IETF",
    "ASCII"
]'''

def test_capabilities_response():
    models = json.loads(supported_models)
    encodings = json.loads(supported_encodings)
    tests = [
        (
            CapabilityResponse(
                gnmi_version='0.7.0',
                supported_models=[ModelData(
                    name=m['name'],
                    organization=m['organization'],
                    version=m.get('version'),
                ) for m in models],
                supported_encodings=[Encoding[e] for e in encodings]
            ),
            pb.CapabilityResponse(
                gNMI_version='0.7.0',
                supported_models=[pb.ModelData(
                    name=m['name'],
                    organization=m['organization'],
                    version=m.get('version'),
                ) for m in models],
                supported_encodings=[get_gnmi_constant(e) for e in encodings]
            ),
        )
    ]

    for test in tests:
        have, want = test
        assert have.encode() == want