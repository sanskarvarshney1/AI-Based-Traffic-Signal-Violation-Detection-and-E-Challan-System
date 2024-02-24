import cv2
import imutils
import numpy as np
import time

from processor import Vehicle


class DirectionViolationDetection:
    def __init__(self, vid_file):  
        self.cnt_up = 0
        self.cnt_down = 0
        self.light="Green"
        self.zone1 = (100, 200)
        self.zone2 = (450, 100)

        self.cap = cv2.VideoCapture(vid_file)

        # Capture the properties of VideoCapture to console
        # for i in range(19):
        #     print(i, self.cap.get(i))

        self.w = self.cap.get(3)
        self.h = self.cap.get(4)
        self.frameArea = self.h * self.w
        self.areaTH = self.frameArea / 200
        print('Area Threshold', self.areaTH)

        self.line_up = int(2 * (self.h / 5))
        self.line_down = int(3 * (self.h / 5))

        self.up_limit = int(1 * (self.h / 5))
        self.down_limit = int(4 * (self.h / 5))

        self.line_down_color = (255, 0, 0)
        self.line_up_color = (0, 0, 255)
        self.pt1 = [0, self.line_down]
        self.pt2 = [self.w, self.line_down]
        self.pts_L1 = np.array([self.pt1, self.pt2], np.int32)
        self.pts_L1 = self.pts_L1.reshape((-1, 1, 2))
        self.pt3 = [0, self.line_up]
        self.pt4 = [self.w, self.line_up]
        self.pts_L2 = np.array([self.pt3, self.pt4], np.int32)
        self.pts_L2 = self.pts_L2.reshape((-1, 1, 2))

        self.pt5 = [0, self.up_limit]
        self.pt6 = [self.w, self.up_limit]
        self.pts_L3 = np.array([self.pt5, self.pt6], np.int32)
        self.pts_L3 = self.pts_L3.reshape((-1, 1, 2))
        self.pt7 = [0, self.down_limit]
        self.pt8 = [self.w, self.down_limit]
        self.pts_L4 = np.array([self.pt7, self.pt8], np.int32)
        self.pts_L4 = self.pts_L4.reshape((-1, 1, 2))

       
        self.fgbg = cv2.createBackgroundSubtractorMOG2()

        self.kernelOp = np.ones((3, 3), np.uint8)
        self.kernelOp2 = np.ones((5, 5), np.uint8)
        self.kernelCl = np.ones((11, 11), np.uint8)

        # Variables
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.vehicles = []
        self.max_p_age = 5
        self.pid = 1

    def feedCap(self, frame):
        retDict = {
            'image_threshold': None,
            'image_threshold_2': None,
            'mask_image': None,
            'mask_image_2': None,
            'frame': None,
            'list_of_cars': []
        }
        cap = cv2.VideoCapture(r"E:\MAjor Project\videos\video8.mp4")

        #while (cap.isOpened()):
        #    _, frame = self.cap.read()
        #    if _ == 0:
        #        break

        for i in self.vehicles:
            i.age_one()  

        fgmask = self.fgbg.apply(frame)
        fgmask2 = self.fgbg.apply(frame)
        
        _, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        _, imBin2 = cv2.threshold(fgmask2, 200, 255, cv2.THRESH_BINARY)
    
        mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, self.kernelOp)
        mask2 = cv2.morphologyEx(imBin2, cv2.MORPH_OPEN, self.kernelOp)
     
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernelCl)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, self.kernelCl)
        retDict['image_threshold'] = cv2.resize(fgmask, (400, 300))
        retDict['image_threshold_2'] = cv2.resize(fgmask2, (400, 300))
        retDict['mask_image'] = cv2.resize(mask, (400, 300))
        retDict['mask_image_2'] = cv2.resize(mask2, (400, 300))

      
        cv2.rectangle(frame, self.zone1, self.zone2, (255, 0, 0), 2)
        contours0 = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours0 = imutils.grab_contours(contours0)
        for cnt in contours0:
            cv2.drawContours(frame, cnt, -1, (0,255,0), 3, 8)
            area = cv2.contourArea(cnt)
            # print area," ",areaTH
            if self.areaTH < area < 20000:
              
                M = cv2.moments(cnt)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                x, y, w, h = cv2.boundingRect(cnt)

                new = True
                for i in self.vehicles:
                    if abs(x - i.getX()) <= w and abs(y - i.getY()) <= h:
                        new = False
                        i.updateCoords(cx, cy) 
                        if i.going_UP(self.line_down, self.line_up):
                            self.cnt_up += 1
                            print("ID:", i.getId(), 'crossed going up at', time.strftime("%c"))
                            cv2.putText(frame,str(i.getId()), (x, y-2), cv2.FONT_HERSHEY_SIMPLEX, 5, 255)
                        elif i.going_DOWN(self.line_down, self.line_up):
                            roi = frame[y:y + h, x:x + w]
                            #cv2.imshow('Region of Interest', roi)
                            retDict['list_of_cars'] = roi
                            #print("Area equal to ::::", area)
                            self.cnt_down += 1
                            print("ID:", i.getId(), 'crossed going down at', time.strftime("%c"))
                            cv2.putText(frame,str(i.getId()), (x, y-2), cv2.FONT_HERSHEY_SIMPLEX, 5, 255)
                        break
                    if i.getState() == '1':
                        if i.getDir() == 'down' and i.getY() > self.down_limit:
                            i.setDone()
                        elif i.getDir() == 'up' and i.getY() < self.up_limit:
                            i.setDone()
                    if i.timedOut():
                        # Remove from the list person
                        index = self.vehicles.index(i)
                        self.vehicles.pop(index)
                        del i
                if new:
                    p = Vehicle.MyVehicle(self.pid, cx, cy, self.max_p_age)
                    self.vehicles.append(p)
                    self.pid += 1

                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.drawContours(frame, cnt, -1, (0,255,0), 3)

        str_down = 'DOWN: ' + str(self.cnt_down)
        frame = cv2.polylines(frame, [self.pts_L1], False, self.line_down_color, thickness=2)
        frame = cv2.polylines(frame, [self.pts_L2], False, self.line_up_color, thickness=2)
        frame = cv2.polylines(frame, [self.pts_L3], False, (255, 255, 255), thickness=1)
        frame = cv2.polylines(frame, [self.pts_L4], False, (255, 255, 255), thickness=1)
        cv2.putText(frame, str_down, (10,40),self.font,2,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(frame, str_down, (10,40),self.font,2,(255,0,0),1,cv2.LINE_AA)

        time.sleep(0.04)
        retDict['frame'] = cv2.resize(frame, (400, 300))
        return retDict

        cap.release()
        cv2.destroyAllWindows()
