#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
#

import sys
import configparser
import time
import threading
import os

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

from tkinter import *
from ea_psu_controller import PsuEA
import eagui_support

SETV_BUTTON_X =             0.585
SETV_BUTTON_Y =             0.205
SETA_BUTTON_X =             0.585
SETA_BUTTON_Y =             0.305
ON_BUTTON_X =               0.2
ON_BUTTON_Y =               0.6
OFF_BUTTON_X =              0.5
OFF_BUTTON_Y =              0.6
REMOTE_ON_BUTTON_X =        0.2
REMOTE_ON_BUTTON_Y =        0.7
REMOTE_OFF_BUTTON_X =       0.5
REMOTE_OFF_BUTTON_Y =       0.7
LABEL_VOLT_X =              0.7
LABEL_VOLT_Y =              0.01
VOLT_VAL_X =                0.11
VOLT_VAL_Y =                0.015

LABEL_CURRENT_X =           0.7
LABEL_CURRENT_Y =           0.11
CURRENT_VAL_X =             0.11
CURRENT_VAL_Y =             0.11
LABEL_STATUS_X =            0.01
LABEL_STATUS_Y =            0.94
LABEL_CONNECTION_STATUS_X = 0.65
LABEL_CONNECTION_STATUS_Y = 0.94
SET_VOLT_TEXTBOX_X =        0.1
SET_VOLT_TEXTBOX_Y =        0.2
SET_CURRENT_TEXTBOX_X =     0.1
SET_CURRENT_TEXTBOX_Y =     0.3
SET_OVP_TEXTBOX_X =     0.1
SET_OVP_TEXTBOX_Y =     0.4
SET_OCP_TEXTBOX_X =     0.1
SET_OCP_TEXTBOX_Y =     0.5
SET_OVP_BUTTON_X =     0.5889
SET_OVP_BUTTON_Y =     0.4
SET_OCP_BUTTON_X =     0.5889
SET_OCP_BUTTON_Y =     0.5

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_exit)
    top = psuData (root)
    eagui_support.init(root, top)
    root.mainloop()

w = None

def create_psuData(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_Toplevel1(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    top = psuData (w)
    eagui_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_psuData():
    global w
    w.destroy()
    w = None

def on_exit():
    psuData.destroy_all(psuData)
    root.destroy()

class psuData:
    volt = 0.0
    current = 0.0
    status = True
    powerStatus = False
    connectionStatus = False
    tsk = []

    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.currValue = StringVar()
        self.voltValue = StringVar()

        top.geometry("600x450+719+372")
        top.minsize(250, 350)
        top.maxsize(250, 350)
        top.resizable(0,  0)
        top.title("EA Power Panel")
        top.configure(background="#d9d9d9")

        self.setVoltageButton = tk.Button(top)
        self.setVoltageButton.place(relx=SETV_BUTTON_X, rely=SETV_BUTTON_Y, height=28, width=80)
        self.setVoltageButton.configure(activebackground="#ececec")
        self.setVoltageButton.configure(activeforeground="#000000")
        self.setVoltageButton.configure(background="#d9d9d9")
        self.setVoltageButton.configure(disabledforeground="#a3a3a3")
        self.setVoltageButton.configure(foreground="#000000")
        self.setVoltageButton.configure(highlightbackground="#d9d9d9")
        self.setVoltageButton.configure(highlightcolor="black")
        self.setVoltageButton.configure(pady="0")
        self.setVoltageButton.configure(text='''Set Voltage''')
        self.setVoltageButton.configure(command=self.psu_setVolt)

        self.setCurrentButton = tk.Button(top)
        self.setCurrentButton.place(relx=SETA_BUTTON_X, rely=SETA_BUTTON_Y, height=28, width=80)
        self.setCurrentButton.configure(activebackground="#ececec")
        self.setCurrentButton.configure(activeforeground="#000000")
        self.setCurrentButton.configure(background="#d9d9d9")
        self.setCurrentButton.configure(disabledforeground="#a3a3a3")
        self.setCurrentButton.configure(foreground="#000000")
        self.setCurrentButton.configure(highlightbackground="#d9d9d9")
        self.setCurrentButton.configure(highlightcolor="black")
        self.setCurrentButton.configure(pady="0")
        self.setCurrentButton.configure(text='''Set Current''')
        self.setCurrentButton.configure(command=self.psu_setCurrent)

        self.setOvpButton = tk.Button(top)
        self.setOvpButton.place(relx=SET_OVP_BUTTON_X, rely=SET_OVP_BUTTON_Y, height=28, width=80)
        self.setOvpButton.configure(activebackground="#ececec")
        self.setOvpButton.configure(activeforeground="#000000")
        self.setOvpButton.configure(background="#d9d9d9")
        self.setOvpButton.configure(disabledforeground="#a3a3a3")
        self.setOvpButton.configure(foreground="#000000")
        self.setOvpButton.configure(highlightbackground="#d9d9d9")
        self.setOvpButton.configure(highlightcolor="black")
        self.setOvpButton.configure(pady="0")
        self.setOvpButton.configure(text='''Set OVP''')
        self.setOvpButton.configure(command=self.psu_setOvp)

        self.setOcpButton = tk.Button(top)
        self.setOcpButton.place(relx=SET_OCP_BUTTON_X, rely=SET_OCP_BUTTON_Y, height=28, width=80)
        self.setOcpButton.configure(activebackground="#ececec")
        self.setOcpButton.configure(activeforeground="#000000")
        self.setOcpButton.configure(background="#d9d9d9")
        self.setOcpButton.configure(disabledforeground="#a3a3a3")
        self.setOcpButton.configure(foreground="#000000")
        self.setOcpButton.configure(highlightbackground="#d9d9d9")
        self.setOcpButton.configure(highlightcolor="black")
        self.setOcpButton.configure(pady="0")
        self.setOcpButton.configure(text='''Set OCP''')
        self.setOcpButton.configure(command=self.psu_setOcp)

        self.buttonON = tk.Button(top)
        self.buttonON.place(relx=ON_BUTTON_X, rely=ON_BUTTON_Y, height=28, width=75)
        self.buttonON.configure(activebackground="#ececec")
        self.buttonON.configure(activeforeground="#000000")
        self.buttonON.configure(background="#d9d9d9")
        self.buttonON.configure(disabledforeground="#a3a3a3")
        self.buttonON.configure(foreground="#000000")
        self.buttonON.configure(highlightbackground="#d9d9d9")
        self.buttonON.configure(highlightcolor="black")
        self.buttonON.configure(pady="0")
        self.buttonON.configure(text='''On''')
        self.buttonON.configure(command=self.power_on)

        self.buttonOff = tk.Button(top)
        self.buttonOff.place(relx=OFF_BUTTON_X, rely=OFF_BUTTON_Y, height=28, width=75)
        self.buttonOff.configure(activebackground="#ececec")
        self.buttonOff.configure(activeforeground="#000000")
        self.buttonOff.configure(background="#d9d9d9")
        self.buttonOff.configure(disabledforeground="#a3a3a3")
        self.buttonOff.configure(foreground="#000000")
        self.buttonOff.configure(highlightbackground="#d9d9d9")
        self.buttonOff.configure(highlightcolor="black")
        self.buttonOff.configure(pady="0")
        self.buttonOff.configure(text='''Off''')
        self.buttonOff.configure(command=self.power_off)

        self.buttonRemoteOn = tk.Button(top)
        self.buttonRemoteOn.place(relx=REMOTE_ON_BUTTON_X, rely=REMOTE_ON_BUTTON_Y, height=28, width=75)
        self.buttonRemoteOn.configure(activebackground="#ececec")
        self.buttonRemoteOn.configure(activeforeground="#000000")
        self.buttonRemoteOn.configure(background="#d9d9d9")
        self.buttonRemoteOn.configure(disabledforeground="#a3a3a3")
        self.buttonRemoteOn.configure(foreground="#000000")
        self.buttonRemoteOn.configure(highlightbackground="#d9d9d9")
        self.buttonRemoteOn.configure(highlightcolor="black")
        self.buttonRemoteOn.configure(pady="0")
        self.buttonRemoteOn.configure(text='''Connect''')
        self.buttonRemoteOn.configure(command=self.psu_connect)

        self.buttonRemoteOff = tk.Button(top)
        self.buttonRemoteOff.place(relx=REMOTE_OFF_BUTTON_X, rely=REMOTE_OFF_BUTTON_Y, height=28, width=75)
        self.buttonRemoteOff.configure(activebackground="#ececec")
        self.buttonRemoteOff.configure(activeforeground="#000000")
        self.buttonRemoteOff.configure(background="#d9d9d9")
        self.buttonRemoteOff.configure(disabledforeground="#a3a3a3")
        self.buttonRemoteOff.configure(foreground="#000000")
        self.buttonRemoteOff.configure(highlightbackground="#d9d9d9")
        self.buttonRemoteOff.configure(highlightcolor="black")
        self.buttonRemoteOff.configure(pady="0")
        self.buttonRemoteOff.configure(text='''Disconnect''')
        self.buttonRemoteOff.configure(command=self.psu_disconnect)


        self.labelVolt = tk.Label(top)
        self.labelVolt.place(relx=LABEL_VOLT_X, rely=LABEL_VOLT_Y, height=33, width=37)
        self.labelVolt.configure(background="#d9d9d9")
        self.labelVolt.configure(disabledforeground="#a3a3a3")
        self.labelVolt.configure(foreground="#000000")
        self.labelVolt.configure(font=("Arial", 14))
        self.labelVolt.configure(text='''V''')

        self.labelCurrent = tk.Label(top)
        self.labelCurrent.place(relx=LABEL_CURRENT_X, rely=LABEL_CURRENT_Y, height=33, width=37)
        self.labelCurrent.configure(activebackground="#f9f9f9")
        self.labelCurrent.configure(activeforeground="black")
        self.labelCurrent.configure(background="#d9d9d9")
        self.labelCurrent.configure(disabledforeground="#a3a3a3")
        self.labelCurrent.configure(foreground="#000000")
        self.labelCurrent.configure(highlightbackground="#d9d9d9")
        self.labelCurrent.configure(highlightcolor="black")
        self.labelCurrent.configure(font=("Arial", 14))
        self.labelCurrent.configure(text='''A''')

        self.labelVoltageVal = tk.Label(top)
        self.labelVoltageVal.place(relx=VOLT_VAL_X, rely=VOLT_VAL_Y, height=30, width=100)
        self.labelVoltageVal.configure(activebackground="#f9f9f9")
        self.labelVoltageVal.configure(activeforeground="black")
        self.labelVoltageVal.configure(background="#d9d9d9")
        self.labelVoltageVal.configure(disabledforeground="#a3a3a3")
        self.labelVoltageVal.configure(foreground="#000000")
        self.labelVoltageVal.configure(highlightbackground="#d9d9d9")
        self.labelVoltageVal.configure(highlightcolor="black")
        self.voltValue.set(str(self.volt))
        self.labelVoltageVal.configure(font=("Arial", 14))
        self.labelVoltageVal.configure(textvariable=self.voltValue)

        self.labelCurentVal = tk.Label(top)
        self.labelCurentVal.place(relx=CURRENT_VAL_X, rely=CURRENT_VAL_Y, height=30, width=100)
        self.labelCurentVal.configure(activebackground="#f9f9f9")
        self.labelCurentVal.configure(activeforeground="black")
        self.labelCurentVal.configure(background="#d9d9d9")
        self.labelCurentVal.configure(disabledforeground="#a3a3a3")
        self.labelCurentVal.configure(foreground="#000000")
        self.labelCurentVal.configure(highlightbackground="#d9d9d9")
        self.labelCurentVal.configure(highlightcolor="black")
        self.currValue.set(str(self.current))
        self.labelCurentVal.configure(font=("Arial", 14))
        self.labelCurentVal.configure(textvariable=self.currValue)

        self.labelStatus = tk.Label(top)
        self.labelStatus.place(relx=LABEL_STATUS_X, rely=LABEL_STATUS_Y, height=23, width=100)
        self.labelStatus.configure(activebackground="#f9f9f9")
        self.labelStatus.configure(activeforeground="black")
        self.labelStatus.configure(background="#d9d9d9")
        self.labelStatus.configure(disabledforeground="#a3a3a3")
        self.labelStatus.configure(foreground="#000000")
        self.labelStatus.configure(highlightbackground="#d9d9d9")
        self.labelStatus.configure(highlightcolor="black")
        self.labelStatus.configure(text='''Idle''')

        self.labelConnectionStatus = tk.Label(top)
        self.labelConnectionStatus.place(relx=LABEL_CONNECTION_STATUS_X, rely=LABEL_CONNECTION_STATUS_Y, height=23, width=100)
        self.labelConnectionStatus.configure(activebackground="#f9f9f9")
        self.labelConnectionStatus.configure(activeforeground="black")
        self.labelConnectionStatus.configure(background="#d9d9d9")
        self.labelConnectionStatus.configure(disabledforeground="#a3a3a3")
        self.labelConnectionStatus.configure(foreground="#000000")
        self.labelConnectionStatus.configure(highlightbackground="#d9d9d9")
        self.labelConnectionStatus.configure(highlightcolor="black")
        self.labelConnectionStatus.configure(text='''Idle''')

        self.setVoltage = tk.Text(top)
        self.setVoltage.place(relx=SET_VOLT_TEXTBOX_X, rely=SET_VOLT_TEXTBOX_Y, relheight=0.071, relwidth=0.4)
        self.setVoltage.configure(background="white")
        self.setVoltage.configure(font="TkTextFont")
        self.setVoltage.configure(foreground="black")
        self.setVoltage.configure(highlightbackground="#d9d9d9")
        self.setVoltage.configure(highlightcolor="black")
        self.setVoltage.configure(insertbackground="black")
        self.setVoltage.configure(selectbackground="blue")
        self.setVoltage.configure(selectforeground="white")
        self.setVoltage.configure(wrap="word")

        self.setCurrent = tk.Text(top)
        self.setCurrent.place(relx=SET_CURRENT_TEXTBOX_X, rely=SET_CURRENT_TEXTBOX_Y, relheight=0.071, relwidth=0.4)
        self.setCurrent.configure(background="white")
        self.setCurrent.configure(font="TkTextFont")
        self.setCurrent.configure(foreground="black")
        self.setCurrent.configure(highlightbackground="#d9d9d9")
        self.setCurrent.configure(highlightcolor="black")
        self.setCurrent.configure(insertbackground="black")
        self.setCurrent.configure(selectbackground="blue")
        self.setCurrent.configure(selectforeground="white")
        self.setCurrent.configure(wrap="word")

        self.setOvp = tk.Text(top)
        self.setOvp.place(relx=SET_OVP_TEXTBOX_X, rely=SET_OVP_TEXTBOX_Y, relheight=0.071, relwidth=0.4)
        self.setOvp.configure(background="white")
        self.setOvp.configure(font="TkTextFont")
        self.setOvp.configure(foreground="black")
        self.setOvp.configure(highlightbackground="#d9d9d9")
        self.setOvp.configure(highlightcolor="black")
        self.setOvp.configure(insertbackground="black")
        self.setOvp.configure(selectbackground="blue")
        self.setOvp.configure(selectforeground="white")
        self.setOvp.configure(wrap="word")

        self.setOcp = tk.Text(top)
        self.setOcp.place(relx=SET_OCP_TEXTBOX_X, rely=SET_OCP_TEXTBOX_Y, relheight=0.071, relwidth=0.4)
        self.setOcp.configure(background="white")
        self.setOcp.configure(font="TkTextFont")
        self.setOcp.configure(foreground="black")
        self.setOcp.configure(highlightbackground="#d9d9d9")
        self.setOcp.configure(highlightcolor="black")
        self.setOcp.configure(insertbackground="black")
        self.setOcp.configure(selectbackground="blue")
        self.setOcp.configure(selectforeground="white")
        self.setOcp.configure(wrap="word")

        self.setVoltage.delete("1.0", END)
        self.setVoltage.insert("1.0", str(round(psu.get_nominal_voltage(), 3)))
        self.setCurrent.delete("1.0", END)
        self.setCurrent.insert("1.0", str(round(psu.get_nominal_current(), 3)))
        self.setOvp.delete("1.0", END)
        self.setOvp.insert("1.0", str(round(psu.get_nominal_voltage(), 3)))
        self.setOcp.delete("1.0", END)
        self.setOcp.insert("1.0", str(round(psu.get_nominal_current(), 3)))

    def destroy_all(self):
        self.status = False
        psu.close(True, True)
        for tt in self.tsk:
            tt.join()

    def update_value(self):
        self.labelStatus.configure(text="Running")
        while self.status:
            time.sleep(0.2)

            try:
                self.volt = round(psu.get_voltage(), 3)
                self.voltValue.set(self.volt)
            except:
                print("Could not read psu values")
            time.sleep(0.1)
            try:
                self.current = round(psu.get_current(), 3)
                self.currValue.set(self.current)
            except:
                print("Could not read psu values")

    def power_on(self):
        psu.output_on()
        self.labelStatus.configure(text="Power on")

    def power_off(self):
        psu.output_off()
        self.labelStatus.configure(text="Power off")

    def psu_connect(self):
        psu.remote_on()
        self.labelConnectionStatus.configure(text="Connected")
        T = threading.Thread(target=self.update_value)
        T.start()
        self.tsk.append(T)

    def psu_disconnect(self):
        psu.remote_off()
        self.labelConnectionStatus.configure(text="Disconnected")

    def psu_setVolt(self):
        setVolt = float(self.setVoltage.get("1.0", END))
        psu.set_voltage(setVolt)

    def psu_setCurrent(self):
        setCurrent = float(self.setCurrent.get("1.0", END))
        psu.set_current(setCurrent)

    def psu_setOvp(self):
        setOvp = float(self.setOvp.get("1.0", END))
        psu.set_ovp(setOvp)

    def psu_setOcp(self):
        setOcp = float(self.setOcp.get("1.0", END))
        psu.set_ocp(setOcp)

if __name__ == '__main__':
    path = os.path.abspath(__file__)
    os.chdir(os.path.dirname(path))
    config = configparser.ConfigParser()
    config.read("config.ini")

    psu = PsuEA(comport=str(config.get("DEVICE", "port")))
    # psu.set_ovp(28)
    # psu.set_ocp(10)
    psu.remote_off()

    vp_start_gui()
