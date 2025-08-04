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
from dataclasses import dataclass

from gnmi.proto import gnmi_pb2 as pb # type: ignore
from gnmi.proto import gnmi_ext_pb2 as ext_pb # type: ignore
from gnmi.proto import gnmi_pb2_grpc # type: ignore

import typing as t

from gnmi import util

from gnmi.models import (
    CapabilityRequest, CapabilityResponse,
    DataType,
    Encoding,
    GetRequest, GetResponse,
    ModelData,
    Path,
    SetRequest, SetResponse,
    Status,
    SubscribeRequest, SubscribeResponse,
    Subscription, SubscriptionList,
    Target,
    Update,
    Value, ValueType
)

from gnmi.exceptions import GrpcError, GrpcDeadlineExceeded

BasicAuth = tuple[str, str]


@dataclass
class TLSConfig:
    ca_cert: bytes
    cert: bytes
    key: bytes
    get_server_cert: bool = False


class Session(object):
    r"""Represents a gNMI session

    Basic Usage::

        In [1]: from gnmi.session import Session
        In [2]: sess = Session(("veos3", 6030),
        ...:     metadata=[("username", "admin"), ("password", "")])

    """

    def __init__(self,
        target: str,
        metadata: t.Optional[dict] = None,
        insecure: bool = False,
        tls: t.Optional[TLSConfig] = None,
        grpc_options: t.Optional[dict] = None,
    ):
        self.target = Target(address=target)
        self._tls = tls

        if grpc_options is None:
            self._grpc_options = {}
        else:
            self._grpc_options = grpc_options

        self._insecure = insecure
        self.metadata = util.prepare_metadata(metadata)

        self._channel = self._new_channel()

        self._stub = gnmi_pb2_grpc.gNMIStub(self._channel) # type: ignore


    def _new_channel(self):
        # starget = f"{self.target.address.host}:{self.target.address.port}"

        if self._insecure:
            return grpc.insecure_channel(self.target.address)

        if not self._tls:
            raise ValueError("no certificates specified, use 'insecure' to bypass")

        if self._tls.get_server_cert:
            # TODO: investigate/test this, add cli option
            # creds = grpc.ssl_channel_credentials(
            #     ssl.get_server_certificate(self.target.address.host_port).encode()
            # )
            raise ValueError("unimplemented")
        else:
            root_cert = self._tls.ca_cert or None
            chain = self._tls.cert or None
            private_key = self._tls.key or None

            creds = grpc.ssl_channel_credentials(
                root_certificates=root_cert,
                private_key=private_key,
                certificate_chain=chain,
            )

        # tgt = ":".join([str(x) for x in self.target])
        return grpc.secure_channel(
            self.target.address, creds, options=list(self._grpc_options.items())
        )


    @staticmethod
    def _build_path(path: t.Union[str, Path, pb.Path]) -> pb.Path:
        if isinstance(path, pb.Path):
            return path
        if isinstance(path, Path):
            return path.encode()
        if isinstance(path, str) :
            return Path.from_str(path).encode()
        
        raise ValueError(f"failed to build path, invlaid type {type(path)}")


    @staticmethod
    def _build_update(update: t.Union[tuple[str, t.Any], tuple[str, t.Any, ValueType], Update, pb.Update]) -> pb.Update:
        if isinstance(update, pb.Update):
            return update
        if isinstance(update, Update):
            return update.encode()
        if isinstance(update, tuple):
            if len(update) == 2:
                path = Path.from_str(update[0])
                value = Value(update[1], ValueType.from_val(update[1]))
                upd = Update(path, value).encode()
            elif len(update) == 3:
                path = Path.from_str(update[2])
                upd = Update(path, Value(update[1], update[2])).encode()
            else:
                raise ValueError(f"failed to build update, invlaid tuple length: {len(update)}")
            return upd
        raise ValueError(f"failed to build updates, invlaid type {type(update)}")


    def capabilities(self) -> CapabilityResponse:
        r"""Discover capabilities of the target

        Usage::

            In [3]: resp = sess.capabilities()

            In [4]: resp.gnmi_version
            Out[4]: '0.10.0'

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

        _cr = CapabilityRequest()

        try:
            response = self._stub.Capabilities(_cr.encode(), metadata=self.metadata)
        except grpc.RpcError as rpcerr:
            status = Status.from_call(rpcerr)
            raise GrpcError(status)

        return CapabilityResponse.decode(response)


    def get(self, 
            paths: list[str],
            prefix: t.Optional[str] = None,
            encoding: t.Union[str, Encoding] = Encoding.JSON,
            data_type: t.Union[str, DataType] = DataType.ALL,
            models: t.Optional[list[ModelData]] = None,
            extensions: t.Optional[list[ext_pb.Extension]] = None,
        ) -> GetResponse:
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

        :param prefix: path prefix
        :type prefix: str
        :param paths: List of paths
        :type paths: list
        :param data_type:
        :type data_type: str
        :param encoding:
        :type encoding: str
        :param models:
        :type models: list[ModelData]
        :param extensions:
        :type extensions: list[ext_pb.Extension]
        :rtype: gnmi.messages.GetResponse_
        """

        _gr = GetRequest(
            prefix=prefix,
            paths=paths,
            type=data_type,
            encoding=encoding,
            models=models,
            extensions=extensions
        )

        try:
            resp = self._stub.Get(_gr.encode(), metadata=self.metadata)
        except grpc.RpcError as rpcerr:
            status = Status.from_call(rpcerr)
            raise GrpcError(status)

        return GetResponse.decode(resp)


    def set(self,
        prefix: t.Optional[str] = None,
        deletes: t.Optional[list[str]] = None,
        replacements: t.Optional[list[tuple[str, t.Any]]]= None,
        updates: t.Optional[list[tuple[str, t.Any]]] = None,
        union_replacements: t.Optional[list[tuple[str, t.Any]]] = None,
    ) -> SetResponse:
        r"""Set: set, update or delete value from specified path

        Usage::

            In [3]: updates = [("/system/config/hostname", "minemeow")]
            or...
            In [3]: updates = [("/system/config/hostname", "minemeow", "string_val")]
            In [4]: sess.set(updates=updates)

        :param prefix: subscription path prefix
        :type prefix: str
        :param updates: updates
        :type updates: list
        :param replacements: replacements
        :type replacements: list
        :param deletes: deletes
        :type deletes: list
        :param union_replacements: union replacements
        :type union_replacements: list
        :rtype: gnmi.messages.SetResponse_
        """

        _sr = SetRequest(
            prefix=prefix,
            deletes=deletes,
            replacements=replacements,
            updates=updates,
            union_replacements=union_replacements
        )

        try:
            return SetResponse.decode(self._stub.Set(_sr.encode(), metadata=self.metadata))
        except grpc.RpcError as rpcerr:
            status = Status.from_call(rpcerr)
            raise GrpcError(status)


    def subscribe(self, 
        subscriptions: list[t.Union[str, Path, Subscription]],
        prefix: t.Optional[str] = None,
        encoding: str = "json",
        mode: str = "stream",
        qos: int = 0,
        aggregate: bool = False,
        timeout: t.Optional[int] = None
    ) -> t.Iterable[SubscribeResponse]:
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

            In [60]: responses = sess.subscribe(paths)

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

        :param subscriptions: List of paths or Subscription objects
        :type subscriptions: list
        :param prefix:
        :type: t.Optional[str]
        :param encoding: 
        :type: str
        :param mode:
        :type: str
        :param qos:
        :type: int
        :param aggregate:
        :type: bool
        :param timeout: 
        :type: int
        :rtype: gnmi.messages.SubscribeResponse_
        """

        def _sr():
            yield SubscribeRequest(
                subscribe=SubscriptionList(
                    subscriptions=subscriptions,
                    prefix=prefix,
                    mode=mode,
                    allow_aggregation=aggregate,
                    encoding=encoding,
                    qos=qos
            )).encode()

        try:
            for r in self._stub.Subscribe(_sr(), timeout=timeout, metadata=self.metadata):
                yield SubscribeResponse.decode(r)
        except grpc.RpcError as rpcerr:
            status = Status.from_call(rpcerr)

            if (
                status.code.name == "DEADLINE_EXCEEDED"
                or status.details == "context deadline exceeded"
            ):
                raise GrpcDeadlineExceeded(status)
            else:
                raise GrpcError(status)