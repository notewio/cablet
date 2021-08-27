# by separating the camera read from our main loop, we no longer have to wait for camera updates to proceed calculating
# see here: https://www.pyimagesearch.com/2015/12/21/increasing-webcam-fps-with-python-and-opencv/

from threading import Thread
import cv2

class ThreadedVideo:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.grabbed, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            self.grabbed, self.frame = self.cap.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
