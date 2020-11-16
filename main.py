import matplotlib.pyplot as plt
import socket
import numpy as np
import threading
import select
import datetime
import traceback

from config import UDP_PORT,BUFFER_SIZE

class SpeakerRecognition:

    def __init__(self):
        self.sound_list = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", UDP_PORT))

        receive_data_thread = threading.Thread(target= self.receive_data)
        receive_data_thread.start()


    def get_time_and_sound_list(self, data):
        received = data.decode('utf-8')
        splited = received.split(",")
        date_str = datetime.datetime.strptime(splited[0],'%Y.%m.%d-%H.%M.%S.%f')
        ms = int(date_str.timestamp() *1000)
        sound_list = [int(value) for value in splited[1:]]
        return ms,sound_list

    def receive_data(self):
        try:
            while True:
                read,_,_ = select.select([self.sock.fileno()],[],[],0.1)
                if len(read) <= 0 : continue
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                ms,sound_list = self.get_time_and_sound_list(data)
                # self.sound_list += sound_list
                print(str(ms)+"  ",end="")
                print(len(sound_list))

        except Exception as e:
                print(traceback.format_exc())

if __name__ == "__main__":
    sr = SpeakerRecognition()
