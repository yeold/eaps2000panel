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
WATT_VAL_X =           0.11
WATT_VAL_Y =           0.81
LABEL_WATT_X =         0.7
LABEL_WATT_Y =         0.81

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
    psu.remote_off()
    psuData.destroy_all(psuData)
    root.destroy()

class psuData:
    volt = 0.0
    current = 0.0
    watt = 0.0
    defaultSetVolt = 0.0
    defaultSetCurrent = 0.0
    defaultOvp = 0.0
    defaultOcp = 0.0
    status = True
    connectionStatus = False
    tsk = []

    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        self.currValue = StringVar()
        self.voltValue = StringVar()
        self.wattValue = StringVar()

        top.minsize(250, 350)
        top.maxsize(250, 350)
        top.resizable(0,  0)
        top.title("EA PS 2000 Panel")

        self.setVoltageButton = tk.Button(top)
        self.setVoltageButton.place(relx=SETV_BUTTON_X, rely=SETV_BUTTON_Y, height=28, width=80)
        self.setVoltageButton.configure(text='''Set Voltage''')
        self.setVoltageButton.configure(command=self.psu_setVolt)

        self.setCurrentButton = tk.Button(top)
        self.setCurrentButton.place(relx=SETA_BUTTON_X, rely=SETA_BUTTON_Y, height=28, width=80)
        self.setCurrentButton.configure(text='''Set Current''')
        self.setCurrentButton.configure(command=self.psu_setCurrent)

        self.setOvpButton = tk.Button(top)
        self.setOvpButton.place(relx=SET_OVP_BUTTON_X, rely=SET_OVP_BUTTON_Y, height=28, width=80)
        self.setOvpButton.configure(text='''Set OVP''')
        self.setOvpButton.configure(command=self.psu_setOvp)

        self.setOcpButton = tk.Button(top)
        self.setOcpButton.place(relx=SET_OCP_BUTTON_X, rely=SET_OCP_BUTTON_Y, height=28, width=80)
        self.setOcpButton.configure(text='''Set OCP''')
        self.setOcpButton.configure(command=self.psu_setOcp)

        self.buttonON = tk.Button(top)
        self.buttonON.place(relx=ON_BUTTON_X, rely=ON_BUTTON_Y, height=28, width=75)
        self.buttonON.configure(text='''On''')
        self.buttonON.configure(command=self.power_on)

        self.buttonOff = tk.Button(top)
        self.buttonOff.place(relx=OFF_BUTTON_X, rely=OFF_BUTTON_Y, height=28, width=75)
        self.buttonOff.configure(text='''Off''')
        self.buttonOff.configure(command=self.power_off)

        self.buttonRemoteOn = tk.Button(top)
        self.buttonRemoteOn.place(relx=REMOTE_ON_BUTTON_X, rely=REMOTE_ON_BUTTON_Y, height=28, width=75)
        self.buttonRemoteOn.configure(text='''Connect''')
        self.buttonRemoteOn.configure(command=self.psu_connect)

        self.buttonRemoteOff = tk.Button(top)
        self.buttonRemoteOff.place(relx=REMOTE_OFF_BUTTON_X, rely=REMOTE_OFF_BUTTON_Y, height=28, width=75)
        self.buttonRemoteOff.configure(text='''Disconnect''')
        self.buttonRemoteOff.configure(command=self.psu_disconnect)

        self.labelVolt = tk.Label(top)
        self.labelVolt.place(relx=LABEL_VOLT_X, rely=LABEL_VOLT_Y, height=33, width=37)
        self.labelVolt.configure(font=("Arial", 14))
        self.labelVolt.configure(text='''V''')

        self.labelCurrent = tk.Label(top)
        self.labelCurrent.place(relx=LABEL_CURRENT_X, rely=LABEL_CURRENT_Y, height=33, width=37)
        self.labelCurrent.configure(font=("Arial", 14))
        self.labelCurrent.configure(text='''A''')

        self.labelVoltageVal = tk.Label(top)
        self.labelVoltageVal.place(relx=VOLT_VAL_X, rely=VOLT_VAL_Y, height=30, width=100)
        self.voltValue.set(str(self.volt))
        self.labelVoltageVal.configure(font=("Arial", 14))
        self.labelVoltageVal.configure(textvariable=self.voltValue)

        self.labelCurentVal = tk.Label(top)
        self.labelCurentVal.place(relx=CURRENT_VAL_X, rely=CURRENT_VAL_Y, height=30, width=100)
        self.currValue.set(str(self.current))
        self.labelCurentVal.configure(font=("Arial", 14))
        self.labelCurentVal.configure(textvariable=self.currValue)

        self.labelStatus = tk.Label(top)
        self.labelStatus.place(relx=LABEL_STATUS_X, rely=LABEL_STATUS_Y, height=23, width=100)
        self.labelStatus.configure(text='''Idle''')

        self.labelConnectionStatus = tk.Label(top)
        self.labelConnectionStatus.place(relx=LABEL_CONNECTION_STATUS_X, rely=LABEL_CONNECTION_STATUS_Y, height=23, width=100)
        self.labelConnectionStatus.configure(text='''Idle''')

        self.setVoltage = tk.Text(top)
        self.setVoltage.place(relx=SET_VOLT_TEXTBOX_X, rely=SET_VOLT_TEXTBOX_Y, relheight=0.071, relwidth=0.4)
        self.setVoltage.configure(background="white")
        self.setVoltage.configure(font="TkTextFont")
        self.setVoltage.configure(foreground="black")
        self.setVoltage.configure(wrap="word")

        self.setCurrent = tk.Text(top)
        self.setCurrent.place(relx=SET_CURRENT_TEXTBOX_X, rely=SET_CURRENT_TEXTBOX_Y, relheight=0.071, relwidth=0.4)
        self.setCurrent.configure(background="white")
        self.setCurrent.configure(font="TkTextFont")
        self.setCurrent.configure(foreground="black")
        self.setCurrent.configure(wrap="word")

        self.setOvp = tk.Text(top)
        self.setOvp.place(relx=SET_OVP_TEXTBOX_X, rely=SET_OVP_TEXTBOX_Y, relheight=0.071, relwidth=0.4)
        self.setOvp.configure(background="white")
        self.setOvp.configure(font="TkTextFont")
        self.setOvp.configure(foreground="black")
        self.setOvp.configure(wrap="word")

        self.setOcp = tk.Text(top)
        self.setOcp.place(relx=SET_OCP_TEXTBOX_X, rely=SET_OCP_TEXTBOX_Y, relheight=0.071, relwidth=0.4)
        self.setOcp.configure(background="white")
        self.setOcp.configure(font="TkTextFont")
        self.setOcp.configure(foreground="black")
        self.setOcp.configure(wrap="word")

        self.setVoltage.delete("1.0", END)
        self.setVoltage.insert("1.0", str(round(self.defaultSetVolt, 3)))
        self.setCurrent.delete("1.0", END)
        self.setCurrent.insert("1.0", str(round(self.defaultSetCurrent, 3)))
        self.setOvp.delete("1.0", END)
        self.setOvp.insert("1.0", str(round(self.defaultOvp, 3)))
        self.setOcp.delete("1.0", END)
        self.setOcp.insert("1.0", str(round(self.defaultOcp, 3)))

        self.labelWatt = tk.Label(top)
        self.labelWatt.place(relx=LABEL_WATT_X, rely=LABEL_WATT_Y, height=33, width=37)
        self.labelWatt.configure(font=("Arial", 14))
        self.labelWatt.configure(text='''W''')

        self.labelWattVal = tk.Label(top)
        self.labelWattVal.place(relx=WATT_VAL_X, rely=WATT_VAL_Y, height=30, width=100)
        self.wattValue.set(str(self.watt))
        self.labelWattVal.configure(font=("Arial", 14))
        self.labelWattVal.configure(textvariable=self.wattValue)

        self.labelConnectionStatus.configure(text="Connected")

    def destroy_all(self):
        self.status = False
        psu.close(True, True)
        for tt in self.tsk:
            tt.join()

    def update_value(self):
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

            self.watt = round((self.volt * self.current), 3)
            self.wattValue.set(self.watt)

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

    psuData.defaultSetVolt = float(config.get("PSU_PARAMS", "set_volt"))
    psuData.defaultSetCurrent = float(config.get("PSU_PARAMS", "set_current"))
    psuData.defaultOvp = float(config.get("PSU_PARAMS", "set_ovp"))
    psuData.defaultOcp = float(config.get("PSU_PARAMS", "set_ocp"))

    vp_start_gui()
