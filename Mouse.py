#Importing necessary libraries
import pyautogui
import cv2
import numpy as np
import time
import autopy
import HandTrackingModule as htm


#Setting up constants
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 10  # random value


#Initializing variables:
pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

#Initializing the camera using OpenCV:
cap = cv2.VideoCapture(0)
#Setting the width and height of the camera frame 
cap.set(3, wCam)
cap.set(4, hCam)

#Creating a hand detector object:
detector = htm.handDetector(maxHands=1)

#Getting the screen size using AutoPy:
wScr, hScr = autopy.screen.size()

# print(wScr, hScr)

#Infinite loop for continuous video capture
while True:
    # Step1: Find the landmarks
    success, img = cap.read()
    img = detector.findHands(img) #Hand tracking using the detector object
    lmList, bbox = detector.findPosition(img) #Getting hand landmarks


    # Step2: Get the tip of the index and middle finger
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:] #Gets the coordinates of the tip of the index finger.
        x2, y2 = lmList[12][1:] #Gets the coordinates of the tip of the middle  finger.
        x4, y4 = lmList[4][1:] #Gets the coordinates of the tip of the thumb.

        #print(x1,y1,x2,y2)

        # Step3: Check which fingers are up
        fingers = detector.fingersUp() #Checks which fingers are up using the fingersUp() method of the hand detector
        print(fingers)

        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),(255, 0, 255), 2)

        # Step4: Only Index Finger: Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:

            # Step5: Convert the coordinates of the index finger tip (x1, y1) to screen coordinates.
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

            # Step6: Smooth Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # Step7: Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)

            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x4, y4), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            plocX, plocY = clocX, clocY #Updating previous hand location for the next iteration.


        # Step8: Both Index and middle are up: Clicking Mode (for right click)
        if fingers[1] == 1 and fingers[2] == 1:

            # Step9: Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 4, img)

            # Step10: Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.rightClick()


        # Step8: Both Index and middle are up: Clicking Mode (for left click)
        if fingers[1] == 1 and fingers[2] == 1:

            # Step9: Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)

            # Step10: Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()


    # Step11: Frame rate
    cTime = time.time() 
    fps = 1/(cTime-pTime)
    pTime = cTime #Updating previous time.

    cv2.putText(img, str(int(fps)), (28, 58), cv2.FONT_HERSHEY_PLAIN, 3, (255, 8, 8), 3)

    # Step12: Display
    cv2.imshow("AI Mouse", img) 
    cv2.waitKey(1) #This line waits for 1 millisecond for a key event
