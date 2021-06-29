# /usr/bin/python3
# -*- coding: UTF-8 -*-
"""memory representation"""

from enum import Enum
from math import log, ceil

class NumBase(Enum):
    def __new__(cls, value, format):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.format = format
        return obj

    Decimal = (10, "3d")
    Hexadecimal = (16, "02X")

class BaseStorage:
    MIN_VALUE = 0
    MAX_VALUE = 0xFF
    DEFAULT_MEMORY_SIZE = 256

    def __init__(self, memory_size: int = DEFAULT_MEMORY_SIZE, init_value: int = 0):
        self._size = memory_size
        self._init_value = init_value
        self._data = [self._init_value] * self._size
        self._last_access = -1
        self.display_format = NumBase.Hexadecimal

    def reset(self):
        self._data = [self._init_value] * self._size
        self._last_access = -1

    def __len__(self):
        return self._size

    def load(self, address: int) -> int:
        if address < 0 or address >= self._size:
            raise KeyError(f"Memory access violation at {address}")

        self._last_access = address
        return self._data[address]

    def store(self, address: int, value: int, owner):
        """Note: owner for compatibility with subclasses"""
        if address < 0 or address >= self._size:
            raise KeyError(f"Memory access violation at {address}")

        if value < Memory.MIN_VALUE or value > Memory.MAX_VALUE:
            raise ValueError(f"Memory overflow with value {value}")

        self._last_access = address
        self._data[address] = value

    def mass_store(self, address: int, values: [int], owner:int = -1):
        for v in values:
            self.store(address, v, owner)
            address += 1

    def __str__(self):
        output = ""
        for i in range(self._size):
            if i % self.display_format.value == 0:
                output += "\n"
            output += format(self._data[i], self.display_format.format) + " "
        return output

class Memory(BaseStorage):
    MAX_SP = 255
    MIN_SP = 0


    def __init__(self, memory_size: int=BaseStorage.DEFAULT_MEMORY_SIZE):
        super().__init__(memory_size)
        self._owner = [0] * memory_size

    def reset(self):
        super().reset()
        self._owner = [0] * Memory.DEFAULT_MEMORY_SIZE

    def store(self, address: int, value: int, owner: int):
        super().store(address, value, owner)    # owner not used in base class. to overcome overloading limitation
        self._owner[address] = owner

    @property
    def last_access(self):
        return self._last_access


class Screen(BaseStorage):
    def __init__(self, width:int, height:int):
        super().__init__(width * height, ord(" "))
        self._width = width
        self._height = height

        @property
        def width (self):
            return self._width

        @property
        def height (self):
            return self._height

    def reset(self):
        self._data = [ord(" ")] * self._size
        self._last_access = -1

    def __str__(self):
        output = ""

        for y in range(self._height):
            output +="\n"
            for x in range(self._width):
                i = y * self._width + x
                output += f"{chr(self._data[i])} "
        return output

