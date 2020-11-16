import tkinter as tk
import tkinter.font as tkFont

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import socket
import numpy as np
import threading
import select
import datetime
import traceback
import random

from config import UDP_PORT,BUFFER_SIZE
from get_formant import get_formant

WORK_ID_DICT = {"update_graph" : None,"calc_formant":None,}

class SpeakerRecognition:

    def __init__(self):
        self.root = tk.Tk()
        width,height = 800,450
        self.root.geometry(f"{width}x{height}")
        self.root.title("Speaker Recognition System")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_window)

        self.main_frame = tk.Frame(master=self.root,bg="green")
        self.main_frame.pack(side=tk.TOP,fill=tk.BOTH,expand=True)

        self.graph = Ax()
        self.graph_canvas = FigureCanvasTkAgg(self.graph.fig,master=self.main_frame)
        self.graph_canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=True)


        self.is_continue_sound = True

        self.sound_list = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", UDP_PORT))

        self.receive_data_thread = threading.Thread(target= self.receive_data)
        self.receive_data_thread.start()

        WORK_ID_DICT["update_graph"] = self.root.after(200,self.update_graph)
        WORK_ID_DICT["calc_formant"] = self.root.after(1000,self.calc_formant)

        self.root.mainloop()



    def get_time_and_sound_list(self, data):
        received = data.decode('utf-8')
        splited = received.split(",")
        date_str = datetime.datetime.strptime(splited[0],'%Y.%m.%d-%H.%M.%S.%f')
        ms = int(date_str.timestamp() *1000)
        sound_list = [int(value) for value in splited[1:]]
        return ms,sound_list

    def receive_data(self):
        try:
            while self.is_continue_sound:
                read,_,_ = select.select([self.sock.fileno()],[],[],0.1)
                if len(read) <= 0 : continue
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                ms,sound_list = self.get_time_and_sound_list(data)
                self.sound_list += sound_list
                print(str(ms)+"  ",end="")
                print(len(sound_list))

        except Exception as e:
                print(traceback.format_exc())

    def calc_formant(self):
        if len(self.sound_list) >= 44100:
            x,y = get_formant(self.sound_list)
            self.add_params(x,y)
            self.sound_list = []
        WORK_ID_DICT["calc_formant"] = self.root.after(1000,self.calc_formant)

    def add_params(self,x,y):
        self.graph.add_params(x,y)

    def update_graph(self):
        self.graph.update_graph()
        self.graph_canvas.draw()
        WORK_ID_DICT["update_graph"] = self.root.after(200,self.update_graph)

    def on_close_window(self):
        self.is_continue_sound = False
        self.receive_data_thread.join()
        if WORK_ID_DICT["update_graph"] != None:
            self.root.after_cancel(WORK_ID_DICT["update_graph"])
        if WORK_ID_DICT["calc_formant"] != None:
            self.root.after_cancel(WORK_ID_DICT["calc_formant"])
        self.root.destroy()
        self.root.quit()

class Ax:
    def __init__(self):
        self.fig = plt.figure(figsize=(2,2))
        self.ax = self.fig.add_subplot(1,1,1)
        self.x = []
        self.y = []

    def add_params(self,x:list,y:list):
        self.x += x
        self.y += y
    
    def update_graph(self):
        self.ax.clear()
        self.ax.plot(self.x,self.y,"ro")

    def close_fig(self):
        plt.close(self.fig)

if __name__ == "__main__":
    sr = SpeakerRecognition()
