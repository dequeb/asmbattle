# /usr/bin/python3
# -*- coding: UTF-8 -*-
"""simple assembler code"""
import logging
import math
from math import floor, ceil, log

from .opcodes import OpCodes
from .memory import BaseStorage, Memory, NumBase


class FaultError(BaseException):
    pass


class Cpu:
    MIN_VALUE = 0
    MAX_VALUE = 255

    REG_A = 0
    REG_B = 1
    REG_C = 2
    REG_D = 3
    REG_SP = 4
    LAST_REGISTRY = REG_SP
    REGISTRY_COUNT = LAST_REGISTRY + 1

    def __init__(self, memory: BaseStorage, io: BaseStorage, cpu_id: int):
        self._memory = memory
        self._io = io
        self._id = cpu_id
        self._log = logging.getLogger(__name__)
        self.display_format = NumBase.Hexadecimal

        self._registries = [0] * Cpu.REGISTRY_COUNT
        self._stack_pointer = Memory.MAX_SP
        self._instruction_pointer = 0
        self._zero = False
        self._carry = False
        self._fault = False

    def reset(self):
        self._registries = [0] * Cpu.REGISTRY_COUNT
        self._stack_pointer = Memory.MAX_SP
        self._instruction_pointer = 0
        self._zero = False
        self._carry = False
        self._fault = False
        self._instruction_pointer = self._id * 2    # implement simple multiprocessor jump table

    def get_registry(self, name: str):
        format_str = self.display_format.format
        name = name.upper()

        if name == "A":
            return format(self._registries[Cpu.REG_A], format_str)
        elif name == "B":
            return format(self._registries[Cpu.REG_B], format_str)
        elif name == "C":
            return format(self._registries[Cpu.REG_C], format_str)
        elif name == "D":
            return format(self._registries[Cpu.REG_D], format_str)
        elif name == "SP":
            return format(self._registries[Cpu.REG_SP], format_str)
        elif name == "IP":
            return format(self._instruction_pointer, format_str)
        else:
            raise KeyError(f"Unknown key: {name}")

    def get_flag(self, name: str):
        format_str ="^6"
        name = name.upper()

        if name == "ZERO":
            return format(str(self._zero), format_str)
        elif name == "CARRY":
            return format(str(self._carry), format_str)
        elif name == "FAULT":
            return format(str(self._fault), format_str)
        else:
            raise KeyError(f"Unknown key: {name}")

    @property
    def _stack_pointer(self):
        return self._registries[Cpu.REG_SP]

    @_stack_pointer.setter
    def _stack_pointer(self, value: int):
        if value < Cpu.MIN_VALUE:
            self._fault = True
            raise FaultError(f"Stack overflow")
        elif value > Cpu.MAX_VALUE:
            self._fault = True
            raise FaultError(f"Stack underflow")
        self._registries[Cpu.REG_SP] = value

    @property
    def id(self):
        return self._id

    @property
    def zero(self):
        return self._zero

    @property
    def carry(self):
        return self._carry

    @property
    def fault(self):
        return self._fault

    def _check_gpr_sp(self, reg: int):
        if reg in range(Cpu.LAST_REGISTRY + 1):
            return reg
        else:
            self._fault = True
            raise FaultError(f"Invalid registry {reg}")

    def _check_gpr(self, reg: int):
        if reg in range(Cpu.REG_A, Cpu.REG_D):
            return reg
        else:
            self._fault = True
            raise FaultError(f"Invalid registry {reg}")

    def _check_value(self, value: int):
        if value in range(Cpu.MIN_VALUE, Cpu.MAX_VALUE):
            return value
        else:
            self._fault = True
            raise FaultError(f"Value out of bound {value}")

    def _check_operation(self, value: int) -> int:
        self._zero = False
        self._carry = False

        if value > Cpu.MAX_VALUE:
            self._carry = True
            value %= (Cpu.MAX_VALUE + 1)
        elif value == 0:
            self._zero = True
        elif value < 0:
            self._carry = True
            value = (Cpu.MAX_VALUE + 1) - (-value % (Cpu.MAX_VALUE + 1))
        return value

    def _jump(self, new_ip):
        self.instruction_pointer = new_ip

    def _push(self, value: int):
        self._memory.store(self._registries[Cpu.REG_SP], value, self._id)
        self._stack_pointer -= 1
        if self._stack_pointer < self._memory.MIN_SP:
            self._fault = True
            raise FaultError("Stack overflow")

    def _pop(self) -> int:
        self._stack_pointer += 1
        return self._memory.load(self._stack_pointer)

    def _divide(self, divisor):
        """ return A integer divided by divisor

        :param divisor: divisor of A
        :return: integer division
        """
        if divisor == 0:
            self._fault = True
            raise FaultError("Division by zero")
        else:
            return math.floor(self._get_gpr_sp(0) / divisor)

    @property
    def instruction_pointer(self):
        return self._instruction_pointer

    @instruction_pointer.setter
    def instruction_pointer(self, value):
        if value < 0 or value >= len(self._memory):
            self._fault = True
            raise FaultError(f"Instruction pointer {self._instruction_pointer} is outside of memory")
        self._instruction_pointer = value

    def increment_instruction_pointer(self):
        self.instruction_pointer = self._instruction_pointer + 1

    def _get_gpr_sp(self, reg: int):
        reg = self._check_gpr_sp(reg)
        return self._registries[reg]

    def _get_gpr(self, reg: int):
        return self._get_gpr_sp(reg)

    def _set_gpr_sp(self, reg: int, value: int):
        reg = self._check_gpr_sp(reg)
        value = self._check_value(value)
        self._registries[reg] = value

    def _set_gpr(self, reg: int, value: int):
        reg = self._check_gpr(reg)
        value = self._check_value(value)
        self._registries[reg] = value

    def _indirect_registry_address(self, value):
        """indirect memory address"""
        reg = value % 8     # TODO : remove constants from code
        base = self._registries[reg]
        offset = floor(value / 8)
        if offset > 15:
            offset -= 32
        return base + offset

    def step(self) -> bool:
        instr_name = "UNKNOWN"

        if self._fault:
            raise FaultError("FAULT. Reset to continue")
        else:
            try:
                instr = self._memory.load(self._instruction_pointer)
                instr_name = OpCodes(instr).name
                # switch case on operand name
                function_name = getattr(self, f"_oper_{instr_name}", None)
                if function_name is not None:
                    result = function_name()
                else:
                    raise FaultError(f"Unknown instruction {instr} = {instr_name} at: {self._instruction_pointer}")

            except FaultError as error:
                self._fault = True
                raise error
            finally:
                self._log.debug(f"instr: {instr_name}, ip: {self._instruction_pointer} z: {self._zero} c:{self._carry} f: {self._fault} ")
        return result

    def _memory_load_at_ip(self) -> int:
        self.increment_instruction_pointer()
        return self._memory.load(self.instruction_pointer)

    def _oper_NONE(self):
        return False

    def _oper_MOV_REG_TO_REG(self):
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        reg_from = self._check_gpr_sp(self._memory_load_at_ip())
        self._set_gpr_sp(reg_to, self._get_gpr_sp(reg_from))
        self.increment_instruction_pointer()
        return True

    def _oper_MOV_ADDRESS_TO_REG(self):
        reg_to = self._memory_load_at_ip()
        mem_from = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._memory.load(mem_from))
        self.increment_instruction_pointer()
        return True

    def _oper_MOV_REGADDRESS_TO_REG(self):
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._memory.load(self._indirect_registry_address(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_MOV_REG_TO_ADDRESS(self):
        mem_to = self._memory_load_at_ip()
        reg_from = self._check_gpr_sp(self._memory_load_at_ip())
        self._memory.store(mem_to, self._get_gpr_sp(reg_from), self.id)
        self.increment_instruction_pointer()
        return True

    def _oper_MOV_REG_TO_REGADDRESS(self):
        reg_to = self._memory_load_at_ip()
        reg_from = self._check_gpr_sp(self._memory_load_at_ip())
        self._memory.store(self._indirect_registry_address(reg_to), self._get_gpr_sp(reg_from), self._id)
        self.increment_instruction_pointer()
        return True

    def _oper_MOV_NUMBER_TO_REG(self):
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        number = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, number)
        self.increment_instruction_pointer()
        return True

    def _oper_MOV_NUMBER_TO_ADDRESS(self):
        mem_to = self._memory_load_at_ip()
        number = self._memory_load_at_ip()
        self._memory.store(mem_to, number, self.id)
        self.increment_instruction_pointer()
        return True

    def _oper_MOV_NUMBER_TO_REGADDRESS(self):
        reg_to = self._memory_load_at_ip()
        number = self._memory_load_at_ip()
        self._memory.store(self._indirect_registry_address(reg_to), number, self.id)
        self.increment_instruction_pointer()
        return True

    def _oper_ADD_REG_TO_REG(self):
        """reg_to = reg_to + reg_from"""
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        reg_from = self._check_gpr_sp(self._memory_load_at_ip())
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) +
                                                       self._get_gpr_sp(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_ADD_REGADDRESS_TO_REG(self):
        """reg_to = reg_to + [reg_from]"""
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) +
                                                       self._memory.load(self._indirect_registry_address(reg_from))))
        self.increment_instruction_pointer()
        return True

    def _oper_ADD_ADDRESS_TO_REG(self):
        """reg_to = reg_to + [number]"""
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        mem_from = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) +
                                                       self._memory.load(mem_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_ADD_NUMBER_TO_REG(self):
        """reg_to = reg_to + number"""
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        number = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) +
                                                       number))
        self.increment_instruction_pointer()
        return True

    def _oper_SUB_REG_FROM_REG(self):
        """reg_to = reg_to - reg_from"""
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        reg_from = self._check_gpr_sp(self._memory_load_at_ip())
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) -
                                                       self._get_gpr_sp(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_SUB_REGADDRESS_FROM_REG(self):
        """reg_to = reg_to - [reg_from]"""
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) -
                                                       self._memory.load(self._indirect_registry_address(reg_from))))
        self.increment_instruction_pointer()
        return True

    def _oper_SUB_ADDRESS_FROM_REG(self):
        """reg_to = reg_to - [number]"""
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        mem_from = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) -
                                                       self._memory.load(mem_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_SUB_NUMBER_FROM_REG(self):
        """reg_to = reg_to - number"""
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        number = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) -
                                                       number))
        self.increment_instruction_pointer()
        return True

    def _oper_INC_REG(self):
        """ reg_to ++ """
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) + 1))
        self.increment_instruction_pointer()
        return True

    def _oper_DEC_REG(self):
        """ -- reg_to """
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        self._set_gpr_sp(reg_to, self._check_operation(self._get_gpr_sp(reg_to) - 1))
        self.increment_instruction_pointer()
        return True

    def _oper_CMP_REG_WITH_REG(self):
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        reg_from = self._check_gpr_sp(self._memory_load_at_ip())
        self._check_operation(self._get_gpr_sp(reg_to) -
                              self._get_gpr_sp(reg_from))
        self.increment_instruction_pointer()
        return True

    def _oper_CMP_REGADDRESS_WITH_REG(self):
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._check_operation(self._get_gpr_sp(reg_to) -
                              self._memory.load(self._indirect_registry_address(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_CMP_ADDRESS_WITH_REG(self):
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        mem_from = self._memory_load_at_ip()
        self._check_operation(self._get_gpr_sp(reg_to) -
                              self._memory.load(mem_from))
        self.increment_instruction_pointer()
        return True

    def _oper_CMP_NUMBER_WITH_REG(self):
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        number = self._memory_load_at_ip()
        self._check_operation(self._get_gpr_sp(reg_to) -
                              number)
        self.increment_instruction_pointer()
        return True

    def _oper_JMP_REGADDRESS(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        self._jump(self._registries[reg_to])
        return True

    def _oper_JMP_ADDRESS(self):
        number = self._memory_load_at_ip()
        self._jump(number)
        return True

    def _oper_JC_REGADDRESS(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        if self._carry:
            self._jump(self._registries[reg_to])
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JC_ADDRESS(self):
        number = self._memory_load_at_ip()
        if self._carry:
            self._jump(number)
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JNC_REGADDRESS(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        if not self._carry:
            self._jump(self._registries[reg_to])
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JNC_ADDRESS(self):
        number = self._memory_load_at_ip()
        if not self._carry:
            self._jump(number)
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JZ_REGADDRESS(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        if self._zero:
            self._jump(self._registries[reg_to])
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JZ_ADDRESS(self):
        number = self._memory_load_at_ip()
        if self._zero:
            self._jump(number)
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JNZ_REGADDRESS(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        if not self._zero:
            self._jump(self._registries[reg_to])
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JNZ_ADDRESS(self):
        number = self._memory_load_at_ip()
        if not self._zero:
            self._jump(number)
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JA_REGADDRESS(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        if not (self._carry or self._zero):
            self._jump(self._registries[reg_to])
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JA_ADDRESS(self):
        number = self._memory_load_at_ip()
        if not (self._carry or self._zero):
            self._jump(number)
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JNA_REGADDRESS(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        if self._carry or self._zero:
            self._jump(self._registries[reg_to])
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_JNA_ADDRESS(self):
        number = self._memory_load_at_ip()
        if self._carry or self._zero:
            self._jump(number)
        else:
            self.increment_instruction_pointer()
        return True

    def _oper_PUSH_REG(self):
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._push(self._registries[reg_from])
        self.increment_instruction_pointer()
        return True

    def _oper_PUSH_REGADDRESS(self):
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._push(self._memory.load(self._indirect_registry_address(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_PUSH_ADDRESS(self):
        mem_from = self._memory_load_at_ip()
        self._push(self._memory.load(mem_from))
        self.increment_instruction_pointer()
        return True

    def _oper_PUSH_NUMBER(self):
        number = self._memory_load_at_ip()
        self._push(number)
        self.increment_instruction_pointer()
        return True

    def _oper_POP_REG(self):
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._registries[reg_from] = self._pop()
        self.increment_instruction_pointer()
        return True

    def _oper_CALL_REGADDRESS(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        self._push(self._instruction_pointer+1)   # return at current postion + 1
        self._jump(self._registries[reg_to])
        return True

    def _oper_CALL_ADDRESS(self):
        number = self._memory_load_at_ip()
        self._push(self._instruction_pointer+1)   # return at current postion + 1
        self._jump(number)
        return True

    def _oper_RET(self):
        self._jump(self._pop())
        return True

    def _oper_MUL_REG(self):
        """ A = A * reg """
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._registries[Cpu.REG_A] = self._check_operation(self._registries[Cpu.REG_A] *
                                                            self._get_gpr(reg_from))
        self.increment_instruction_pointer()
        return True

    def _oper_MUL_REGADDRESS(self):
        """ A = A * [reg] """
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._registries[Cpu.REG_A] = self._check_operation(self._registries[Cpu.REG_A] *
                                                            self._memory.load(self._indirect_registry_address(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_MUL_ADDRESS(self):
        """ A = A * [number] """
        mem_from = self._memory_load_at_ip()
        self._registries[Cpu.REG_A] = self._check_operation(self._registries[Cpu.REG_A] *
                                                            self._memory.load(mem_from))
        self.increment_instruction_pointer()
        return True

    def _oper_MUL_NUMBER(self):
        """ A = A * number """
        number = self._memory_load_at_ip()
        self._registries[Cpu.REG_A] = self._check_operation(self._registries[Cpu.REG_A] *
                                                            number)
        self.increment_instruction_pointer()
        return True

    def _oper_DIV_REG(self):
        """ A = A / reg """
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._registries[Cpu.REG_A] = self._check_operation(self._registries[Cpu.REG_A] //
                                                            self._get_gpr(reg_from))
        self.increment_instruction_pointer()
        return True

    def _oper_DIV_REGADDRESS(self):
        """ A = A / [reg] """
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._registries[Cpu.REG_A] = self._check_operation(self._registries[Cpu.REG_A] //
                                                            self._memory.load(self._indirect_registry_address(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_DIV_ADDRESS(self):
        """ A = A / [number] """
        mem_from = self._memory_load_at_ip()
        self._registries[Cpu.REG_A] = self._check_operation(self._registries[Cpu.REG_A] //
                                                            self._memory.load(mem_from))
        self.increment_instruction_pointer()
        return True

    def _oper_DIV_NUMBER(self):
        """ A = A / number """
        number = self._memory_load_at_ip()
        self._registries[Cpu.REG_A] = self._check_operation(self._registries[Cpu.REG_A] //
                                                            number)
        self.increment_instruction_pointer()
        return True

    def _oper_AND_REG_WITH_REG(self):
        """reg_to = reg_to AND reg_from"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) &
                                                       self._get_gpr(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_AND_REGADDRESS_WITH_REG(self):
        """reg_to = reg_to AND [reg_from]"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) &
                                                       self._memory.load(self._indirect_registry_address(reg_from))))
        self.increment_instruction_pointer()
        return True

    def _oper_AND_ADDRESS_WITH_REG(self):
        """reg_to = reg_to AND [number]"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        mem_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) &
                                                       self._memory.load(mem_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_AND_NUMBER_WITH_REG(self):
        """reg_to = reg_to AND number"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        number = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) &
                                                       number))
        self.increment_instruction_pointer()
        return True

    def _oper_OR_REG_WITH_REG(self):
        """reg_to = reg_to OR reg_from"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._check_gpp(self._memory_load_at_ip())
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) |
                                                       self._get_gpr(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_OR_REGADDRESS_WITH_REG(self):
        """reg_to = reg_to OR [reg_from]"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) |
                                                       self._memory.load(self._indirect_registry_address(reg_from))))
        self.increment_instruction_pointer()
        return True

    def _oper_OR_ADDRESS_WITH_REG(self):
        """reg_to = reg_to OR [number]"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        mem_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) |
                                                       self._memory.load(mem_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_OR_NUMBER_WITH_REG(self):
        """reg_to = reg_to OR number"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        number = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) |
                                                       number))
        self.increment_instruction_pointer()
        return True

    def _oper_XOR_REG_WITH_REG(self):
        """reg_to = reg_to XOR reg_from"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) ^
                                                       self._get_gpr(reg_from)))
        self.increment_instruction_pointer()
        return True


    def _oper_XOR_REGADDRESS_WITH_REG(self):
        """reg_to = reg_to XOR [reg_from]"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) ^
                                                       self._memory.load(self._indirect_registry_address(reg_from))))
        self.increment_instruction_pointer()
        return True

    def _oper_XOR_ADDRESS_WITH_REG(self):
        """reg_to = reg_to XOR [number]"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        mem_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) ^
                                                       self._memory.load(mem_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_XOR_NUMBER_WITH_REG(self):
        """reg_to = reg_to XOR number"""
        reg_to = self._check_gpr(self._memory_load_at_ip())
        number = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) ^
                                                       number))
        self.increment_instruction_pointer()
        return True

    def _oper_NOT_REG(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        self._set_gpr(reg_to, self._check_operation(~self._get_gpr(reg_to)))
        self.increment_instruction_pointer()
        return True

    def _oper_SHL_REG_WITH_REG(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) <<
                                                       self._get_gpr(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_SHL_REGADDRESS_WITH_REG(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) <<
                                                    self._memory.load(self._indirect_registry_address(reg_from))))
        self.increment_instruction_pointer()
        return True

    def _oper_SHL_ADDRESS_WITH_REG(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        mem_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) <<
                                                    self._memory.load(mem_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_SHL_NUMBER_WITH_REG(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        number = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) <<
                                                    number))
        self.increment_instruction_pointer()
        return True

    def _oper_SHR_REG_WITH_REG(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._check_gpr(self._memory_load_at_ip())
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) >>
                                                       self._get_gpr(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_SHR_REGADDRESS_WITH_REG(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) >>
                                                    self._memory.load(self._indirect_registry_address(reg_from))))
        self.increment_instruction_pointer()
        return True

    def _oper_SHR_ADDRESS_WITH_REG(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        mem_from = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) >>
                                                    self._memory.load(mem_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_SHR_NUMBER_WITH_REG(self):
        reg_to = self._check_gpr(self._memory_load_at_ip())
        number = self._memory_load_at_ip()
        self._set_gpr(reg_to, self._check_operation(self._get_gpr(reg_to) <<
                                                    number))
        self.increment_instruction_pointer()
        return True

    def _oper_IN_PORT_TO_REG(self):
        reg_to = self._memory_load_at_ip()
        port_from = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._io.load(port_from))
        self.increment_instruction_pointer()
        return True

    def _oper_IN_REGPORT_TO_REG(self):
        reg_to = self._check_gpr_sp(self._memory_load_at_ip())
        reg_from = self._memory_load_at_ip()
        self._set_gpr_sp(reg_to, self._io.load(self._indirect_registry_address(reg_from)))
        self.increment_instruction_pointer()
        return True

    def _oper_OUT_REG_TO_PORT(self):
        port_to = self._memory_load_at_ip()
        reg_from = self._check_gpr_sp(self._memory_load_at_ip())
        self._io.store(port_to, self._get_gpr_sp(reg_from), self.id)
        self.increment_instruction_pointer()
        return True

    def _oper_OUT_REG_TO_REGPORT(self):
        reg_to = self._memory_load_at_ip()
        reg_from = self._check_gpr_sp(self._memory_load_at_ip())
        self._io.store(self._indirect_registry_address(reg_to), self._get_gpr_sp(reg_from), self._id)
        self.increment_instruction_pointer()
        return True


    def __str__(self):
        format_str = self.display_format.format
        output = "   A       B       C       D       IP      SP     Z     C     F    \n"

        for reg in range(Cpu.REG_A, Cpu.REG_D + 1):
            output += format(self._registries[reg], format_str)

        output += format(self._instruction_pointer, format_str) + format(self._registries[Cpu.REG_SP], format_str)+ \
                  f"{str(self._zero):^6}{str(self._carry):^6}{str(self._fault):^6}"

        return output
