#!/usr/bin/env python

import sys
import Tkinter
import tkMessageBox


def warn(message):
    window = Tkinter.Tk()
    window.wm_withdraw()
    tkMessageBox.showwarning('Error!', message)
    sys.exit()

def error(message):
    window = Tkinter.Tk()
    window.wm_withdraw()
    tkMessageBox.showerror('Error!', message)
    sys.exit()
    
    