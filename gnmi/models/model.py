# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.
import typing as t

from abc import ABC, abstractmethod

T = t.TypeVar('T')

# def validates(prop: str):
#     def inner(func):
#         @functools.wraps(func)
#         def wrapper(self, *args, **kwargs):
#             val = getattr(self, prop)
#             res = func(self, *args, **kwargs)
#             # print("After method execution")
#             return res
#         return wrapper
#
#     return inner

class BaseModel(ABC, t.Generic[T]):

    def __setattr__(self, name, value):
        if hasattr(self, name+"_factory"):
            value = getattr(self, name+"_factory")(value)

        super().__setattr__(name, value)


    @abstractmethod
    def encode(self) -> T:
        pass

    @classmethod
    @abstractmethod
    def decode(cls, v: T) -> "BaseModel":
        pass


