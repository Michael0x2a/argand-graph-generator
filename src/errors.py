#!/usr/bin/env python

import sys
from datetime import datetime

import Tkinter
import tkMessageBox

__version__ = "3.0"


def warn(message):
    window = Tkinter.Tk()
    window.wm_withdraw()
    tkMessageBox.showwarning('Error!', message)
    log(message)
    sys.exit()

def error(message):
    window = Tkinter.Tk()
    window.wm_withdraw()
    tkMessageBox.showerror('Error!', message)
    log(message)
    sys.exit()
    
def log(message):
    with open('log.txt', 'a') as log:
        text = '\n'.join([
            str(datetime.now()) + ':',
            '',
            'Metadata:',
            '    graph_gen version: ' + __version__,
            '',
            'Message:',
            message,
            '',
            'END LOG',
            ''])
        log.write(text)
        