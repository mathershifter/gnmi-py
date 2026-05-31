# -*- coding: utf-8 -*-

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


