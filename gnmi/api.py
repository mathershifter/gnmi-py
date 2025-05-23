# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

from gnmi.messages import Notification_, SetResponse_
from gnmi.exceptions import GrpcDeadlineExceeded
import typing as t
from gnmi.session import Session
from gnmi.structures import Auth, CertificateStore, GetOptions
from gnmi.structures import Options, SubscribeOptions
from gnmi.target import Target

__all__ = ["capabilites", "delete", "get", "replace", "subscribe", "update"]


def _new_session(
    target: str,
    auth: Auth = ("", ""),
    insecure: bool = False,
    certificates: CertificateStore = {},
    override: str = "",
):
    target_ = Target.from_url(target)

    metadata: dict[str, str] = {}
    
    username, password = auth
    if username:
        metadata = {"username": username, "password": password or ""}

    grpc_options: dict = {}
    if override:
        grpc_options["server_host_override"] = override

    return Session(
        target_,
        metadata=metadata,
        certificates=certificates,
        insecure=insecure,
        grpc_options=grpc_options,
    )


def capabilites(
    target: str,
    auth: Auth = ("", None),
    insecure: bool = False,
    certificates: CertificateStore = {},
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
    :param certificates: SSL certificates
    :type auth: gnmi.structures.CertificateStore
    :param override: override hostname
    :type override: str
    """
    sess = _new_session(target, auth, insecure, certificates, override)
    return sess.capabilities()


def get(
    target: str,
    paths: list,
    auth: Auth = ("", None),
    insecure: bool = False,
    certificates: CertificateStore = {},
    override: str = "",
    options: GetOptions = {},
) -> t.Iterable[Notification_]:
    """
    Get path(s) from target

    Usage::

        >>> respones = get("veos1:6030", ["/system/config"],
        ...     auth=("admin", "p4ssw0rd"))
        >>> for notif in respones:
        ...     for update in notif.updates:
        ...         print(update.path, update.get_value())
        ...     for path in notif.deletes:
        ...         print(str(path))

    :param target: gNMI target
    :type target: str
    :param paths: Path string
    :type paths: str
    :param auth: username and password
    :type auth: tuple
    :param certificates: SSL certificates
    :type certificates: gnmi.structures.CertificateStore
    :param override: override hostname
    :type override: str
    :param options: Get options
    :type options: gnmi.structures.GetOptions
    """
    sess = _new_session(target, auth, insecure, certificates, override)

    for notif in sess.get(paths, options=options):
        yield notif


def subscribe(
    target: str,
    paths: list,
    auth: Auth = ("", None),
    insecure: bool = False,
    certificates: CertificateStore = {},
    override: str = "",
    options: SubscribeOptions = {},
) -> t.Iterable[Notification_]:
    """
    Subscribe to updates from target

    Usage::

        >>> responses = subscribe("veos1:6030", ["/system/processes/process"],
        ...     auth=("admin", "p4ssw0rd"))s
        ...
        >>> for resp in responses:
        ...     for update in resp.update:
        ...         for update in update.updates:
        ...             print(update.path, update.get_value())
        ...         for path in update.deletes:
        ...             print(str(path))

    :param target: gNMI target
    :type target: str
    :param paths: Path string
    :type paths: str
    :param auth: username and password
    :type auth: tuple
    :param certificates: SSL certificates
    :type certificates: gnmi.structures.CertificateStore
    :param override: override hostname
    :type override: str
    :param options: Subscribe options
    :type options: gnmi.structures.SubscribeOptions
    """
    sess = _new_session(target, auth, insecure, certificates, override)

    try:
        for resp in sess.subscribe(paths, options=options):
            if resp.sync_response:
                continue
            yield resp.update

    except GrpcDeadlineExceeded:
        pass


def delete(
    target: str,
    deletes: list[str] = [],
    auth: Auth = ("", None),
    insecure: bool = False,
    certificates: CertificateStore = {},
    override: str = "",
    options: Options = {},
) -> SetResponse_:
    """
    Delete paths from the target

    Usage::

        >>> delete("veos1:6030", ["/some/deletable/path"],
        ...     auth=("admin", "p4ssw0rd"))

    :param target: gNMI target
    :type target: str
    :param paths: Path string
    :type paths: str
    :param auth: username and password
    :type auth: tuple
    :param certificates: SSL certificates
    :type certificates: gnmi.structures.CertificateStore
    :param override: override hostname
    :type override: str
    :param options: Subscribe options
    :type options: gnmi.structures.SubscribeOptions
    """

    sess = _new_session(target, auth, insecure, certificates, override)
    rsp: SetResponse_ = sess.set(deletes=deletes, options=options)
    return rsp


def replace(
    target: str,
    replacements: list[tuple[str, t.Any]] = [],
    auth: Auth = ("", None),
    insecure: bool = False,
    certificates: CertificateStore = {},
    override: str = "",
    options: Options = {},
) -> SetResponse_:
    """
    Replace paths on the target

    Usage::
        >>> replacements = [("/system/config/hostname", "newhostname")]
        >>> replace("veos1:6030", replacements,
        ...     auth=("admin", "p4ssw0rd"))

    :param target: gNMI target
    :type target: str
    :param replacements: update path, value
    :type replacements: tuple
    :param auth: username and password
    :type auth: tuple
    :param certificates: SSL certificates
    :type certificates: gnmi.structures.CertificateStore
    :param override: override hostname
    :type override: str
    :param options: Subscribe options
    :type options: gnmi.structures.SubscribeOptions
    """
    sess = _new_session(target, auth, insecure, certificates, override)
    rsp: SetResponse_ = sess.set(replacements=replacements, options=options)
    return rsp


def update(
    target: str,
    updates: list[tuple[str, t.Any]] = [],
    auth: Auth = ("", None),
    insecure: bool = False,
    certificates: CertificateStore = {},
    override: str = "",
    options: Options = {},
) -> SetResponse_:
    """
    Update paths on the target

    Usage::
        >>> updates = [("/system/config", {"hostname": "newhostname"})]
        >>> replace("veos1:6030", updates,
        ...     auth=("admin", "p4ssw0rd"))

    :param target: gNMI target
    :type target: str
    :param updates: update path, value
    :type updates: tuple
    :param auth: username and password
    :type auth: tuple
    :param certificates: SSL certificates
    :type certificates: gnmi.structures.CertificateStore
    :param override: override hostname
    :type override: str
    :param options: Subscribe options
    :type options: gnmi.structures.SubscribeOptions
    """
    sess = _new_session(target, auth, insecure, certificates, override)
    rsp: SetResponse_ = sess.set(updates=updates, options=options)
    return rsp
