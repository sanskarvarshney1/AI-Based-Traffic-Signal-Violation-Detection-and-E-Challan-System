import datetime

import cv2
import imutils



import winsound

class TrafficProcessor:

    def __init__(self):
        self.firstFrame = None
        self.light = "Green"
        self.cnt = 0
        self.dynamic = False
        self.min_area = 500
        self.duration = 200  # millisecond
        self.freq = 900  # Hz

        # cam specific properties
        self.zone1 = (100, 150)
        self.zone2 = (450, 145)
        self.thres = 30
        self.dynamic = False

    def cross_violation(self, frame):
        text = ""
        isCar = False
        cropped_cars = []

        self.frame = imutils.resize(frame, width=500)
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.gray = cv2.GaussianBlur(self.gray, (21, 21), 0)

        if self.firstFrame is None:
            self.firstFrame = self.gray
            pack = {'frame': self.frame, 'reference': self.firstFrame, 'list_of_cars': cropped_cars, 'cnt': self.cnt}
            return pack

        self.frameDelta = cv2.absdiff(self.firstFrame, self.gray)
        self.thresh = cv2.threshold(self.frameDelta, self.thres, 255, cv2.THRESH_BINARY)[1]
        
        self.thresh = cv2.dilate(self.thresh, None, iterations=2)
        cnts = cv2.findContours(self.thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        
        for c in cnts:
            if cv2.contourArea(c) < self.min_area:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            if (self.zone1[0] < (x + w / 2) < self.zone2[0] and (y + h / 2) < self.zone1[1] + 100 and (
                    y + h / 2) > self.zone2[1] - 100):
                isCar = True

            if self.light == "Red" and self.zone1[0] < (x + w / 2) < self.zone2[0] and self.zone1[1] > (y + h / 2) > self.zone2[1]:
                winsound.Beep(self.freq, self.duration)
                rcar = self.frame[y:y + h, x:x + w]
                rcar = cv2.resize(rcar, (0, 0), fx=4, fy=4)
                cropped_cars.append(rcar)
                cv2.imwrite(r"E:\MAjor Project\reported_car\car_" + str(self.cnt) + ".jpg", rcar)
                self.cnt += 1
                text = "<Violation>"

            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 255, 0), 2)

        if self.dynamic or not isCar:
            self.firstFrame = self.gray
        if self.light == "Green":
            color = (0, 255, 0)
        else:
            color = (0, 0, 255)

        cv2.rectangle(self.frame, self.zone1, self.zone2, (255, 0, 0), 2)
        cv2.putText(self.frame, "Signal Status: {}".format(self.light), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.putText(self.frame, "{}".format(text), (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.putText(self.frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                    (10, self.frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

        pack = {'frame': self.frame, 'reference': self.firstFrame, 'list_of_cars': cropped_cars, 'cnt': self.cnt}

        return pack
