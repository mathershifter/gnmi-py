from typing import Sequence, AsyncIterable

from grpc.aio import Channel, insecure_channel, secure_channel
from grpc import ssl_channel_credentials

from gnmi.util import prepare_metadata
from gnmi.proto import gnmi_ext_pb2 as ext_pb
from gnmi.proto import gnmi_pb2_grpc
from gnmi.tls import get_server_certificate, TLSConfig

from gnmi.models.capabilities import CapabilityRequest, CapabilityResponse
from gnmi.models.get import DataType, GetRequest, GetResponse
from gnmi.models.encoding import Encoding
from gnmi.models.model_data import ModelData
from gnmi.models.path import PathLike, Path
from gnmi.models.set import SetRequest, SetResponse
from gnmi.models.subscribe import SubscribeRequest, SubscribeResponse
from gnmi.models.subscription import Subscription
from gnmi.models.subscription_list import SubscriptionList
from gnmi.models.target import TargetLike, target_factory
from gnmi.models.update import UpdateList

BasicAuth = tuple[str, str]


class AsyncSession:
    def __init__(
        self,
        target: TargetLike,
        metadata: dict | None = None,
        insecure: bool = False,
        tls: TLSConfig | None = None,
        grpc_options: dict | None = None,
    ):
        self._target = target_factory(target)
        self._metadata = prepare_metadata(metadata or {})
        self._insecure = insecure
        self._tls = tls
        self._grpc_options = (grpc_options or {}).items()

        self._channel = self._new_channel()

        self._stub = gnmi_pb2_grpc.gNMIStub(self._channel)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._channel.close(None)

    def _new_channel(self) -> Channel:
        if self._insecure:
            return insecure_channel(str(self._target))

        if not self._tls:
            raise ValueError("no certificates specified, use 'insecure' to bypass")

        trusted_cert = self._tls.ca_cert or None
        chain = self._tls.client_cert or None
        private_key = self._tls.client_key or None

        if self._tls.get_server_cert:
            trusted_cert = get_server_certificate(
                self._target, self._tls.context, pem=True
            )

        creds = ssl_channel_credentials(
            root_certificates=trusted_cert,
            private_key=private_key,
            certificate_chain=chain,
        )

        return secure_channel(
            str(self._target), creds, options=list(self._grpc_options)
        )

    async def capabilities(self) -> CapabilityResponse:
        r"""Discover capabilities of the target

        Usage::

            In [3]: resp = await asess.capabilities()

            In [4]: resp.gnmi_version
            Out[4]: '0.10.0'

            In [5]: resp.supported_encodings
            Out[5]: [<Encoding.JSON: 0>, <Encoding.PROTO: 2>, <Encoding.JSON_IETF: 4>]

            In [7]: for model in resp.supported_models:
                ...:     print(model.name, model.version)
            openconfig-system-logging 0.3.1
            openconfig-messages 0.0.1
            openconfig-platform-types 1.0.0
            openconfig-if-types 0.2.1
            openconfig-acl 1.0.2
            openconfig-pf-srte 0.1.1
            openconfig-bgp 6.0.0
            ...

        :rtype: gnmi.models.capabilities.CapabilityResponse
        """

        _cr = CapabilityRequest()

        response = await self._stub.Capabilities(_cr.encode(), metadata=self._metadata)
        return CapabilityResponse.decode(response)

    async def get(
        self,
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

            In [9]: resp = await sess.get(paths, prefix="/", encoding="json")

            In [10]: async for notif in resp.notifications:
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
            extensions=extensions,
        )

        response = await self._stub.Get(_gr.encode(), metadata=self._metadata)
        return GetResponse.decode(response)

    async def set(
        self,
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
            In [4]: await sess.set(updates=updates)

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
            union_replacements=union_replacements,
        )

        response = await self._stub.Set(_sr.encode(), metadata=self._metadata)
        return SetResponse.decode(response)

    async def subscribe(
        self,
        subscriptions: Sequence[str | Path | Subscription],
        prefix: PathLike | None = None,
        encoding: Encoding | str | int = "json",
        mode: str = "stream",
        qos: int = 0,
        aggregate: bool = False,
        timeout: int | None = None,
    ) -> AsyncIterable[SubscribeResponse]:
        r"""Subscribe to state updates from the target

        Usage::

            In [57]: import grpc
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
                ...:     async for resp in responses:
                ...:         prefix = resp.update.prefix
                ...:         for update in resp.update.updates:
                ...:             path = prefix + update.path
                ...:             print(str(path), update.value)
                ...: except grpc.RpcError as e:
                ...:     # e.code() == grpc.StatusCode.DEADLINE_EXCEEDED on timeout
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
                    qos=qos,
                )
            ).encode()

        async for r in self._stub.Subscribe(
            _sr(), timeout=timeout, metadata=self._metadata
        ):
            yield SubscribeResponse.decode(r)
