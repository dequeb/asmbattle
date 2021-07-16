# /usr/bin/python3
# -*- coding: UTF-8 -*-
from tkinter import *
from tk_html_widgets import HTMLScrolledText
import webbrowser
import markdown2 as markdown
from asmbattle.files import *

# Set up message catalog access
t = get_translation('aboutbox')
t.install()
_ = t.gettext


class AboutBox(Toplevel):
    VERSION= open(get_root_filename('VERSION'), 'r').read()
    count = 0

    def __init__(self, parent):
        if AboutBox.count > 0:
            return
        else:
            AboutBox.count +=1

        Toplevel.__init__(self, parent)
        self.minsize(600, 300)
        # self.maxsize(500, 300)

        self.title(_("about..."))
        self["bg"]="white"
        link1=Label(self, text=_("If you like this program, buy me pizza !"),
                    underline=-1, fg="blue", cursor="hand2")
        link1.pack(side=TOP, expand=FALSE)

        top_frame = Frame(self, bg="white")
        top_frame.pack(side=TOP, fill=X, expand=TRUE)

        # image
        canvas = Canvas(top_frame)
        canvas.pack(side=LEFT, fill='both', expand='yes')

        try:
            self.img = PhotoImage(file= get_icon_filename("icon_256x256.png"))
            canvas.create_image(1, 1, image=self.img, anchor=NW)
        except TclError:
            pass

        # text
        right_top_frame = Frame(top_frame, bg="white")
        # right_top_frame["bg"]="white"
        right_top_frame.pack(side=RIGHT, fill=X, expand=TRUE)
        Label(right_top_frame, text="ASM Battle", padx=20, pady=20, font=("", 25)).pack(side=TOP, fill=X, expand='yes')
        Label(right_top_frame, text=_(f"Version: {AboutBox.VERSION}")).pack(side=TOP, fill=X, expand='yes')
        Message(right_top_frame, text=_("""
        An original idea of Michel Rondeau (https://www.michelrondeau.com/asmbattle) based on prior work """
        """by Marco Schweighauser (https://schweigi.github.io/assembler-simulator/)"""), padx=20, pady=20).pack(side=TOP, fill=X, expand='yes')

        Button(self, text=_("   Ok   "), command=self.do_close, bg="systemButtonFace").pack(ipadx= 20, ipady=20, padx=5, pady=5, anchor=S)


        html = markdown.markdown(open( get_root_filename(_("README.md")), "r").read())
        st = HTMLScrolledText(self, padx=20, pady=20, height=13, relief=GROOVE, wrap=WORD, html=html)
        st.pack(side=TOP, fill=BOTH, expand='yes')

        html = markdown.markdown(open(get_root_filename(_("LICENCE.txt")), "r").read())
        st = HTMLScrolledText(self, padx=20, pady=20, height=13, relief=GROOVE, wrap=WORD, html=html)
        st.pack(side=TOP, fill=BOTH, expand='yes')

        html = markdown.markdown(open(get_root_filename(_("CHANGELOG.md")), "r").read())
        st = HTMLScrolledText(self, padx=20, pady=20, height=13, relief=GROOVE, wrap=WORD, html=html)
        st.pack(side=TOP, fill=BOTH, expand='yes')

        # dialog box behavior
        self.focus_force()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def do_close(self):
        self.destroy()

    def __del__(self):
        AboutBox.count -= 1

class HelpBox(Toplevel):
    count = 0

    def __init__(self, parent):
        if HelpBox.count > 0:
            return
        else:
            HelpBox.count += 1
        Toplevel.__init__(self, parent)
        self.minsize(600, 300)

        self.title(_("help..."))
        self["bg"]="white"
        Label(self, text=_("See original documentation at: ")).pack(side=TOP, fill=X, expand='yes')

        link1=Label(self, text="https://schweigi.github.io/assembler-simulator/instruction-set.html",
                    underline=-1, fg="blue", cursor="hand2")
        link1.pack()
        link1.bind("<Button-1>", lambda e: webbrowser.open("https://schweigi.github.io/assembler-simulator/instruction-set.html"))

        html = markdown.markdown( _(""" 
#Extension#

##IO Instructions##

Read or write from an IO port. The current implementation uses these instruction to read or write to screen. 
The range of valid port depends on hardware attached to CPU.         


    IN port, reg
    IN reg, reg
    OUT port, reg
    OUT reg, reg"""))
        st = HTMLScrolledText(self, padx=20, pady=20, height=13, relief=GROOVE, wrap=WORD, html=html)
        st.pack(side=TOP, fill=BOTH, expand='yes')

    def __del__(self):
        HelpBox.count -= 1

def main():
    root = Tk()
    AboutBox(root)
    HelpBox(root)
    root.mainloop()

if __name__ == "__main__":
    main()