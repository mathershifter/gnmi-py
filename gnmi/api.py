# -*- coding: utf-8 -*-

from typing import Iterable, AsyncGenerator, AsyncIterable, Sequence

from gnmi.tls import TLSConfig
from gnmi.session import Session, BasicAuth
from gnmi.async_session import AsyncSession
from gnmi.models import Notification, SetResponse, Subscription
from gnmi.models.path import PathLike
from gnmi.models.update import UpdateList
from gnmi.models.target import TargetLike

__all__ = ["capabilities", "delete", "get", "replace", "subscribe", "update"]


def _metadata(auth: BasicAuth = ("", "")) -> dict[str, str]:
    metadata: dict[str, str] = {}

    username, password = auth
    if username:
        metadata = {"username": username, "password": password or ""}

    return metadata


def _grpc_options(override: str = "") -> dict:
    grpc_options: dict = {}
    if override:
        grpc_options["server_host_override"] = override

    return grpc_options


def capabilities(
    target: str,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
):
    """
    Get supported models and encodings from target

    Usage::

        >>> capabilities("veos1:6030", auth=("admin", "p4ssw0rd"))

    :param target: gNMI target
    :type target: str
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.session.TLSConfig
    :param insecure: disable TLS
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """

    with Session(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        return sess.capabilities()


async def acapabilities(
    target: TargetLike,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
):
    """
    Async get supported models and encodings from target

    Usage::

        >>> import asyncio
        >>> asyncio.run(acapabilities("veos1:6030", auth=("admin", "p4ssw0rd")))

    :param target: gNMI target
    :type target: str
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.session.TLSConfig
    :param insecure: disable TLS
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """

    async with AsyncSession(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        return await sess.capabilities()


def get(
    target: TargetLike,
    paths: list,
    prefix: PathLike | None = None,
    encoding: str = "json",
    data_type: str = "all",
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
) -> Iterable[Notification]:
    """
    Get path(s) from target

    Usage::

        >>> responses = get("veos1:6030", ["/system/config"],
        ...     auth=("admin", "p4ssw0rd"))
        >>> for n in responses:
        ...     for upd in n.updates:
        ...         print(upd.path, upd.val)
        ...     for path in n.deletes:
        ...         print(str(path))

    :param target: gNMI target
    :type target: str
    :param prefix: Prefix path
    :type prefix: PathLike
    :param paths: list paths
    :type paths: str
    :param encoding: encoding to use
    :type encoding: str
    :param data_type: data type
    :type data_type: str
    :param auth: username and password
    :type auth: tuple
    :param insecure: insecure
    :type insecure: bool
    :param tls: SSL tls
    :type tls: gnmi.session.TLSConfig
    :param override: override hostname
    :type override: str

    """
    with Session(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        rsp = sess.get(paths, prefix=prefix, encoding=encoding, data_type=data_type)

        for notif in rsp.notifications:
            yield notif


async def aget(
    target: TargetLike,
    paths: Sequence[PathLike],
    prefix: PathLike | None = None,
    encoding: str = "json",
    data_type: str = "all",
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
) -> AsyncGenerator[Notification, None]:
    """
    Async get path(s) from target

    Usage::

        >>> async for notif in aget("veos1:6030", ["/system/config"],
        ...     auth=("admin", "p4ssw0rd")):
        ...     for upd in notif.updates:
        ...         print(upd.path, upd.val)
        ...     for path in notif.deletes:
        ...         print(str(path))
    """
    async with AsyncSession(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        rsp = await sess.get(
            paths, prefix=prefix, encoding=encoding, data_type=data_type
        )

        for notif in rsp.notifications:
            yield notif


def subscribe(
    target: TargetLike,
    paths: Sequence[PathLike],
    auth: BasicAuth = ("", ""),
    prefix: PathLike | None = None,
    encoding: str = "json",
    #
    mode: str = "stream",
    submode: str = "target_defined",
    #
    aggregate: bool = False,
    suppress: bool = False,
    #
    timeout: int = 0,
    interval: int = 0,
    heartbeat: int = 0,
    #
    insecure: bool = False,
    tls: TLSConfig | None = None,
    #
    qos: int = 0,
    override: str = "",
) -> Iterable[Notification]:
    """
    Subscribe to updates from target

    Usage::

        >>> responses = subscribe("veos1:6030", ["/system/processes/process"],
        ...     auth=("admin", "p4ssw0rd"))
        ...
        >>> for n in responses:
        ...     for upd in n.updates:
        ...         print(upd.path, upd.val)
        ...     for path in n.deletes:
        ...         print(str(path))

    :param target: gNMI target
    :type target: str
    :param paths: Path string
    :type paths: str
    :param prefix: Prefix path
    :type prefix: PathLike
    :param encoding: encoding to use
    :type encoding: str
    :param mode: mode to use
    :type mode: str
    :param qos: qos to use
    :type qos: int
    :param aggregate: aggregate to use
    :type aggregate: bool
    :param timeout: timeout to use
    :type timeout: int
    :param submode: submode to use
    :type submode: str
    :param suppress: suppress notifications
    :type suppress: bool
    :param interval: interval to use
    :type interval: int
    :param heartbeat: heartbeat to use
    :type heartbeat: int
    :param auth: username and password
    :type auth: tuple
    :param insecure: insecure
    :type insecure: bool
    :param tls: SSL certificates
    :type tls: gnmi.session.TLSConfig
    :param override: override hostname
    :type override: str
    """
    with Session(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        subs = []
        for p in paths:
            subs.append(
                Subscription(
                    path=p,
                    mode=submode,
                    sample_interval=interval,
                    heartbeat_interval=heartbeat,
                    suppress_redundant=suppress,
                )
            )

        for resp in sess.subscribe(
            subs,
            prefix=prefix,
            encoding=encoding,
            mode=mode,
            qos=qos,
            aggregate=aggregate,
            timeout=timeout,
        ):
            if resp.sync_response:
                continue
            yield resp.update


async def asubscribe(
    target: TargetLike,
    paths: Sequence[PathLike],
    auth: BasicAuth = ("", ""),
    prefix: PathLike | None = None,
    encoding: str = "json",
    mode: str = "stream",
    submode: str = "target_defined",
    aggregate: bool = False,
    suppress: bool = False,
    timeout: int = 0,
    interval: int = 0,
    heartbeat: int = 0,
    insecure: bool = False,
    tls: TLSConfig | None = None,
    qos: int = 0,
    override: str = "",
) -> AsyncIterable[Notification]:
    """
    Async subscribe to updates from target

    Usage::

        >>> async for notif in asubscribe("veos1:6030",
        ...     ["/system/processes/process"],
        ...     auth=("admin", "p4ssw0rd")):
        ...     for upd in notif.updates:
        ...         print(upd.path, upd.val)
        ...     for path in notif.deletes:
        ...         print(str(path))
    """
    async with AsyncSession(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        subs = []
        for p in paths:
            subs.append(
                Subscription(
                    path=p,
                    mode=submode,
                    sample_interval=interval,
                    heartbeat_interval=heartbeat,
                    suppress_redundant=suppress,
                )
            )

        async for resp in sess.subscribe(
            subs,
            prefix=prefix,
            encoding=encoding,
            mode=mode,
            qos=qos,
            aggregate=aggregate,
            timeout=timeout,
        ):
            if resp.sync_response:
                continue
            yield resp.update


def delete(
    target: TargetLike,
    paths: Sequence[PathLike],
    prefix: PathLike | None = None,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
) -> SetResponse:
    """
    Delete paths from the target

    Usage::

        >>> delete("veos1:6030", ["/some/deletable/path"],
        ...     auth=("admin", "p4ssw0rd"))

    :param target: gNMI target
    :type target: str
    :param paths: Path strings
    :type paths: list[str]
    :param prefix: Prefix path
    :type prefix: PathLike
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.session.TLSConfig
    :param insecure: insecure
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """

    with Session(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        return sess.set(deletes=paths, prefix=prefix)


async def adelete(
    target: TargetLike,
    paths: Sequence[PathLike],
    prefix: PathLike | None = None,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
) -> SetResponse:
    """
    Async delete paths from the target

    Usage::

        >>> import asyncio
        >>> asyncio.run(adelete("veos1:6030", ["/some/deletable/path"],
        ...     auth=("admin", "p4ssw0rd")))

    :param target: gNMI target
    :type target: str
    :param paths: Path strings
    :type paths: list[str]
    :param prefix: Prefix path
    :type prefix: PathLike
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.session.TLSConfig
    :param insecure: insecure
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """

    async with AsyncSession(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        return await sess.set(deletes=paths, prefix=prefix)


def replace(
    target: TargetLike,
    replacements: UpdateList,
    prefix: PathLike | None = None,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
) -> SetResponse:
    """
    Replace paths on the target

    Usage::
        >>> replace(
        ...     "veos1:6030",
        ...     [("/system/config/hostname", "newhostname")],
        ...     auth=("admin", "p4ssw0rd")
        ... )

    :param target: gNMI target
    :type target: str
    :param replacements: update path, value
    :type replacements: tuple
    :param prefix: Prefix path
    :type prefix: PathLike
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.session.TLSConfig
    :param insecure: insecure
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """
    with Session(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        return sess.set(replacements=replacements, prefix=prefix)


async def areplace(
    target: TargetLike,
    replacements: UpdateList,
    prefix: PathLike | None = None,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
) -> SetResponse:
    """
    Async replace paths on the target

    Usage::
        >>> import asyncio
        >>> asyncio.run(areplace(
        ...     "veos1:6030",
        ...     [("/system/config/hostname", "newhostname")],
        ...     auth=("admin", "p4ssw0rd")
        ... ))
    """
    async with AsyncSession(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        return await sess.set(replacements=replacements, prefix=prefix)


def update(
    target: TargetLike,
    updates: UpdateList,
    prefix: PathLike | None = None,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
) -> SetResponse:
    """
    Update paths on the target

    Usage::

        >>> update("veos1:6030",
        ...     [("/system/config/hostname", "newhostname")],
        ...     auth=("admin", "p4ssw0rd"))

    :param target: gNMI target
    :type target: str
    :param updates: update path, value
    :type updates: list[tuple]
    :param prefix: Prefix path
    :type prefix: PathLike
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.session.TLSConfig
    :param insecure: insecure
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """
    with Session(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        return sess.set(updates=updates, prefix=prefix)


async def aupdate(
    target: TargetLike,
    updates: UpdateList,
    prefix: PathLike | None = None,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: TLSConfig | None = None,
    override: str = "",
) -> SetResponse:
    """
    Async update paths on the target

    Usage::

        >>> import asyncio
        >>> asyncio.run(aupdate("veos1:6030",
        ...     [("/system/config/hostname", "newhostname")],
        ...     auth=("admin", "p4ssw0rd")))

    :param target: gNMI target
    :type target: str
    :param updates: update path, value
    :type updates: list[tuple]
    :param prefix: Prefix path
    :type prefix: PathLike
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.session.TLSConfig
    :param insecure: insecure
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """
    async with AsyncSession(
        target,
        metadata=_metadata(auth),
        insecure=insecure,
        tls=tls,
        grpc_options=_grpc_options(override),
    ) as sess:
        return await sess.set(updates=updates, prefix=prefix)
