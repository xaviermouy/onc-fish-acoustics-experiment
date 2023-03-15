# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 12:01:40 2018

@author: xavier.mouy
"""
import os
import fnmatch
import skimage
from skimage import io
import numpy as np
import matplotlib.pyplot as plt
import cv2
import numpy as np
import imutils
import time
import csv


## ############################################################################

def estimateBackground(fname,nframes,gaussBlurSize):
    camera = cv2.VideoCapture(fname)
    frameStack=[]
    idx = 0
    # loop over the frames of the video
    while True:        
        # grab the current frame and initialize the occupied/unoccupied text
        (grabbed, frame) = camera.read()        
        # if the frame could not be grabbed, then we have reached the end
        # of the video
        if not grabbed:
            break
        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, gaussBlurSize, 0)
        frameStack.append(gray)
        
        idx+=1
        if idx >= nframes:
            break
    #median = np.mean(frameStack, axis=0).astype(dtype=np.uint8)    
    median = np.median(frameStack, axis=0).astype(dtype=np.uint8)    

    return median


def detectObjects(fname):
    
    # Parameters
    nBackgroundFrames=8000
    binThreshold = 15#20 10
    min_area = 10 #10
    gaussBlurSize=(31, 31) #gaussBlurSize=(31, 31)
    dilateKernel= np.ones((10,10),np.uint8) #(10,10)
    doplot = False #False
    FrameProcTimeInterval_ms=100

    # Initialization
    detecFrameIdx=[]
    detecFrameTime=[]
    detecBoxes=[]
    detecDataFrames=[]
    outFps = 10 #1000/FrameProcTimeInterval_ms
    
    # Load video
    camera = cv2.VideoCapture(fname)
    length = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(camera.get(cv2.CAP_PROP_FPS))

    # Define the codec and create VideoWriter object
    #fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #out = cv2.VideoWriter(outfile,fourcc, outFps, (500,280))

    # initialize the first frame in the video stream
    print('Define background scene...')
    BackgroundFrame = estimateBackground(fname, nBackgroundFrames,gaussBlurSize)
    firstFrame = BackgroundFrame
    print('Detect objects...')
    # loop over the frames of the video
    frameTime = 0
    idx=0
    while True:                
        # Define which frame to read
        #print(frameidx)
        camera.set(0,frameTime);   

        # grab the current frame and initialize the occupied/unoccupied text
        (grabbed, frame) = camera.read()
        # if the frame could not be grabbed, then we have reached the end of the video
        if not grabbed:
            break        
        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, gaussBlurSize, 0)     
        # if the first frame is None, initialize it
        if firstFrame is None:
            firstFrame = gray
            continue
        # compute the absolute difference between the current frame and first frame
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, binThreshold, 255, cv2.THRESH_BINARY)[1]     
        # dilate the thresholded image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(thresh, dilateKernel, iterations=2)
        (im2, cnts, hierarchy) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)         
        
#        plt.figure()
#        plt.imshow(frame)
#        plt.figure()
#        plt.imshow(gray,cmap='Greys')
#        plt.figure()
#        plt.imshow(frameDelta,cmap='Greys')
#        plt.figure()
#        plt.imshow(thresh,cmap='Greys')
#        plt.figure()
#        plt.imshow(firstFrame,cmap='Greys')
        
        # loop over the contours            
        isdetec=False
        boxCoord =[];
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < min_area:
                continue
            else:
                isdetec=True                    
                # compute the bounding box for the contour, draw it on the frame, and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                # box coord
                boxCoord.append([x,y,w,h])                            
        if isdetec == True:
            detecFrameIdx.append(idx) # Idx of the frame with detections
            detecFrameTime.append(frameTime/1000) # time of the frame with detections in sec
            detecBoxes.append(boxCoord) # save box coord for that frame
            detecDataFrames.append(frame) # save frame
        # draw the text and timestamp on the frame
        #cv2.putText(frame, "".format(text), (10, 20),
        #cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        #cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        #(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
     
        # write annotated video
        #out.write(frame)
        
        # show the frame and record if the user presses a key
        if doplot:
            cv2.imshow("Original video", frame)
            cv2.imshow("Thresholded video", thresh)
            cv2.imshow("Frame Delta", frameDelta)         
        
        # if the `q` key is pressed, break from the lop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        #if idx >= 500 :
        #    break
        # frame index
        idx+=1        
        frameTime += FrameProcTimeInterval_ms

    # close everything
    camera.release()
    #out.release()
    cv2.destroyAllWindows()
    
    return detecFrameIdx, detecFrameTime, detecBoxes, detecDataFrames, fps, outFps


def getConsecutiveDetectionFrames(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) > stepsize)[0]+1)


indir=r'C:\Users\xavier.mouy\Documents\PhD\Projects\AMAR_array\Data\2018-10-17_IOSdock_deployment\Video_data\Test'
outdir=r'C:\Users\xavier.mouy\Documents\PhD\Projects\AMAR_array\Data\2018-10-17_IOSdock_deployment\Video_data\results'

## list image files
listImageFiles = os.listdir(indir)  
#pattern = "*.mp4"  
pattern = "*.h264"
files=[]
for infile in sorted(listImageFiles):  
    if fnmatch.fnmatch(infile, pattern):
        fname = os.path.join(indir,infile)
        filerootname = os.path.splitext(os.path.basename(fname))[0]
        print(' ')
        print('--------------------------------------------') 
        print (fname)
        
        outputfilename=os.path.join(outdir, filerootname + '_detections.csv')
        
        if os.path.isfile(outputfilename) == True:
            print('File already processed...')
        else:
            # Detect moving ojects
            start_time = time.time()
            detecFrameIdx, detecFrameTime, detecBoxes, detecDataFrames, fps, outFps = detectObjects(fname)
            elapsed_time = time.time() - start_time
            print('Elapsed time: '+ str(int(elapsed_time))+' seconds' )
            
            # find detection periods
            print('Create output files...')
            dT = 0.3
            detections = getConsecutiveDetectionFrames(detecFrameTime, stepsize=dT)
            
            # Extract video snippets and write detection log
            durDetecThreshold = 1 # sec                
            # initialization
            detecinfo = [['File', 'DetecIdx','Tstart', 'Tend']]
            FrameStartIdx=0
            detecIdx = 0        
            # create output csv file
            myCsvFile = open(outputfilename, 'w')
            
            # loops through detected periods and extrcat video snippet if the duration is long enough 
            for detec in detections:
                lenDetec = len(detec)
                if len(detec)>0:
                    if detec[-1]-detec[0]>=durDetecThreshold: # detection is long enough
                        detecIdx += 1
                        #save info for CSV file
                        detecinfo.append([filerootname,detecIdx,detec[0],detec[-1]])
                        # Define the codec and create VideoWriter object
                        outfile = os.path.join(outdir,filerootname + '_DetecIdx-' + str(detecIdx) + '_Tstart-' + str(detec[0]) + '.avi')
                        fourcc = cv2.VideoWriter_fourcc(*'XVID')
                        out = cv2.VideoWriter(outfile,fourcc, outFps, (500,280))
                        for framenb in range(len(detec)):
                            frame = detecDataFrames[FrameStartIdx]
                            out.write(frame)
                            FrameStartIdx +=1
                        out.release()
                    else:
                        FrameStartIdx += lenDetec
                    
            # write Csv file
            with myCsvFile:
                writer = csv.writer(myCsvFile)
                writer.writerows(detecinfo)
