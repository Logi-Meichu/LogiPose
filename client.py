import wx 
from time import sleep
import cv2 
import socket
import numpy as np
import _pickle as pickle
import threading

class ShowCapture(wx.Panel): 
    def __init__(self, parent, capture, fps=30): 
        wx.Panel.__init__(self, parent) 

        if capture:
            self.capture = capture 
            self.frame = None
            ret, frame = self.capture.read() 

            height, width = frame.shape[:2] 
            parent.SetSize((width, height)) 
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 

            self.bmp = wx.Bitmap.FromBuffer(width, height, frame) 

            self.timer = wx.Timer(self) 
            self.timer.Start(1000./fps)

            self.Bind(wx.EVT_PAINT, self.OnPaint) 
            self.Bind(wx.EVT_TIMER, self.NextFrame) 
            self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnErase)

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(self.Socket)

        self.addr = ("localhost", 6000)

    def OnClose(self,event):
        self.thread.terminate()
        self.Destroy()

    def OnErase(self, event):
        # Do nothing, reduces flicker by removing
        # unneeded background erasures and redraws
        pass

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self) 
        dc.DrawBitmap(self.bmp, 0, 0) 

    def NextFrame(self, event): 
        ret, self.frame = self.capture.read() 
        if ret: 
            self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB) 
            self.bmp.CopyFromBuffer(self.frame) 
            self.Refresh()

    def Socket(self):
        clientMessage = "ABCDEFG"
        print(type(self.frame))

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        client.connect(self.addr)

        client.sendall(clientMessage.encode())        

        serverMessage = str(client.recv(1024), encoding='utf-8')
        print('Server:', serverMessage)

        client.close()

if __name__ == '__main__':
    capture = None
    capture = cv2.VideoCapture(2) 
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) 
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720) 

    app = wx.App() 
    frame = wx.Frame(None) 
    cap = ShowCapture(frame, capture) 
    frame.Show() 
    app.MainLoop() 