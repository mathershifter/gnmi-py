# -*- coding: utf-8 -*-
# Copyright (c) 2025 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

import datetime

from dataclasses import dataclass

from datetime import date
from gnmi.deserialize import deserialize

@dataclass
class DeserialTest:
    name: str
    anniversary: date

    @classmethod
    def deserialize_anniversary(cls, data, **_) -> datetime.date:
        return datetime.date.fromisoformat(data)
    # def anniversary(self, v: str):
    #     pass

def test_deserailize():

    dt = deserialize(DeserialTest, dict(
        name="bub",
        anniversary="1977-02-19"
    ))

    assert dt is not None
    assert dt.name == "bub"
    assert dt.anniversary == date(1977, 2, 19)
