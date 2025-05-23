# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import typing as t
import grpc

DEFAULT_GRPC_PORT: t.Final[int] = 6030
DEFAULT_GRPC_HOST: t.Final[str] = "localhost"

GNMIRC_FILES: t.Final[list[str]] = [".gnmirc", "_gnmirc"]

GRPC_CODE_MAP: t.Final[dict] = {x.value[0]: x for x in grpc.StatusCode} # type: ignore