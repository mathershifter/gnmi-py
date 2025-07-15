# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.exceptions import GrpcDeadlineExceeded
import typing as t
from gnmi.session import Session, TLSConfig, BasicAuth

from gnmi.models import Notification, SetResponse
__all__ = ["capabilites", "delete", "get", "replace", "subscribe", "update"]


def _new_session(
    target: str,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: t.Optional[TLSConfig] = None,
    override: str = "",
):
    metadata: dict[str, str] = {}
    
    username, password = auth
    if username:
        metadata = {"username": username, "password": password or ""}

    grpc_options: dict = {}
    if override:
        grpc_options["server_host_override"] = override

    return Session(
        target,
        metadata=metadata,
        tls=tls,
        insecure=insecure,
        grpc_options=grpc_options,
    )


def capabilites(
    target: str,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: t.Optional[TLSConfig] = None,
    override: str = "",
):
    """
    Get supported models and encodings from target

    Usage::

        >>> capabilites("veos1:6030", auth=("admin", "p4ssw0rd"))

    :param target: gNMI target
    :type target: str
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.structures.CertificateStore
    :param insecure: disable TLS
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """
    sess = _new_session(target, auth, insecure, tls, override)
    return sess.capabilities()


def get(
    target: str,
    paths: list,
    prefix: t.Optional[None] = None,
    encoding: str = "json",
    data_type: str = "all",
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: t.Optional[TLSConfig] = None,
    override: str = ""
) -> t.Iterable[Notification]:
    """
    Get path(s) from target

    Usage::

        >>> respones = get("veos1:6030", ["/system/config"],
        ...     auth=("admin", "p4ssw0rd"))
        >>> for n in respones:
        ...     for upd in n.updates:
        ...         print(upd.path, upd.val)
        ...     for path in n.deletes:
        ...         print(str(path))

    :param target: gNMI target
    :type target: str
    :param prefix: Prefix path
    :type prefix: str
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
    :type tls: gnmi.structures.CertificateStore
    :param override: override hostname
    :type override: str

    """
    sess = _new_session(target, auth, insecure, tls, override)
    rsp = sess.get(
            paths,
            prefix=prefix,
            encoding=encoding,
            data_type=data_type)

    for notif in rsp.notifications:
        yield notif


def subscribe(
    target: str,
    paths: list,
    auth: BasicAuth = ("", ""),
    prefix: t.Optional[str] = None,
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
    tls: t.Optional[TLSConfig] = None,
    #
    qos: int = 0,
    override: str = "",
) -> t.Iterable[Notification]:
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
    :type prefix: str
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
    :type tls: gnmi.structures.CertificateStore
    :param override: override hostname
    :type override: str
    """
    sess = _new_session(target, auth, insecure, tls, override)

    try:
        for resp in sess.subscribe(paths,
                                   prefix=prefix,
                                   encoding=encoding,
                                   mode=mode,
                                   qos=qos,
                                   aggregate=aggregate,
                                   timeout=timeout,
                                   submode=submode,
                                   suppress=suppress,
                                   interval=interval,
                                   heartbeat=heartbeat):
            if resp.sync_response:
                continue
            yield resp.update

    except GrpcDeadlineExceeded:
        pass

def delete(
    target: str,
    paths: list[str],
    prefix: t.Optional[str] = None,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: t.Optional[TLSConfig] = None,
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
    :type prefix: str
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.structures.CertificateStore
    :param insecure: insecure
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """

    sess = _new_session(target, auth, insecure, tls, override)
    rsp: SetResponse = sess.set(deletes=paths, prefix=prefix)
    return rsp


def replace(
    target: str,
    replacements: list[tuple[str, t.Any]],
    prefix: t.Optional[str] = None,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: t.Optional[TLSConfig] = None,
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
    :type prefix: str
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.structures.CertificateStore
    :param insecure: insecure
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """
    sess = _new_session(target, auth, insecure, tls, override)
    rsp: SetResponse = sess.set(replacements=replacements, prefix=prefix)
    return rsp


def update(
    target: str,
    updates: list[tuple[str, t.Any]],
    prefix: t.Optional[str] = None,
    auth: BasicAuth = ("", ""),
    insecure: bool = False,
    tls: t.Optional[TLSConfig] = None,
    override: str = "",
) -> SetResponse:
    """
    Update paths on the target

    Usage::
        >>> replace("veos1:6030",
        ...     [("/system/config/hostname", "newhostname")],
        ...     auth=("admin", "p4ssw0rd"))

    :param target: gNMI target
    :type target: str
    :param updates: update path, value
    :type updates: list[tuple]
    :param prefix: Prefix path
    :type prefix: str
    :param auth: username and password
    :type auth: tuple
    :param tls: SSL certificates
    :type tls: gnmi.structures.CertificateStore
    :param insecure: insecure
    :type insecure: bool
    :param override: override hostname
    :type override: str
    """
    sess = _new_session(target, auth, insecure, tls, override)
    rsp: SetResponse = sess.set(updates=updates, prefix=prefix)
    return rsp
