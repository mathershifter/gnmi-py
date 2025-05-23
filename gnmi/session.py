# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
"""
gnmi.session
~~~~~~~~~~~~~~~~

Implementation if gnmi.session API

"""
# import enum

import grpc

from gnmi.proto import gnmi_pb2 as pb # type: ignore
from gnmi.proto import gnmi_pb2_grpc # type: ignore

import typing as t
import ssl

from collections import defaultdict

from gnmi import util
from gnmi.messages import CapabilityRequest_, CapabilityResponse_, GetResponse_, Path_, Status_
from gnmi.messages import Update_
from gnmi.messages import SubscribeResponse_, SetResponse_
from gnmi.structures import CertificateStore, Options
from gnmi.structures import GetOptions, SubscribeOptions
from gnmi.exceptions import GrpcError, GrpcDeadlineExceeded
from gnmi.target import Target

SUBSCRIPTION_LIST_MODE_MAP: t.Final[dict[str, pb.SubscriptionList.Mode]] = defaultdict(
    lambda: pb.SubscriptionList.STREAM,
    {
        "stream": pb.SubscriptionList.STREAM,
        "once": pb.SubscriptionList.ONCE,
        "poll": pb.SubscriptionList.POLL,
    }
)

GET_DATA_TYPE_MAP: t.Final[dict[str, pb.GetRequest.DataType]] = defaultdict(
    lambda: pb.GetRequest.ALL,
    {
        "all": pb.GetRequest.ALL,
        "config": pb.GetRequest.CONFIG,
        "state": pb.GetRequest.STATE,
        "operational": pb.GetRequest.OPERATIONAL,
    }
)

class Session(object):
    r"""Represents a gNMI session

    Basic Usage::

        In [1]: from gnmi.session import Session
        In [2]: sess = Session(("veos3", 6030),
        ...:     metadata=[("username", "admin"), ("password", "")])

    """

    def __init__(
        self,
        target: Target,
        metadata: dict = {},
        insecure: bool = False,
        certificates: CertificateStore = {},
        grpc_options: dict = {},
    ):
        self._certificates = certificates
        self._grpc_options = grpc_options
        self._insecure = insecure
        self.target = target
        self.metadata = util.prepare_metadata(metadata)

        self._channel = self._new_channel()

        self._stub = gnmi_pb2_grpc.gNMIStub(self._channel) # type: ignore

    # @property
    # def hostaddr(self):
    #     return "%s:%d" % self.target

    def _new_channel(self):
        if self._insecure:
            return grpc.insecure_channel(str(self.target))

        elif not self._certificates.get("root_certificates"):
            creds = grpc.ssl_channel_credentials(
                ssl.get_server_certificate(self.target.addr).encode()
            )
        else:
            root_cert = self._certificates.get("root_certificates") or None
            chain = self._certificates.get("certificate_chain") or None
            private_key = self._certificates.get("private_key") or None

            creds = grpc.ssl_channel_credentials(
                root_certificates=root_cert,
                private_key=private_key,
                certificate_chain=chain,
            )

        tgt = ":".join([str(x) for x in self.target.addr])
        return grpc.secure_channel(
            tgt, creds, options=list(self._grpc_options.items())
        )

    def _build_path(self, path: t.Union[str,Path_]) -> pb.Path:
        if isinstance(path, Path_):
            return path.pb()
        return Path_.from_string(path).pb()
    
    def _build_update(self, update: t.Union[tuple[str, t.Any],Update_]) -> pb.Update:
        if isinstance(update, Update_):
            return update.pb()
        return Update_.from_keyval(update).pb()

    def _parse_path(
        self, path: t.Optional[t.Union[Path_, pb.Path, str, list, tuple]]
    ) -> pb.Path:
        if path is None:
            path = ""
        elif isinstance(path, (list, tuple)):
            path = "/".join(list(path))

        if isinstance(path, str):
            return Path_.from_string(path).pb()
        elif isinstance(path, Path_):
            return path.pb()
        elif isinstance(path, pb.Path):
            return path
        else:
            raise ValueError("Failed to parse path: %s" % str(path))

    def capabilities(self) -> CapabilityResponse_:
        r"""Discover capabilities of the target

        Usage::

            In [3]: resp = sess.capabilities()

            In [4]: resp.gnmi_version
            Out[4]: '0.7.0'

            In [5]: resp.supported_encodings
            Out[5]: [0, 4, 3]

            In [7]: for model in resp.supported_models:
                ...:     print(model["name"], model["version"])
                ...:     # print(model["organization])
            openconfig-system-logging 0.3.1
            openconfig-messages 0.0.1
            openconfig-platform-types 1.0.0
            arista-system-augments
            openconfig-if-types 0.2.1
            openconfig-acl 1.0.2
            arista-intf-augments
            openconfig-pf-srte 0.1.1
            openconfig-bgp 6.0.0
            ...

        :rtype: gnmi.messages.CapabilityResponse_
        """

        _cr = CapabilityRequest_()

        try:
            response = self._stub.Capabilities(_cr.pb(), metadata=self.metadata)
        except grpc.RpcError as rpcerr:
            status = Status_.from_call(rpcerr)
            raise GrpcError(status)

        return CapabilityResponse_(response)

    def get(self, paths: list, options: GetOptions = {}) -> GetResponse_:
        r"""Get snapshot of state from the target

        Usage::

            In [8]: paths = [
            ...:     "/system/config/hostname",
            ...:     "/system/memory/state/physical",
            ...:     "/system/memory/state/reserved"
            ...: ]
            In [9]: options={"prefix": "/", "encoding": "json"}

            In [10]: resp = sess.get(paths, options)

            In [11]: for notif in resp:
                ...:     for update in notif:
                ...:         print(update.path, update.val)
                ...:
            /system/config/hostname veos3-782f
            /system/memory/state/physical 2062848000
            /system/memory/state/reserved 2007666688

        :param paths: List of paths
        :type paths: list
        :param options:
        :type options: gnmi.structures.GetOptions

        :rtype: gnmi.messages.GetResponse_
        """

        response: pb.GetResponse

        prefix = self._parse_path(options.get("prefix"))
        encoding = util.get_gnmi_constant(options.get("encoding") or "json")
        
        type_ = GET_DATA_TYPE_MAP.get(options.get("type", "all"))

        paths = [self._parse_path(path) for path in paths]

        _gr = pb.GetRequest(path=paths, prefix=prefix, encoding=encoding, type=type_)

        try:
            response = self._stub.Get(_gr, metadata=self.metadata)
        except grpc.RpcError as rpcerr:
            status = Status_.from_call(rpcerr)
            raise GrpcError(status)

        return GetResponse_(response)

    def set(
        self,
        deletes: list[str] = [],
        replacements: list[tuple[str, t.Any]] = [],
        updates: list[tuple[str, t.Any]] = [],
        options: Options = {},
    ) -> SetResponse_:
        r"""Set set, update or delete value from specified path

        Usage::

            In [3]: updates = [("/system/config/hostname", "minemeow")]
            In [4]: sess.set(updates=updates)

        :param updates: List of updates
        :type updates: list
        :param replacements: List of replacements
        :type replacements: list
        :param deletes: List of deletes
        :type deletes: list
        :param options:
        :type options: gnmi.structures.Options
        :rtype: gnmi.messages.SetResponse_
        """
        response: SetResponse_

        prefix = self._parse_path(options.get("prefix"))
        delete: list[pb.Path] = []
        replace: list[pb.Update] = []
        update: list[pb.Update] = []

        for d in deletes:
            delete.append(self._build_path(d))
        for r in replacements:
            replace.append(self._build_update(r))
        for u in updates:
            update.append(self._build_update(u))

        _sr = pb.SetRequest(prefix=prefix, delete=delete, update=update, replace=replace)

        try:
            response = SetResponse_(self._stub.Set(_sr, metadata=self.metadata))
        except grpc.RpcError as rpcerr:
            status = Status_.from_call(rpcerr)
            raise GrpcError(status)

        return response

    def subscribe(
        self, paths: list, options: SubscribeOptions = {}
    ) -> t.Iterable[SubscribeResponse_]:
        r"""Subscribe to state updates from the target

        Usage::

            In [57]: from gnmi.exceptions import GrpcDeadlineExceeded
            In [58]: paths = [
            ...:     "/interface[name=Management1]",
            ...:     "/interface[name=Ethernet1]"
            ...: ]

            In [59]: options = {
            ...:     "prefix": "/interfaces",
            ...:     "mode": "stream",
            ...:     "submode": "on-change",
            ...:     "timeout": 5
            ...:  }

            In [60]: responses = sess.subscribe(paths, options)

            In [61]: try:
                ...:     for resp in responses:
                ...:         prefix = resp.update.prefix
                ...:         for update in resp.update:
                ...:             path = prefix + update.path
                ...:             print(str(path), update.value)
                ...: except GrpcDeadlineExceeded:
                ...:     pass
                ...:
            /interfaces/interface[name=Management1]/config/description
            /interfaces/interface[name=Management1]/config/enabled True
            /interfaces/interface[name=Management1]/config/load-interval 300
            /interfaces/interface[name=Management1]/config/loopback-mode False
            <output-omitted>
            /interfaces/interface[name=Ethernet1]/config/description
            /interfaces/interface[name=Ethernet1]/config/enabled True
            /interfaces/interface[name=Ethernet1]/config/load-interval 300
            /interfaces/interface[name=Ethernet1]/config/loopback-mode False
            /interfaces/interface[name=Ethernet1]/config/mtu 0
            /interfaces/interface[name=Ethernet1]/config/name Ethernet1
            <output-omitted>

        :param paths: List of paths
        :type paths: list
        :param options:
        :type options: gnmi.structures.GetOptions
        :rtype: gnmi.messages.SubscribeResponse_
        """

        aggregate = bool(options.get("aggregate", False))
        encoding = util.get_gnmi_constant(options.get("encoding") or "json")
        heartbeat = options.get("heartbeat") or 0
        interval = options.get("interval") or 0
        
        mode = SUBSCRIPTION_LIST_MODE_MAP.get(options.get("mode", "stream"))
        
        prefix = self._parse_path(options.get("prefix"))
        qos = pb.QOSMarking(marking=options.get("qos", 0))
        submode = util.get_gnmi_constant(options.get("submode") or "on-change")
        suppress = bool(options.get("suppress"))
        timeout = options.get("timeout")

        subs = []
        for path in paths:
            path = self._parse_path(path)
            sub = pb.Subscription(
                path=path,
                mode=submode,
                suppress_redundant=suppress,
                sample_interval=interval,
                heartbeat_interval=heartbeat,
            )
            subs.append(sub)

        def _sr():
            sub_list = pb.SubscriptionList(
                prefix=prefix,
                mode=mode,
                allow_aggregation=aggregate,
                encoding=encoding,
                subscription=subs,
                qos=qos,
            )
            yield pb.SubscribeRequest(subscribe=sub_list)

        try:
            for r in self._stub.Subscribe(_sr(), timeout, metadata=self.metadata):
                yield SubscribeResponse_(r)
        except grpc.RpcError as rpcerr:
            status = Status_.from_call(rpcerr)

            # server sometimes sends:
            #    gnmi.exceptions.GrpcError: StatusCode.UNKNOWN: context deadline exceeded
            if (
                status.code.name == "DEADLINE_EXCEEDED"
                or status.details == "context deadline exceeded"
            ):
                raise GrpcDeadlineExceeded(status)
            else:
                raise GrpcError(status)
