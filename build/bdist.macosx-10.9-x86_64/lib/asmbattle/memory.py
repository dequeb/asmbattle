# /usr/bin/python3
# -*- coding: UTF-8 -*-
"""memory representation"""

from enum import Enum
from math import log, ceil

class FaultError(BaseException):
    pass

class NumBase(Enum):
    def __new__(cls, value, format):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.format = format
        return obj

    Decimal = (10, "6d")
    Hexadecimal = (16, "04X")

class BaseStorage:
    MIN_VALUE = 0
    MAX_VALUE = 0xFFFF
    DEFAULT_MEMORY_SIZE = 0x200

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

    def load(self, address: int, by_cpu=True) -> int:
        if address < 0 or address > self._size:
            raise KeyError(f"Memory access violation at {address}")

        if by_cpu:
            self._last_access = address
        return self._data[address]

    def store(self, address: int, value: int, owner, by_cpu=True):
        """Note: owner for compatibility with subclasses"""
        if address < 0 or address >= self._size:
            raise KeyError(f"Memory access violation at {address}")

        if value < Memory.MIN_VALUE or value > Memory.MAX_VALUE:
            raise ValueError(f"Memory overflow with value {value}")

        if by_cpu:
            self._last_access = address
        self._data[address] = value

    def mass_store(self, address: int, values: [int], owner=-1):
        for v in values:
            self.store(address, v, owner, by_cpu=False)
            address += 1

    def __str__(self):
        output = ""
        for i in range(len(self)):
            if i % self.display_format.value == 0:
                output += "\n"
            output += format(self.load(i, by_cpu=False), self.display_format.format) + " "
        return output

    def min_SP(self):
        return 0

class Memory(BaseStorage):
    def __init__(self, memory_size: int=BaseStorage.DEFAULT_MEMORY_SIZE, init_value: int = 0):
        super().__init__(memory_size, init_value)
        self._owner = [-1] * memory_size

    def reset(self):
        super().reset()
        self._owner = [-1] * len(self)

    def store(self, address: int, value: int, owner: int, by_cpu=True):
        super().store(address, value, owner, by_cpu)    # owner not used in base class. to overcome overloading limitation
        self._owner[address] = owner

    @property
    def last_access(self):
        return self._last_access

    def owner(self, address):
        return self._owner[address]

class ROM(Memory):
    """read-only memory"""
    DEFAULT_MEMORY_SIZE = 0x40

    def __init__(self, memory_size: int):
        super().__init__(memory_size)

    def store(self, address: int, value: int, owner: int, by_cpu=True):
        if owner >= 0 or by_cpu:
            address_str = format(address, self.display_format.format)
            raise FaultError(f"Read-only memory at {address_str}")
        else:
            super().store(address, value, owner, by_cpu)

    def mass_store(self, address: int, values: [int], can_write_rom=False, owner=-1):
        if not can_write_rom:
            raise FaultError(f"address {address} is read-only")
        else:
            super().mass_store(address, values, owner)

class MixedMemory(Memory):
    def __init__(self,
                 ram_size: int = BaseStorage.DEFAULT_MEMORY_SIZE,
                 rom_size: int = ROM.DEFAULT_MEMORY_SIZE):
        super().__init__(ram_size)
        self._rom = ROM(rom_size)
        self._rom_base = 0
        self._ram_base = self._rom_base + rom_size

    def load(self, address: int, by_cpu = True) -> int:
        if address in range(self._rom_base, self._ram_base):
            value =  self._rom.load(address, by_cpu)
        else:
            value = super().load(address - self._ram_base, by_cpu)
        if by_cpu:
            self._last_access = address
        return value

    def store(self, address: int, value: int, owner, by_cpu=True):
        if address in range(self._rom_base, self._ram_base):
            self._rom.store(address, value, owner, by_cpu)
        else:
            super().store(address - self._ram_base, value, owner, by_cpu) # this will raise an error
        if by_cpu:
            self._last_access = address

    def mass_store(self, address: int, values: [int], can_write_rom=False, owner=-1):
        if address in range(self._rom_base, self._ram_base):
            self._rom.mass_store(address, values, can_write_rom, owner)
        else:
            return super().mass_store(address, values, owner)

    def owner(self, address):
        assert address in range(len(self)), f"Adresse {address} out of range {range(len(self))}"

        if address in range(self._rom_base, self._ram_base):
            return self._rom.owner(address)
        else:
            return super().owner(address - self._ram_base)

    def is_rom(self, address):
        return  address in range(self._rom_base, self._ram_base)

    def is_ram(self, address):
        return not self.is_rom(address)

    def __len__(self):
        return self._size + len(self._rom)

    @property
    def rom_base(self):
        return self._rom_base

    @property
    def ram_base(self):
        return self._ram_base

    def min_SP(self):
        return self._ram_base

class Screen(Memory):
    DEFAULT_VALUE="\u2581"

    def __init__(self, width:int, height:int):
        super().__init__(width * height, ord(Screen.DEFAULT_VALUE))
        self._width = width
        self._height = height

        @property
        def width (self):
            return self._width

        @property
        def height (self):
            return self._height

    def __str__(self):
        output = ""

        for y in range(self._height):
            output +="\n"
            for x in range(self._width):
                i = y * self._width + x
                output += f"{chr(self._data[i])} "
        return output

def main():
    mm = MixedMemory()
    mm.mass_store(mm.rom_base, [1, 2, 3, 4], can_write_rom=True)
    mm.mass_store(mm.ram_base, [255, 254, 253, 252])
    print(mm)
    assert mm.load(mm.rom_base, by_cpu=False) == 1, f"{mm.load(mm.rom_base, by_cpu=False)} == 1"
    assert mm.load(mm.ram_base, by_cpu=False) == 255, f"{mm.load(mm.ram_base, by_cpu=False)}== 255"



if __name__ == "__main__":
    main()