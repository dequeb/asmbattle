# /usr/bin/python3
# -*- coding: UTF-8 -*-
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import scrolledtext
from asmbattle.aboutbox import AboutBox, HelpBox
import os
import gettext
import webbrowser


PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(PROGRAM_DIR + "/..")
RESOURCE_DIR = ROOT_DIR + "/resources"
ICON_DIR = ROOT_DIR + "/resources/icons"
LOCALE_DIR = ROOT_DIR + "/locale"

# Set up message catalog access
t = gettext.translation('ui_view', LOCALE_DIR, fallback=True)
t.install()
_ = t.gettext


# class FancyListbox(tkinter.Listbox):
#     def __init__(self, parent, *args, **kwargs):
#         tkinter.Listbox.__init__(self, parent, *args, **kwargs)
#
#         self.popup_menu = tkinter.Menu(self, tearoff=0)
#         self.popup_menu.add_command(label="Cut",
#                                     command=self.cut_selected)
#         self.popup_menu.add_command(label="Copy",
#                                     command=self.copy_selected)
#         self.popup_menu.add_command(label="Paste",
#                                     command=self.paste)
#         self.popup_menu.add_command(label="Select All",
#                                     command=self.select_all)
#         self.popup_menu.add_command(label="Delete",
#                                     command=self.delete_selected)
#         self.parent = parent
#         self.parent.bind("<Button-2>", self.popup) # Button-2 on Aqua
#
#
#     def popup(self, event):
#         try:
#             self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
#         finally:
#             self.popup_menu.grab_release()
#
#     def copy_selected(self):
#         for i in self.parent.curselection()[::-1]:
#             self.clipboard_clear()
#             self.clipboard_append( self.parent.selection_get())
#
#     def cut_selected(self):
#         for i in self.parent.curselection()[::-1]:
#             pass #            self.delete(i)
#
#     def paste(self):
#         pass # self.selection_set(0, 'end')
#
#
#     def delete_selected(self):
#         for i in self.curselection()[::-1]:
#             self.parent.delete(i)
#
#     def select_all(self):
#         self.parent.selection_set(0, 'end')

class BaseWindow(Tk):
    IP_COLOR = "#9EA5FF"
    SP_COLOR = "#FFA17B"

    PLAYER1_COLOR = "#6981B6"
    PLAYER2_COLOR = "#71D282"
    PLAYER3_COLOR = "#D53140"
    PLAYER4_COLOR = "#DFD941"

    LAST_ACCESS_COLOR = "#A8EFB6"

    def __init__(self, title="", *args, **kwargs):
        Tk.__init__(self)

        self.geometry("1200x900")
        self.title(title)
        self._font = font.Font(family = "Courier New", size = 14)

        self._speed_hz = IntVar(self, 2)
        self._display_hexadecimal = BooleanVar(self, True)

        ## prepare frame
        self._tabs, self._prepare_frame, self._play_frame = self.build_tabs(self)
        self.add_prepare_toolbar(self._prepare_frame)
        self._error_message = self._error_var = self.add_error(self._prepare_frame)
        self._cpu_display= self.add_cpu(self._prepare_frame)

        # vertical splitter
        pw = ttk.PanedWindow(self._prepare_frame, orient=VERTICAL)
        pw.pack(fill=BOTH, anchor=N, expand=TRUE)
        prepare_frame_up = ttk.Frame(pw, relief=SUNKEN)
        prepare_frame_down = ttk.Frame(pw, relief=SUNKEN)
        pw.add(prepare_frame_up, weight=15)
        pw.add(prepare_frame_down, weight=1)

        self._textEditor_code = self.add_code(prepare_frame_up)

        # vertical splitter
        pw = ttk.PanedWindow(prepare_frame_down, orient=VERTICAL)
        pw.pack(fill=BOTH, anchor=N, expand=TRUE)
        prepare_frame_memory = ttk.Frame(pw, relief=SUNKEN)
        prepare_frame_screen = ttk.Frame(pw, relief=SUNKEN)
        pw.add(prepare_frame_memory, weight=5)
        pw.add(prepare_frame_screen, weight=1)

        self._textEditor_memory = self.add_memory(prepare_frame_memory)
        self._textEditor_screen = self.add_screen(prepare_frame_screen)

        ## play frame
        self.add_play_toolbar(self._play_frame)
        self._players = self.add_players(self._play_frame)
        # vertical spliter
        pw = ttk.PanedWindow(self._play_frame, orient=VERTICAL)
        pw.pack(fill=BOTH, anchor=N, expand=TRUE)
        play_frame_memory = ttk.Frame(pw, relief=SUNKEN)
        play_frame_screen = ttk.Frame(pw, relief=SUNKEN)
        pw.add(play_frame_memory, weight=5)
        pw.add(play_frame_screen, weight=3)

        self._textEditor_memory_play = self.add_memory(play_frame_memory)
        self._textEditor_screen_play = self.add_screen(play_frame_screen)

        self.update()
        # now root.geometry() returns valid size/placement
        self.minsize(self.winfo_width(), self.winfo_height())
        self.add_menus()

        self.toplevel_help = None
        self.toplevel_about = None


    def add_menus(self):
        if os.name == "posix":
            cmd_prefix = "Cmd+"
        else:
            cmd_prefix = "Ctrl+"

        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label=_("New"),  underline=0, command=self.do_file_new  , accelerator=cmd_prefix+"N")
        filemenu.add_command(label=_("Open"),  underline=0, command=self.do_file_open , accelerator=cmd_prefix+"O")
        filemenu.add_command(label=_("Save"),  underline=0, command=self.do_file_save, accelerator=cmd_prefix+"S")
        self.bind_all("<Command-N>", self.do_file_new)
        self.bind_all("<Command-O>", self.do_file_open)
        self.bind_all("<Command-S>", self.do_file_save)

        filemenu.add_separator()

        filemenu.add_command(label=_("Quit"),  underline=0, command=self.do_file_quit, accelerator=cmd_prefix+"Q")
        menubar.add_cascade(label=_("File"), underline=0, menu=filemenu)
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label=_("Undo"),  underline=0, accelerator=cmd_prefix+"Z",
                             command=lambda: self.event_generate("<<Undo>>"))

        editmenu.add_separator()

        editmenu.add_command(label=_("Cut"),  underline=1, accelerator=cmd_prefix+"X",
                             command=lambda: self._textEditor_code.event_generate("<<Cut>>"))
        editmenu.add_command(label=_("Copy"),  underline=0, accelerator=cmd_prefix+"C",
                             command=lambda: self._textEditor_code.event_generate("<<Copy>>"))
        editmenu.add_command(label=_("Paste"),  underline=0, accelerator=cmd_prefix+"V",
                             command=lambda: self._textEditor_code.event_generate("<<Paste>>"))
        editmenu.add_command(label=_("Select All"), underline=7,  accelerator=cmd_prefix+"A",
                             command=lambda: self._textEditor_code.event_generate("<<SelectAll>>"))

        menubar.add_cascade(label=_("Edit"),  underline=0, menu=editmenu)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label=_("Help..."),  underline=0, command=self.do_help_index, accelerator="F1")
        helpmenu.add_command(label=_("About..."),  underline=0, command=self.do_help_about)
        menubar.add_cascade(label=_("Help"),  underline=0, menu=helpmenu)
        self.config(menu=menubar)

    def build_tabs(self, frame):
        """Tab Widget"""
        tabs = ttk.Notebook(frame)
        tabs.pack(fill=BOTH, expand=FALSE)
        tabs.bind("<<NotebookTabChanged>>", self.on_tab_selected)
        prepare_frame = ttk.Frame(tabs, name="prepare")
        play_frame = ttk.Frame(tabs, name="play")
        tabs.add(prepare_frame, text=_("Prepare"))
        tabs.add(play_frame, text=_("Play"))
        return (tabs, prepare_frame, play_frame)

    def add_prepare_toolbar(self, frame):
        tb_frame = ttk.Frame(frame,  relief=tkinter.GROOVE)
        tb_frame.pack(side=tkinter.TOP, anchor=N, fill=X, expand=FALSE)

        # creating buttons
        btn = Button(tb_frame, text=_("Load..."), command=self.load_button_clicked, bg="systemButtonFace")
        btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        btn = Button(tb_frame, text=_("Save..."), command=self.save_button_clicked, bg="systemButtonFace")
        btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        btn = Button(tb_frame, text=_("Assemble"), command=self.assemble_button_clicked, bg="systemButtonFace")
        btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        self.run_btn = Button(tb_frame, text=_(">>Run"), command=self.run_button_clicked, bg="systemButtonFace")
        self.run_btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        btn = Button(tb_frame, text=_(">Step"), command=self.step_button_clicked, bg="systemButtonFace")
        btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        btn = Button(tb_frame, text=_("Reset"), command=self.reset_button_clicked, bg="systemButtonFace")
        btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        sep = ttk.Separator(tb_frame)
        sep.pack(padx=15, pady=5, side=tkinter.LEFT)

        # creating speed spinbox
        lbl = Label(tb_frame, text=_("Speed (Hz): "), justify=RIGHT, bg="systemButtonFace")
        lbl.pack(padx=1, pady=5, side=tkinter.LEFT)
        sbox = Spinbox(tb_frame, values=(1,2, 4,8,16,32,64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000),
                       width=5, state="readonly",
                       textvariable=self._speed_hz, command=self.speed_hz_changed)
        sbox.pack(padx=1, pady=5, side=tkinter.LEFT)

        # creating display radio buttons
        rbtn = Radiobutton(tb_frame, text=_("Hexadecimal"), variable=self._display_hexadecimal,
                           value=True, command=self.numeric_format_changed)
        rbtn.pack(padx=2, pady=5, side=tkinter.RIGHT)
        rbtn = Radiobutton(tb_frame, text=_("Decimal"), variable=self._display_hexadecimal,
                           value=False, command=self.numeric_format_changed)
        rbtn.pack(padx=2, pady=5, side=tkinter.RIGHT)
        lbl = Label(tb_frame, text=_("Display: "), justify=RIGHT, bg="systemButtonFace")
        lbl.pack(padx=1, pady=5, side=tkinter.RIGHT)
        sep = ttk.Separator(tb_frame)
        sep.pack(padx=15, pady=5, side=tkinter.RIGHT)

    def add_play_toolbar(self, frame):
        tb_frame = ttk.Frame(frame,  relief=tkinter.GROOVE)
        tb_frame.pack(side=tkinter.TOP, anchor=N, fill=X, expand=FALSE)

        # creating buttons
        btn = Button(tb_frame, text=_("Load..."), command=self.load_button_clicked, bg="systemButtonFace")
        btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        self.play_run_btn = Button(tb_frame, text=_(">>Run"), command=self.run_button_clicked, bg="systemButtonFace")
        self.play_run_btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        btn = Button(tb_frame, text=_(">Step"), command=self.step_button_clicked, bg="systemButtonFace")
        btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        btn = Button(tb_frame, text=_("Reset"), command=self.reset_button_clicked, bg="systemButtonFace")
        btn.pack(padx=5, pady=5, side=tkinter.LEFT)
        sep = ttk.Separator(tb_frame)
        sep.pack(padx=15, pady=5, side=tkinter.LEFT)

        # creating speed spinbox
        lbl = Label(tb_frame, text=_("Speed (Hz): "), justify=RIGHT, bg="systemButtonFace")
        lbl.pack(padx=1, pady=5, side=tkinter.LEFT)
        sbox = Spinbox(tb_frame, values=(1, 2, 4, 8, 16, 32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000 ),
                       width=5, state="readonly",
                       textvariable=self._speed_hz, command=self.speed_hz_changed)
        sbox.pack(padx=1, pady=5, side=tkinter.LEFT)

        # creating display radio buttons
        rbtn = Radiobutton(tb_frame, text=_("Hexadecimal"), variable=self._display_hexadecimal,
                           value=True, command=self.numeric_format_changed)
        rbtn.pack(padx=2, pady=5, side=tkinter.RIGHT)
        rbtn = Radiobutton(tb_frame, text=_("Decimal"), variable=self._display_hexadecimal,
                           value=False, command=self.numeric_format_changed)
        rbtn.pack(padx=2, pady=5, side=tkinter.RIGHT)
        lbl = Label(tb_frame, text=_("Display: "), justify=RIGHT, bg="systemButtonFace")
        lbl.pack(padx=1, pady=5, side=tkinter.RIGHT)
        sep = ttk.Separator(tb_frame)
        sep.pack(padx=15, pady=5, side=tkinter.RIGHT)

    def add_error(self, frame) -> StringVar:
        link1=Label(frame, text=_("To support me with this project, buy me pizza !"),
                    underline=-1, fg="blue", cursor="hand2")
        link1.pack(side=TOP, expand=FALSE)
        link1.bind("<Button-1>", lambda e: webbrowser.open("https://www.buymeacoffee.com/michelrondeau"))

        # create a StringVar class
        error_message = StringVar()
        error_message.set(_("error"))
        lbl = Label(frame, textvariable = error_message, fg="red", justify=LEFT, anchor='w', bg="systemButtonFace")
        lbl.pack(padx=5, pady=5, side=TOP, fill=X, expand=FALSE)
        return error_message

    def add_code(self, frame):
        # defining code editor
        lbl = Label(frame, text=_("Code"), bg="systemButtonFace")
        lbl.pack(padx=5, pady=5, side=TOP, fill=BOTH, expand=FALSE)
        text_editor_code = scrolledtext.ScrolledText(frame, name="text_code", wrap=NONE,
                                     font=self._font, undo=True)
        text_editor_code.pack(padx=5, pady=5, side=TOP, fill=BOTH, expand=True)
        text_editor_code.insert(END, "code")
        text_editor_code.bind("<Key>", self.code_modified)

        # flb = FancyListbox(text_editor_code)  - not working yet...

        return text_editor_code

    def add_screen(self, frame):
        # defining screen viewer
        lbl = Label(frame, text=_("Screen"), bg='SystemButtonFace')

        lbl.pack(padx=5, pady=5, side=TOP, fill=X, expand=FALSE)
        text_editor_screen = scrolledtext.ScrolledText(frame, name="text_screen", wrap=NONE,
                                       font=self._font, height=5)
        text_editor_screen.pack(padx=5, pady=5, side=TOP, fill=BOTH, expand=True)
        text_editor_screen.insert(END, _("screen"))
        text_editor_screen.bind("<Key>", lambda e: 'break')
        return text_editor_screen

    def add_memory(self, frame):
        # defining memory viewer
        lbl = Label(frame, text=_("Memory"), bg="systemButtonFace")
        lbl.pack(padx=5, pady=5, side=TOP, fill=X, expand=FALSE)
        text_editor_memory = scrolledtext.ScrolledText(frame, name="text_memory", wrap=NONE,
                                       font=self._font, height=20)
        text_editor_memory.pack(padx=5, pady=5, side=TOP, fill=BOTH, expand=True)
        text_editor_memory.insert(END, "memory")
        text_editor_memory.bind("<Key>", lambda e: "break")
        return text_editor_memory

    def add_cpu(self, frame) -> dict:
        fields={}

        lbl = Label(frame, text=_("CPU"), bg="systemButtonFace")
        lbl.pack(padx=5, pady=5, side=TOP, fill=X, expand=FALSE)
        cpu_frame = ttk.Frame(frame, relief=tkinter.GROOVE)
        cpu_frame.pack(side=tkinter.TOP, fill=BOTH, expand=FALSE)

        # labels
        lbl = Label(cpu_frame, text="A", bg="systemButtonFace")
        lbl.grid(sticky=N, column=0, row=0, padx=5, pady=5)
        lbl = Label(cpu_frame, text="B", bg="systemButtonFace")
        lbl.grid(sticky=N, column=1, row=0, padx=5, pady=5)
        lbl = Label(cpu_frame, text="C", bg="systemButtonFace")
        lbl.grid(sticky=N, column=2, row=0, padx=5, pady=5)
        lbl = Label(cpu_frame, text="D", bg="systemButtonFace")
        lbl.grid(sticky=N, column=3, row=0, padx=5, pady=5)
        lbl = Label(cpu_frame, text="IP", bg="systemButtonFace")
        lbl.grid(sticky=N, column=4, row=0, padx=5, pady=5)
        lbl = Label(cpu_frame, text="SP", bg="systemButtonFace")
        lbl.grid(sticky=N, column=5, row=0, padx=5, pady=5)
        lbl = Label(cpu_frame, text="Zero", bg="systemButtonFace")
        lbl.grid(sticky=N, column=6, row=0, padx=5, pady=5)
        lbl = Label(cpu_frame, text="Carry", bg="systemButtonFace")
        lbl.grid(sticky=N, column=7, row=0, padx=5, pady=5)
        lbl = Label(cpu_frame, text="Fault", bg="systemButtonFace")
        lbl.grid(sticky=N, column=8, row=0, padx=5, pady=5)

        # registers and flags
        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.bind("<Key>", lambda e: "break")
        entry.grid(sticky=W, column=0, row=1, padx=5, pady=5)
        fields["REG_A"] = entryText

        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.bind("<Key>", lambda e: "break")
        entry.grid(sticky=W, column=1, row=1, padx=5, pady=5)
        fields["REG_B"] = entryText

        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.grid(sticky=W, column=2, row=1, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["REG_C"] = entryText

        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.grid(sticky=W, column=3, row=1, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["REG_D"] = entryText

        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText, bg=BaseWindow.IP_COLOR)
        entry.bind("<Key>", lambda e: "break")
        entry.grid(sticky=W, column=4, row=1, padx=5, pady=5)
        fields["REG_IP"] = entryText

        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText, bg=BaseWindow.SP_COLOR)
        entry.grid(sticky=W, column=5, row=1, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["REG_SP"] = entryText

        entryText = StringVar(); entryText.set("True")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.grid(sticky=W, column=6, row=1, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["ZERO"] = entryText

        entryText = StringVar(); entryText.set("True")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.grid(sticky=W, column=7, row=1, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["CARRY"] = entryText

        entryText = StringVar(); entryText.set("True")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.grid(sticky=W, column=8, row=1, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["FAULT"] = entryText

        # indirect registers
        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5,font=self._font, textvariable=entryText)
        entry.grid(sticky=W, column=0, row=2, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")

        fields["IND_A"] = entryText
        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.grid(sticky=W, column=1, row=2, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["IND_B"] = entryText

        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.grid(sticky=W, column=2, row=2, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["IND_C"] = entryText

        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText)
        entry.grid(sticky=W, column=3, row=2, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["IND_D"] = entryText

        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText, bg=BaseWindow.IP_COLOR)
        entry.grid(sticky=W, column=4, row=2, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["IND_IP"] = entryText

        entryText = StringVar(); entryText.set("0")
        entry = Entry(cpu_frame, width=5, font=self._font, textvariable=entryText, bg=BaseWindow.SP_COLOR)
        entry.grid(sticky=W, column=5, row=2, padx=5, pady=5)
        entry.bind("<Key>", lambda e: "break")
        fields["IND_SP"] = entryText

        return fields

    def add_players(self, frame) -> []:
        players_frame = ttk.Frame(frame,  relief=tkinter.GROOVE)
        players_frame.pack(side=tkinter.TOP, fill=X, expand=FALSE)
        players= []

        players.append(self.add_player(players_frame, 1, BaseWindow.PLAYER1_COLOR))
        players.append(self.add_player(players_frame, 2, BaseWindow.PLAYER2_COLOR))
        players.append(self.add_player(players_frame, 3, BaseWindow.PLAYER3_COLOR))
        players.append(self.add_player(players_frame, 4, BaseWindow.PLAYER4_COLOR))

        return players


    def add_player(self, frame, player_no:int, color: str):
        assert player_no in range(1, 1 + player_no)

        player_frame = ttk.Frame(frame,  relief=tkinter.GROOVE)
        player_frame.pack(side=tkinter.LEFT, fill=X, expand=FALSE)

        lbl_player = Label(player_frame, text=_("Player ") + str(player_no), bg="systemButtonFace", fg=color)
        lbl_player.grid(sticky=W, column=0, row=0, padx=5, pady=5)
        btn = Button(player_frame, text=_("Erase"), command=getattr(self, f"erase_{player_no}_button_clicked"), bg="systemButtonFace")
        btn.grid(sticky=E, column=1, row=0, padx=5, pady=5)
        lbl_error = Label(player_frame, text=_("Error"), fg="red", width=30, justify=LEFT, anchor='w', bg="systemButtonFace")
        lbl_error.grid(sticky=W, column=0, row=1, padx=5, pady=5, columnspan=2)

        entryText = StringVar(); entryText.set("0")
        entry = Entry(player_frame, width=5, font=self._font, textvariable=entryText, bg=color)
        entry.grid(sticky=W, column=0, row=2, padx=5, pady=5, columnspan=2)
        entry.bind("<Key>", lambda e: "break")
        return {"name": lbl_player, "error":lbl_error, "score" :entryText}

    def code_modified(self, event):
        if event.keysym in "Up/Left/Down/Right":
            return False
        else:
            return True

    def on_tab_selected(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        print("tab changed: " + tab_text)
        return tab_text

    def load_button_clicked(self):
        print("load clicked")

    def save_button_clicked(self):
        print("save clicked")

    def erase_1_button_clicked(self):
        print("erase 1 clicked")

    def erase_2_button_clicked(self):
        print("erase 2 clicked")

    def erase_3_button_clicked(self):
        print("erase 3 clicked")

    def erase_4_button_clicked(self):
        print("erase 4 clicked")

    def assemble_button_clicked(self):
        print("assemble clicked")

    def run_button_clicked(self):
        print("run clicked")

    def step_button_clicked(self):
        print("step clicked")

    def reset_button_clicked(self):
        print("reset clicked")

    def speed_hz_changed(self):
        print(f"speed: {self._speed_hz.get()}")

    def numeric_format_changed(self):
        print(f"display hex: {self._display_hexadecimal.get()}")

    def do_file_new(self):
        print("menu")

    def do_file_open(self):
        print("menu")

    def do_file_save(self):
        print("menu")

    def do_file_quit(self):
        self.quit()

    def do_help_index(self):
        if self.toplevel_help == None:
            self.toplevel_help = HelpBox(self)

    def do_help_about(self):

        self.toplevel_about = AboutBox(self)

def main():
    root = BaseWindow(title="UI View")
    root.mainloop()

if __name__ == "__main__":
    main()