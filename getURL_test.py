# -*- coding: utf-8 -*-
'''
-------------------------------------------------------------------------------
Filename   : xxx.py
Date       : 2013-03-xx
Author     : Joe Lotz
Description: 
-------------------------------------------------------------------------------
'''


import win32gui
import win32con

def getWindowText(hwnd):
    buf_size = 1 + win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
    buf = win32gui.PyMakeBuffer(buf_size)
    win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, buf_size, buf)
    return str(buf)
    
hwnd = win32gui.GetForegroundWindow()
omniboxHwnd = win32gui.FindWindowEx(hwnd, 0, 'Chrome_OmniboxView', None)

print omniboxHwnd