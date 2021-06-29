# /usr/bin/python3
# -*- coding: UTF-8 -*-
"""game ui"""

import sys
import time
import logging
from PyQt6 import QtWidgets, QtGui, uic
from PyQt6.QtWidgets import QWidgetAction
from PyQt6.QtCore import QThread, pyqtSignal

from asmbattle import Assembler, Memory, Cpu, Screen, FaultError, NumBase
class Worker(QThread):
    signal_running = pyqtSignal(bool)
    signal_error = pyqtSignal(str)

    def __init__(self, memory: Memory, cpu: Cpu, screen: Screen, speed_hz: float ):
        super().__init__()
        self._memory = memory
        self._cpu = cpu
        self._screen = screen
        self._speed_hz = speed_hz

    def run(self):
        ns_in_sec = 1000000000000.0
        start_time_s = time.time_ns() / ns_in_sec
        target_duration_s = 1 / self._speed_hz
        try:
            while self._cpu.step():
                self.signal_running.emit(True)
                if self.isInterruptionRequested():
                    break

                end_time_s = time.time_ns() / ns_in_sec
                duration_s = end_time_s - start_time_s
                sleep_duration_s = target_duration_s - duration_s

                logging.getLogger(__name__).debug(
                    f"speed(hz): {self._speed_hz}start: {start_time_s} end: {end_time_s} duration: {duration_s} target: {target_duration_s} sleep: {sleep_duration_s}")

                if sleep_duration_s > 0.0:
                    logging.debug("sleeping")
                    time.sleep(sleep_duration_s)
                start_time = time.time_ns() / ns_in_sec

        except (FaultError, ValueError) as error:
            self.signal_error.emit(str(error))
        finally:
            self.signal_running.emit(False)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("./asmbattle_test.ui", self)

        # little hack to make window content resizable
        layout = self.centralWidget().children()[0].layout()
        self.centralWidget().setLayout(layout)

        logging.basicConfig(level=logging.ERROR)

        # View initialization
        self._assemble = Assembler()
        self._memory = Memory()
        self._screen = Screen(width=64, height=8)
        self._cpu = Cpu(self._memory, self._screen, 0)
        self._code_mapping = None
        self.numeric_format = NumBase.Hexadecimal
        self.thread = None
        self.show_error("")
        self._code_mapping = None
        self._code = ""

        self.toolButton_assemble.clicked.connect(self.do_action_assemble)
        self.actionAssemble.triggered.connect(self.do_action_assemble)

        self.toolButton_run.clicked.connect(self.do_action_run)
        self.actionRun.triggered.connect(self.do_action_run)

        self.toolButton_step.clicked.connect(self.do_action_step)
        self.actionStep.triggered.connect(self.do_action_step)

        self.toolButton_reset.clicked.connect(self.do_action_reset)
        self.actionReset.triggered.connect(self.do_action_reset)

        self.actionQuit.triggered.connect(self.action_quit)
        self.radioButton_hex.toggled.connect(self.change_numeric_format)

        # colors
        self.sp_color = self.lineEdit_reg_SP.palette().color(QtGui.QPalette.ColorRole.Base)  # color.getRgb()
        self.ip_color = self.lineEdit_reg_IP.palette().color(QtGui.QPalette.ColorRole.Base)  # color.getRgb()
        self.last_access_color = QtGui.QColor(168,239,182,255)
        self.set_default_program()      # only when launching program
        # fill display
        self.do_action_reset()


    def change_numeric_format(self, checked):
        if checked:
            format_obj = NumBase.Hexadecimal
        else:
            format_obj = NumBase.Decimal
        if format_obj.format != self.numeric_format:
            self.numeric_format = format_obj
            self._memory.display_format = format_obj
            self._cpu.display_format = format_obj
            self.refresh()

    def action_quit(self):
        exit()

    def stop_action_run(self):
        self.thread.requestInterruption()

    def do_action_run(self):
        self.show_error("")
        self.toolButton_run.setText("STOP")
        self.toolButton_run.clicked.connect(self.stop_action_run)
        self.toolButton_run.clicked.disconnect(self.do_action_run)

        self.thread = Worker(memory=self._memory,
                             cpu=self._cpu,
                             screen=self._screen,
                             speed_hz=float(self.label_speed_hz.text()))
        self.thread.signal_running.connect(self.signal_running_accept)
        self.thread.signal_error.connect(self.show_error)
        self.thread.setTerminationEnabled(True)
        self.thread.start()

    def signal_running_accept(self, is_running: bool):
        if is_running:
            self.refresh()
        else:
            self.toolButton_run.setText(">> Run")
            self.toolButton_run.clicked.disconnect(self.stop_action_run)
            self.toolButton_run.clicked.connect(self.do_action_run)

    def do_action_step(self) -> bool:
        self.show_error("")
        try:
            result = self._cpu.step()
        except (FaultError, ValueError) as error:
            self.show_error(str(error))
        self.refresh()

    def do_action_reset(self):
        self.show_error("")
        self._cpu.reset()
        self._screen.reset()
        if len(self.textEdit_code.toPlainText()) == 0:
            self.set_default_program()
        self.refresh()

    def do_action_assemble(self):
        self.show_error("")
        self._memory.reset()
        try:
            self._code = self.textEdit_code.toPlainText()
            program = self._assemble.assemble(self._code)
            self._memory.mass_store(0, program["code"])
            self._code_mapping = program["mapping"]
        except (ValueError, IndexError) as error:
            self.show_error(str(error))
        finally:
            self.refresh_memory()


    def refresh(self):
        self.refresh_memory()
        self.refresh_screen()
        self.refresh_processor()
        self.refresh_code()

    def rgb_to_hex(self, r, g, b):
        """convert rgb to hex
        see: https://www.w3resource.com/python-exercises/string/python-data-type-string-exercise-95.php"""
        return ('{:02X}' * 3).format(r, g, b)

    def refresh_code(self):
        output = ""
        code = self._code
        mapping = self._code_mapping
        r, g, b, a = self.ip_color.getRgb()
        color = self.rgb_to_hex(r, g, b)
        begin_ip_color = f'<span style=" background-color:#{color};\" >'
        end_color = '</span>'

        if code is None or len(code) == 0:
            self.textEdit_code.setPlaitext("")
            return
        # find line to highlight
        if mapping is not None:
            ip = self._cpu.instruction_pointer
            ip_line = mapping[ip]
        else:
            ip_line = -1

        code_lines = self._code.split('\n')
        for i in range(len(code_lines)):
            if i == ip_line:
                output += begin_ip_color
            output += code_lines[i]
            if i == ip_line:
                output += end_color
            output += "<br>"
        self.textEdit_code.setHtml(output)


    def refresh_memory(self):
        device = self._memory
        last_access = device._last_access

        output = ""
        r, g, b, a = self.last_access_color.getRgb()
        color = self.rgb_to_hex(r, g, b)
        begin_access_color = f'<span style=" background-color:#{color};\" >'
        r, g, b, a = self.sp_color.getRgb()
        color = self.rgb_to_hex(r, g, b)
        begin_sp_color = f'<span style=" background-color:#{color};\" >'
        r, g, b, a = self.ip_color.getRgb()
        color = self.rgb_to_hex(r, g, b)
        begin_ip_color = f'<span style=" background-color:#{color};\" >'
        sp = self._cpu._registries[Cpu.REG_SP]
        ip = self._cpu.instruction_pointer
        end_color = '</span>'

        output = ""
        for i in range(device._size):
            in_color = True
            if i % self.numeric_format.value == 0:
                output += "<br>"
            if i == ip:
                output += begin_ip_color
            elif i >= sp:
                output  += begin_sp_color
            elif i == last_access:
                output += begin_access_color
            else:
                in_color = False
            output += format(device._data[i], self.numeric_format.format) + " "
            if in_color:
                output += end_color

        self.textBrowser_memory.setHtml(output)

    def refresh_screen(self):
        device = self._screen
        last_access = device._last_access

        output = ""
        r, g, b, a = self.last_access_color.getRgb()
        color = self.rgb_to_hex(r, g, b)
        begin_color = f'<span style=" background-color:#{color};\" >'
        end_color = '</span>'


        for y in range(device._height):
            output += "<br>"
            for x in range(device._width):
                i = y * device._width + x
                if i == last_access:
                    output += begin_color
                output += f"{chr(device._data[i])} "
                if i == last_access:
                    output += end_color

        self.textBrowser_screen.setHtml(output)

    def refresh_processor(self):
        self.lineEdit_reg_A.setText(self._cpu.get_registry("A"))
        self.lineEdit_reg_B.setText(self._cpu.get_registry("B"))
        self.lineEdit_reg_C.setText(self._cpu.get_registry("C"))
        self.lineEdit_reg_D.setText(self._cpu.get_registry("D"))
        self.lineEdit_reg_SP.setText(self._cpu.get_registry("SP"))
        self.lineEdit_reg_IP.setText(self._cpu.get_registry("IP"))

        self.lineEdit_ind_A.setText(format(self._memory._data[self._cpu._registries[Cpu.REG_A]], self.numeric_format.format))
        self.lineEdit_ind_B.setText(format(self._memory._data[self._cpu._registries[Cpu.REG_B]], self.numeric_format.format))
        self.lineEdit_ind_C.setText(format(self._memory._data[self._cpu._registries[Cpu.REG_C]], self.numeric_format.format))
        self.lineEdit_ind_D.setText(format(self._memory._data[self._cpu._registries[Cpu.REG_D]], self.numeric_format.format))
        self.lineEdit_ind_SP.setText(format(self._memory._data[self._cpu._registries[Cpu.REG_SP]], self.numeric_format.format))
        self.lineEdit_ind_IP.setText(format(self._memory._data[self._cpu._instruction_pointer], self.numeric_format.format))

        self.lineEdit_zero.setText(str(self._cpu.get_flag("ZERO")))
        self.lineEdit_carry.setText(str(self._cpu.get_flag("CARRY")))
        self.lineEdit_fault.setText(str(self._cpu.get_flag("FAULT")))

    def show_error(self, message: str):
        if message is None or len(message) == 0:
            self.label_error_message.hide()
        else:
            self.label_error_message.setText(message)
            self.label_error_message.setVisible(True)

    def set_default_program(self):
        self._code = """
 
            ; Simple example
            ; Writes Hello World to the output
            
            JMP start
            hello: DB "Hello World!" 	; Variable
                   DB 0		; String terminator
            
            start:
                MOV C, hello    	; Point to var 
                MOV D, 0    		; Point to output
                CALL print
                HLT             	; Stop execution
            
            print:			; print(C:*from, D:*to)
                PUSH A
                PUSH B
                MOV B, 0
            .loop:
                MOV A, [C]		; Get char from var
                OUT [D], A		; Write to output
                INC C
                INC D  
                CMP B, [C]		; Check if end
                JNZ .loop		; jump if not
            
                POP B
                POP A
                RET
	    
	    """

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()