# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
from typing import TypeVar, Generic, Protocol
from dataclasses import dataclass
from abc import abstractmethod

T = TypeVar('T')

@dataclass
class BaseModel(Protocol, Generic[T]):

    @abstractmethod
    def encode(self) -> T: ...

    @classmethod
    @abstractmethod
    def decode(cls, v: T) -> "BaseModel": ...


