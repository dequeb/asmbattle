# /usr/bin/python3
# -*- coding: UTF-8 -*-
"""game ui"""

import time
import locale
import logging
import random
import sys
import threading
import tkinter
from tkinter import filedialog, messagebox, PhotoImage

from asmbattle.assembler import Assembler
from asmbattle.cpu import Cpu
from asmbattle.memory import Screen, MixedMemory, NumBase, FaultError, Memory
from asmbattle.ui_view import BaseWindow
from asmbattle.files import *

# Set up message catalog access
t = get_translation('ui_controller')
t.install()
_ = t.gettext

class Worker(threading.Thread):
    def __init__(self,
                 event_generator: tkinter.Tk,
                 stop_event: threading.Event,
                 memory: Memory, cpus: [Cpu], screen: Screen, speed_hz: float):
        super().__init__()
        # check cpus valid
        assert len(cpus) > 0

        self._stop_event = stop_event
        self.event_generator = event_generator
        self.errorss = [[] for i in range(len(cpus))]
        self._memory = memory
        self._cpus = cpus
        self._screen = screen
        self.speed_hz = speed_hz
        self._file_modified = False
        self._filename = ""

    def signal_running(self, running: bool):
        self.event_generator.event_generate("<<running>>", x=int(running))

    def signal_error(self, text: str, cpu_id: int):
        logging.debug(f"cpu id: {cpu_id}, text: {text}")
        self.errorss[cpu_id].append(text)
        self.event_generator.event_generate("<<error>>", x=len(self.errorss[cpu_id]) - 1, y=cpu_id)

    def run(self):
        ns_in_sec = 10000000000.0
        REFRESH_FRAME_DELAY = 1.0 / 60.0  # 24 frames per second
        start_time_s = time.time_ns() / ns_in_sec
        start_time_frame_s = time.time_ns() / ns_in_sec
        running = True
        sleep_duration_s = 0.0
        logging.debug(f"lauching {len(self._cpus)} CPU(s).")
        ids = [i for i in range(len(self._cpus))]

        while running:
            running = False
            random.shuffle(ids)   # execute cpu in a different sequence each time

            for i in range(len(self._cpus)):
                if self._cpus[ids[i]] is not None:
                    if self._stop_event.wait(0.0):
                        running = False
                        break
                    try:
                        if self._cpus[ids[i]].step():
                            running = True
                        else:
                            raise FaultError(_("CPU Halted"))
                    except (FaultError, KeyError, ValueError) as error:
                        self.signal_error(str(error), ids[i])
                        # remove cpu from array
                        self._cpus[ids[i]] = None

            # refresh GUI
            end_time_s = time.time_ns() / ns_in_sec
            duration_frame_s =  end_time_s - start_time_frame_s
            if duration_frame_s > REFRESH_FRAME_DELAY:
                logging.debug("refreshing UI")
                self.signal_running(True)
                start_time_frame_s = end_time_s
            else:
                logging.debug(f"expecting {REFRESH_FRAME_DELAY} and got {duration_frame_s} second. skipping UI")
            # adjust CPU speed
            duration_s = end_time_s - start_time_s
            target_duration_s = 1 / self.speed_hz    # speed might be changed by main process
            sleep_duration_s = max(0.0, target_duration_s - duration_s)   # avoid negative sleep time
            start_time_s = time.time_ns() / ns_in_sec
            logging.debug(f"sleeping during {sleep_duration_s} seconds")

            if self._stop_event.wait(sleep_duration_s):
                running = False
                break
        self.signal_running(True)       # final GUI refresh
        logging.debug("stopping...")
        self.signal_running(False)

class MainWindow(BaseWindow):
    ROM_COLOR = "#B4B4B4"
    INSTR_COLOR = "#B4D2FF"
    TITLE = _("ASM Battle")

    def __init__(self, nb_cpu=1, *args, **kwargs):
        BaseWindow.__init__(self, title=MainWindow.TITLE)

        # Model initialization
        self._nb_cpu = nb_cpu
        self._assemble = Assembler()
        self._memory = MixedMemory(rom_size=0x80)   # NOTE: ROM jump table must be adjust according to ROM size
        self._screen = Screen(width=100, height=4)
        self._cpus = []
        for i in range(self._nb_cpu):
            self._cpus.append(Cpu(self._memory, self._screen, len(self._memory) - (i * 0x20) - 1, i))

        self._code_mapping = None
        self.numeric_format = NumBase.Hexadecimal
        self.thread = None
        self._stop_event = None
        self.show_error("")
        self._filename = ""
        self._original_code = ""

        # colors
        self.last_access_color = BaseWindow.LAST_ACCESS_COLOR
        self.cpu_colors = [BaseWindow.PLAYER1_COLOR,
                           BaseWindow.PLAYER2_COLOR,
                           BaseWindow.PLAYER3_COLOR,
                           BaseWindow.PLAYER4_COLOR]

        assert len(self.cpu_colors) == self._nb_cpu, "nb colors not matching nb cpu"
        self.load_rom()

        # fill display
        self._textEditor_code.delete(1.0, tkinter.END)  # remove default value
        self.reset_button_clicked()

        # custom events
        self.bind("<<running>>", self.receive_running)
        self.bind("<<error>>", self.receive_error)
        self.bind("<<RefreshWindow>>", self.do_refresh)
        self.do_refresh()   # cannot call event, as event not has not started yet

    def __del__(self):
        self.stop_button_clicked()

    def numeric_format_changed(self):
        if self._display_hexadecimal.get():
            format_obj = NumBase.Hexadecimal
        else:
            format_obj = NumBase.Decimal
        if format_obj.format != self.numeric_format:
            self.numeric_format = format_obj
            self._memory.display_format = format_obj
            for i in range(len(self._cpus)):
                self._cpus[i].display_format = format_obj
            self.refresh()

    def speed_hz_changed(self):
        if self.thread is not None:
            self.thread.speed_hz = int(self._speed_hz.get())

    def code_modified(self, event=None):
        if super().code_modified(event):
            self.code_changed(True)

    def code_changed(self, changed=True):
        self._file_modified = changed
        self.update_title()

    def get_filename(self) -> str:
        return self._filename

    def set_filename(self, filename):
        self._filename = filename
        self.update_title()

    def update_title(self):
        SEP = " - "
        MARKER = "*"

        title = MainWindow.TITLE
        if len(self._filename) > 0:
            title += SEP + self._filename
        if self._file_modified:
            title += MARKER
        self.title(title)

    def load(self):
        code = "."
        filename = filedialog.askopenfilename(parent=self, title=_("Load ASM"), initialdir=".",
                                              filetypes=((_("text files"), "*.txt"), (_("assembler files"), "*.asm")))
        if len(filename) > 0:
            try:
                with open(filename, 'r') as f:
                    code = f.read()
            except (IOError, FileNotFoundError) as error:
                self.show_error(str(error))
            finally:
                # change current directory
                dir_name = os.path.dirname(filename)
                os.chdir(dir_name)
        return filename, code

    def load_button_clicked(self):
        filename, code = self.load()
        if len(filename) > 0:
            self._textEditor_code.delete(1.0, tkinter.END)  # remove default value
            self._textEditor_code.insert(1.0, code)
            self.set_filename(filename)
            self.code_changed(False)
            self.assemble_button_clicked()

    def save_button_clicked(self):
        filename = self.get_filename()
        if len(filename) == 0:
            filename = filedialog.asksaveasfilename(parent=self, title=_("Save ASM"), initialdir=".",
                                                    filetypes=((_("assembler files"), "*.asm"),))
            # change current directory
            if len(filename) > 0:
                dir_name = os.path.dirname(filename)
                os.chdir(dir_name)

        if len(filename) > 0:
            try:
                with open(filename, 'w') as f:
                    f.write(self._textEditor_code.get(1.0, tkinter.END))
                self.set_filename(filename)
                self.code_changed(False)
            except (IOError, FileNotFoundError) as error:
                self.show_error(str(error))

    def stop_button_clicked(self):
        try:
            self._stop_event.set()
        except AttributeError:
            pass

    def run_button_clicked(self, cpu_ids=[0]):
        self.show_error("")
        self.run_btn.configure(text=_("STOP"), command=self.stop_button_clicked)

        cpus = []
        for i in range(len(self._cpus)):
            if i in cpu_ids:
                cpus.append(self._cpus[i])
            else:
                cpus.append(None)

        self._stop_event = threading.Event()
        self.thread = Worker(self,
                             self._stop_event,
                             memory=self._memory,
                             cpus=cpus,
                             screen=self._screen,
                             speed_hz=float(self._speed_hz.get()))
        self.thread.start()

    def receive_error(self, event: tkinter.Event):
        cpu_id = event.y        # hack since data field not implemented in python
        error_no = event.x
        self.show_error(self.thread.errorss[cpu_id][error_no], cpu_id)

    def receive_running(self, event: tkinter.Event):
        is_running = bool(event.x)   # hack since data field not implemented in python

        if is_running:
            self.refresh()
        else:
            self.run_btn.configure(text=_(">>Run"), command=self.run_button_clicked)
            self.thread = None
            self._stop_event = None

    def step_button_clicked(self):
        self.show_error("")
        try:
            if self._cpus[0].step():       # only first cpu active in simulation
                self.refresh()
            else:
                raise FaultError(_("CPU Halted"))
        except (FaultError, ValueError, KeyError) as error:
            self.show_error(str(error))

    def reset_button_clicked(self):
        self.show_error("")
        for i in range(len(self._cpus)):
            self._cpus[i].reset()
        self._screen.reset()
        self.refresh()

    def assemble_button_clicked(self):
        self.reset_button_clicked()
        self._memory.reset()
        self._code_mapping = self.load_program_for_cpu(0, self._textEditor_code.get(1.0, tkinter.END))
        self.refresh()

    def do_file_new(self):
        self._textEditor_code.delete(1.0, tkinter.END)
        self.reset_button_clicked()

    def do_file_open(self):
        self.load_button_clicked()

    def do_file_save(self):
        self.save_button_clicked()

    def load_program_for_cpu(self, cpu_id: int, code: str, single_user = False) -> dict:
        """load program for processor proc_id based on jump table in ROM and return mapping"""
        assert cpu_id in range(self._nb_cpu), "Cpu number of out range"

        mapping = None
        try:
            # get processor entry point from jump table
            jump_address = (cpu_id * 2) + 1
            base_address = self._memory.load(jump_address, by_cpu=False)

            # assemble code for loading at base memory
            program = self._assemble.assemble(code, base_address)

            # get max program size base on space between jump table to avoid simple overwrite on load
            max_program_size = self._memory.load(((1 * 2) + 1), by_cpu=False) -\
                               self._memory.load(((0 * 2) + 1), by_cpu=False)
            if single_user:
                max_program_size *= self._nb_cpu

            program_size = len(program["code"])
            if program_size > max_program_size:
                program_size_str = format(program_size, self.numeric_format.format)
                max_program_size_str = format(max_program_size, self.numeric_format.format)

                raise FaultError(
                    _("Memory protection error: program size {} exceed limit of {}")
                      .format(program_size_str, max_program_size_str))
            self._memory.mass_store(base_address, program["code"], owner=cpu_id)
            mapping = program["mapping"]

        except (FaultError, ValueError, KeyError, IndexError) as error:
            self.show_error(str(error), cpu_id)
        self.refresh_memory()
        return mapping

    def refresh(self):
        self.event_generate("<<RefreshWindow>>")

    def do_refresh(self, event=None):
        try:
            self.refresh_memory()
            self.refresh_screen()
            self.refresh_processor(0)
            self.refresh_code()
        except AttributeError:
            # object not fully initialized
            pass

    def get_reg_colors(self,  use_default_cpu_colors) -> {str: str}:
        if use_default_cpu_colors:
            sp_colors = [BaseWindow.SP_COLOR] * self._nb_cpu
            ip_colors = [BaseWindow.IP_COLOR] * self._nb_cpu
        else:
            sp_colors = self.cpu_colors
            ip_colors = self.cpu_colors
        return {"ip": ip_colors, "sp": sp_colors}

    def refresh_code(self):
        code = self._textEditor_code.get(1.0, tkinter.END).rstrip()   # remove blank characters at the end
        mapping = self._code_mapping
        color = self.IP_COLOR

        if code is None or len(code) == 0:
            self._textEditor_code.insert(1.0, self.get_default_program())
            self.code_changed(False)
            self.set_filename("")
            return
        else:
            self._textEditor_code.delete(1.0, tkinter.END)

        # find line to highlight
        if mapping is not None:
            ip = self._cpus[0].instruction_pointer
            try:
                ip_line = mapping[ip]
            except KeyError:
                ip_line = -1    # during processor fault
        else:
            ip_line = -1

        code_lines = code.split('\n')
        for i in range(len(code_lines)):
            begin_pos = self._textEditor_code.index(tkinter.INSERT)
            self._textEditor_code.insert(tkinter.INSERT, code_lines[i] + "\n")
            end_pos = self._textEditor_code.index(tkinter.INSERT)

            if i == ip_line:
                logging.debug(f"ip_line = {i}")

                self._textEditor_code.tag_add("code", begin_pos, end_pos)
                self._textEditor_code.tag_config("code", background=color)

    def set_memory_display(self, text_widget: tkinter.Text, nb_cpu_to_display=1, use_default_cpu_colors=True):
        device = self._memory
        last_access = device._last_access

        sp = []
        ip = []
        for i in range(nb_cpu_to_display):
            sp.append(self._cpus[i]._registries[Cpu.REG_SP])
            ip.append(self._cpus[i].instruction_pointer)

        colors = self.get_reg_colors(use_default_cpu_colors)
        ip_colors = colors["ip"]
        sp_colors = colors["sp"]
        cpu_colors = self.cpu_colors

        text_widget.delete(1.0, tkinter.END)
        for i in range(len(device)):
            if i % (2 * self.numeric_format.value) == 0:
                begin_pos = text_widget.index(tkinter.INSERT)
                text_widget.insert(tkinter.INSERT, "\n" + format(i, self.numeric_format.format) + " ")
                end_pos = text_widget.index(tkinter.INSERT)
                tag = f"header{i}"
                text_widget.tag_add(tag, begin_pos, end_pos)
                text_widget.tag_config(tag, font=("Courier New", "12", "bold"))

            bg_color = "#FFFFFF"
            fg_color = "#000000"
            in_color = False
            for cpu_id in range(nb_cpu_to_display):
                if i == ip[cpu_id]:
                    bg_color = ip_colors[cpu_id]
                    in_color = True
                    break
                elif i >= sp[cpu_id]:
                    bg_color = sp_colors[cpu_id]
                    in_color = True
                    break

            if not in_color:
                if i == last_access:
                    bg_color = BaseWindow.LAST_ACCESS_COLOR
                    in_color = True
                elif self._code_mapping is not None and i in self._code_mapping:
                    bg_color = MainWindow.INSTR_COLOR
                    in_color = True
                elif self._memory.is_rom(i):
                    bg_color = MainWindow.ROM_COLOR
                    in_color = True

            if device.owner(i) in range(nb_cpu_to_display):
                fg_color = cpu_colors[device.owner(i)]
                in_color = True

            begin_pos = text_widget.index(tkinter.INSERT)
            text_widget.insert(tkinter.INSERT, f"{format(device.load(i, by_cpu=False), self.numeric_format.format)} ")
            if in_color:
                end_pos = text_widget.index(tkinter.INSERT)
                tag = f"mem{i}"
                text_widget.tag_add(tag, begin_pos, end_pos)
                text_widget.tag_config(tag, background=bg_color, foreground=fg_color)

    def set_screen_display(self, text_widget: tkinter.Text):
        device = self._screen
        last_access = device._last_access
        text_widget.delete(1.0, tkinter.END)

        for y in range(device._height):
            if y > 0:
                text_widget.insert(tkinter.INSERT, "\n")

            for x in range(device._width):
                i = y * device._width + x

                bg_color = "#FFFFFF"
                fg_color = "#000000"
                in_color = False

                if i == last_access:
                    bg_color = BaseWindow.LAST_ACCESS_COLOR
                    in_color = True

                if device.owner(i) in range(len(self._cpus)):
                    fg_color = self.cpu_colors[device.owner(i)]
                    in_color = True

                begin_pos = text_widget.index(tkinter.INSERT)
                text_widget.insert(tkinter.INSERT, f"{chr(device.load(i, by_cpu=False))}")
                if in_color:
                    end_pos = text_widget.index(tkinter.INSERT)
                    tag = f"scr{i}"
                    text_widget.tag_add(tag, begin_pos, end_pos)
                    text_widget.tag_config(tag, background=bg_color, foreground=fg_color)

    def refresh_memory(self):
        self.set_memory_display(self._textEditor_memory)

    def refresh_screen(self):
        self.set_screen_display(self._textEditor_screen)

    def refresh_processor(self, proc_id):
        self._cpu_display["REG_A"].set(self._cpus[proc_id].get_registry("A"))
        self._cpu_display["REG_B"].set(self._cpus[proc_id].get_registry("B"))
        self._cpu_display["REG_C"].set(self._cpus[proc_id].get_registry("C"))
        self._cpu_display["REG_D"].set(self._cpus[proc_id].get_registry("D"))
        self._cpu_display["REG_SP"].set(self._cpus[proc_id].get_registry("SP"))
        self._cpu_display["REG_IP"].set(self._cpus[proc_id].get_registry("IP"))

        try:
            self._cpu_display["IND_A"].set(format(
                self._memory.load(self._cpus[proc_id]._registries[Cpu.REG_A], by_cpu=False), self.numeric_format.format))
        except (FaultError, KeyError):
            self._cpu_display["IND_A"].set("ERR")

        try:
            self._cpu_display["IND_B"].set(format(
                self._memory.load(self._cpus[proc_id]._registries[Cpu.REG_B], by_cpu=False), self.numeric_format.format))
        except (FaultError, KeyError):
            self._cpu_display["IND_B"].set("ERR")

        try:
            self._cpu_display["IND_C"].set(format(
                self._memory.load(self._cpus[proc_id]._registries[Cpu.REG_C], by_cpu=False), self.numeric_format.format))
        except (FaultError, KeyError):
            self._cpu_display["IND_C"].set("ERR")

        try:
            self._cpu_display["IND_D"].set(format(
                self._memory.load(self._cpus[proc_id]._registries[Cpu.REG_D], by_cpu=False), self.numeric_format.format))
        except (FaultError, KeyError):
            self._cpu_display["IND_D"].set("ERR")

        try:
            self._cpu_display["IND_SP"].set(format(
                self._memory.load(self._cpus[proc_id]._registries[Cpu.REG_SP], by_cpu=False), self.numeric_format.format))
        except (FaultError, KeyError):
            self._cpu_display["IND_SP"].set("ERR")

        try:
            self._cpu_display["IND_IP"].set(format(
                self._memory.load(self._cpus[proc_id]._instruction_pointer, by_cpu=False), self.numeric_format.format))
        except FaultError:
            self._cpu_display["IND_IP"].set("ERR")

        self._cpu_display["ZERO"].set(str(self._cpus[proc_id].get_flag("ZERO")))
        self._cpu_display["CARRY"].set(str(self._cpus[proc_id].get_flag("CARRY")))
        self._cpu_display["FAULT"].set(str(self._cpus[proc_id].get_flag("FAULT")))

    def show_error(self, message: str, cpu=0):
        if cpu != 0:
            raise IndexError(f"Unable to display error for cpu {cpu}")
        self._error_message.set(message)

    def get_default_program(self):
        return \
        """            ; Simple example
            ; Writes Hello World to the output
            
                    JMP start
            hello:  DB "Hello World!"   ; Variable
                    DB 0                ; String terminator
            start:
                    MOV C, hello        ; Point to var 
                    MOV D, 0            ; Point to output
                    CALL 0x08           ; Call ROM string print
                                        ; NOTE: ROM int print at 0x0A 
                    HLT                 ; Stop execution"""

    def load_rom(self):
        """# load ROM"""
        program = self._assemble.assemble("""
            ; static jump table: one entry per cpu
            ; 0x68 words of memory per program 
                JMP 0x0080
                JMP 0x00E8
                JMP 0x0150
                JMP 0x01B8
                JMP print
                JMP PRINT_NUMBER
                HLT
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
    ; input B number to display
    ; input D screen position
    ; return D last screen position
        BASE:		DB 10
    ; A quotient
    ; B input number
    ; C reminder
    ; D input position
        PRINT_NUMBER:
        .loop2:		
                PUSH C
                MOV A, B		; B / 10 -> A - calculate quotient
                DIV [BASE]
                MUL [BASE]		; A * 10 -> A
                SUB B, A		; B - A -> C	- calculate rest - to be printed in reverse order
                MOV C, B
                DIV [BASE]		; A / 10 -> B
                MOV B, A
                CMP B, 0		; Is reminder zero?
                JE .L1		; yes, don't display it
                CALL .loop2		; recursive call
                
    ; print numbers in C from stack
        .L1:		ADD C, 48		; ASCII of character zero
                OUT [D], C		; print char at D
                INC D
                POP C
                RET
        """, base_address=0x00)
        self._memory.mass_store(self._memory.rom_base, program["code"], can_write_rom=True)


class Windows2Panes(MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(4, *args, **kwargs)

        # set view
        self.hide_all_errors()

        # set model
        self._player_code = [None] * self._nb_cpu

    def is_player_file_loaded(self, player_no: int):
        assert player_no in range(1, self._nb_cpu + 1), "Player number out of range"
        return self._players[player_no - 1]["name"]["text"] != _("Player {}").format(player_no)

    def set_player_label(self, player_no, filename):
        assert player_no in range(1, self._nb_cpu + 1), "Player number out of range"

        if len(filename) > 0:
            filename = os.path.basename(filename)           # remove path
            filename = os.path.splitext(filename)[0]        # remove extension
            filename = f": [{filename}]"
        self._players[player_no - 1]["name"].configure(text=_("Player {}{}")
                                                       .format(player_no, filename))

    def do_load_player(self, player_no: int):
        assert player_no in range(1, self._nb_cpu + 1), "Player number out of range"

        filename, code = self.load()
        self._player_code = code
        self.set_player_label(player_no, filename)
        self.load_program_for_cpu(player_no-1, code, single_user = True)
        self.refresh()

    def load_button_clicked(self):
        if self._tabs.index('current') == 0:
            super().load_button_clicked()
        else:
            # get free slots
            free_players = []
            for i in range(self._nb_cpu):
                if not self.is_player_file_loaded(i + 1):
                    free_players.append(i + 1)

            if len(free_players) == 0:
                messagebox.showerror(message = _("No free slot to add a player. Click 'Erase' to remove a player."),
                                     icon="error")
                return
            # select player slot
            selected_player = free_players[int(random.random() * len(free_players))]

            # load code
            self.do_load_player(selected_player)

    def on_tab_selected(self, event):
        self.refresh()

    def run_button_clicked(self, cpu_ids=[0]):
        if self._tabs.index('current') == 0:
            super().run_button_clicked()
        else:
            self.hide_all_errors()
            self.play_run_btn.configure(text=_("STOP"), command=self.stop_button_clicked)
            if self._tabs.index('current') == 0:
                super().run_button_clicked(cpu_ids)
            else:
                cpu_ids =[]
                for i in range(self._nb_cpu):
                    if self.is_player_file_loaded(i + 1):
                        cpu_ids.append(i)
                super().run_button_clicked(cpu_ids)

    def receive_running(self, event: tkinter.Event):
        is_running = bool(event.x)  # hack since data field not implemented in python
        if is_running:
            self.refresh()
        else:
            self.play_run_btn.configure(text=_(">>Run"), command=self.run_button_clicked)
            super().receive_running(event)

    def step_button_clicked(self):
        if self._tabs.index('current') == 0:
            super().step_button_clicked()
        else:
            self.hide_all_errors()
            for i in range(self._nb_cpu):
                if self.is_player_file_loaded(i + 1):
                    try:
                        if self._cpus[i].step():
                            self.refresh()
                        else:
                            raise FaultError(_("CPU Halted"))
                    except (FaultError, ValueError) as error:
                        self.show_error(str(error), i)

    def reset_button_clicked(self):
        super().reset_button_clicked()
        if self._tabs.index('current') == 0:
            return
        self.hide_all_errors()
        self._memory.reset()
        for player_no in range(1, self._nb_cpu + 1):
            self.set_player_label(player_no, "")
        self.refresh()

    def erase_1_button_clicked(self):
        self.set_player_label(1, "")
        self.show_error("", 0)

    def erase_2_button_clicked(self):
        self.set_player_label(2, "")
        self.show_error("", 1)

    def erase_3_button_clicked(self):
        self.set_player_label(3, "")
        self.show_error("", 2)

    def erase_4_button_clicked(self):
        self.set_player_label(4, "")
        self.show_error("", 3)

    def show_error(self, message, cpu_id=0):
        if cpu_id == 0:
            super().show_error(message)
        try:
            self._players[cpu_id]["error"].config(text=message)
        except IndexError:
            pass

    def hide_all_errors(self):
        for i in range(self._nb_cpu):
            self.show_error("", i)

    def refresh(self):
        if self._tabs.index('current') == 0:
            super().refresh()
        else:
            self.refresh_memory()
            self.refresh_screen()
            self.refresh_scores()

    def refresh_memory(self):
        if self._tabs.index('current') == 0:
            super().refresh_memory()
        else:
            self.set_memory_display(self._textEditor_memory_play,
                                    nb_cpu_to_display=self._nb_cpu,
                                    use_default_cpu_colors=False)

    def refresh_screen(self):
        if self._tabs.index('current') == 0:
            super().refresh_screen()
        else:
            self.set_screen_display(self._textEditor_screen_play)

    def _get_score(self, cpu_id):
        score = 0
        for add in range(len(self._memory)):
            if self._memory.owner(add) == cpu_id:
                score += 1

        for add in range(len(self._screen)):
            if self._screen.owner(add) == cpu_id:
                score += 1
        return score

    def refresh_scores(self):
        for i in range(self._nb_cpu):
            self._players[i]["score"].set(str(self._get_score(i)))


def main():
    logging.basicConfig(level=logging.DEBUG)
    root = Windows2Panes(sys.argv)
    root.mainloop()


if __name__ == "__main__":
    main()
