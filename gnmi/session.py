# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
"""
gnmi.session
~~~~~~~~~~~~~~~~

Implementation if gnmi.session API

"""
import ssl
import grpc
from dataclasses import dataclass

from gnmi.proto import gnmi_ext_pb2 as ext_pb # type: ignore
from gnmi.proto import gnmi_pb2_grpc # type: ignore

from typing import Sequence, Iterable

from gnmi import util

from gnmi.certs import get_server_certificate

from gnmi.models.capabilities import CapabilityRequest, CapabilityResponse
from gnmi.models.get import DataType, GetRequest, GetResponse
from gnmi.models.encoding import Encoding
from gnmi.models.model_data import ModelData
from gnmi.models.path import PathLike, Path, Paths
from gnmi.models.set import SetRequest, SetResponse
from gnmi.models.status import Status
from gnmi.models.subscribe import SubscribeRequest, SubscribeResponse
from gnmi.models.subscription import Subscription
from gnmi.models.subscription_list import SubscriptionList
from gnmi.models.target import Target
from gnmi.models.update import UpdateList
from gnmi.exceptions import GrpcError, GrpcDeadlineExceeded

BasicAuth = tuple[str, str]


@dataclass
class TLSConfig:
    ca_cert: bytes
    client_cert: bytes
    client_key: bytes
    get_server_cert: bool = False

    @property
    def context(self):
        return ssl.create_default_context(cadata=self.ca_cert)


class Session(object):
    r"""Represents a gNMI session

    Basic Usage::

        In [1]: from gnmi.session import Session
        In [2]: sess = Session(("veos3", 6030),
        ...:     metadata=[("username", "admin"), ("password", "")])

    """

    def __init__(self,
        target: str,
        metadata: dict | None = None,
        insecure: bool = False,
        tls: TLSConfig | None = None,
        grpc_options: dict | None = None,
    ):
        self.target = Target(target)
        self._tls = tls

        if grpc_options is None:
            self._grpc_options = {}
        else:
            self._grpc_options = grpc_options

        self._insecure = insecure
        self.metadata = util.prepare_metadata(metadata)

        self._channel = self._new_channel()

        self._stub = gnmi_pb2_grpc.gNMIStub(self._channel) # type: ignore

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._channel.close()

    def _new_channel(self):
        # starget = f"{self.target.address.host}:{self.target.address.port}"

        if self._insecure:
            return grpc.insecure_channel(self.target.address)

        if not self._tls:
            raise ValueError("no certificates specified, use 'insecure' to bypass")

        
        
        root_cert = self._tls.ca_cert or None
        
        chain = self._tls.client_cert or None
        private_key = self._tls.client_key or None

        if self._tls.get_server_cert:
            _ = get_server_certificate(self.target, self._tls.context)

        creds = grpc.ssl_channel_credentials(
            root_certificates=root_cert,
            private_key=private_key,
            certificate_chain=chain,
        )

        return grpc.secure_channel(
            self.target.address, creds, options=list(self._grpc_options.items())
        )


    def capabilities(self) -> CapabilityResponse:
        r"""Discover capabilities of the target

        Usage::

            In [3]: resp = sess.capabilities()

            In [4]: resp.gnmi_version
            Out[4]: '0.10.0'

            In [5]: resp.supported_encodings
            Out[5]: [<Encoding.JSON: 0>, <Encoding.PROTO: 2>, <Encoding.JSON_IETF: 4>]

            In [7]: for model in resp.supported_models:
                ...:     print(model.name, model.version)
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

        :rtype: gnmi.models.capabilities.CapabilityResponse
        """

        _cr = CapabilityRequest()

        try:
            response = self._stub.Capabilities(_cr.encode(), metadata=self.metadata)
        except grpc.RpcError as rpcerr:
            status = Status.from_call(rpcerr)
            raise GrpcError(status)

        return CapabilityResponse.decode(response)


    def get(self, 
            paths: Sequence[PathLike],
            prefix: PathLike | None = None,
            encoding: Encoding | str | int = Encoding.JSON,
            data_type: DataType | str | int = DataType.ALL,
            models: list[ModelData] = [],
            extensions: list[ext_pb.Extension] = [],
        ) -> GetResponse:
        r"""Get snapshot of state from the target

        Usage::

            In [8]: paths = [
            ...:     "/system/config/hostname",
            ...:     "/system/memory/state/physical",
            ...:     "/system/memory/state/reserved"
            ...: ]

            In [9]: resp = sess.get(paths, prefix="/", encoding="json")

            In [10]: for notif in resp.notifications:
                ...:     for update in notif.updates:
                ...:         print(update.path, update.value)
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
        :rtype: gnmi.models.get.GetResponse
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
        prefix: PathLike | None = None,
        deletes: Sequence[PathLike] = [],
        replacements: UpdateList = [],
        updates: UpdateList = [],
        union_replacements: UpdateList = [],
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
        :rtype: gnmi.models.set.SetResponse
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
        subscriptions: Sequence[str | Path | Subscription],
        prefix: PathLike | None = None,
        encoding: Encoding | str | int = "json",
        mode: str = "stream",
        qos: int = 0,
        aggregate: bool = False,
        timeout: int | None = None
    ) -> Iterable[SubscribeResponse]:
        r"""Subscribe to state updates from the target

        Usage::

            In [57]: from gnmi.exceptions import GrpcDeadlineExceeded
            In [58]: paths = [
            ...:     "/interface[name=Management1]",
            ...:     "/interface[name=Ethernet1]"
            ...: ]

            In [59]: responses = sess.subscribe(
            ...:     paths,
            ...:     prefix="/interfaces",
            ...:     mode="stream",
            ...:     timeout=5,
            ...: )

            In [60]: try:
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
        :rtype: gnmi.models.subscribe.SubscribeResponse
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