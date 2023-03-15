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
import scipy.io
import matplotlib.patches as patches
import matplotlib
matplotlib.use("Agg")
import matplotlib.animation as manimation

#matplotlib.use("Agg")

FFMpegWriter = manimation.writers['ffmpeg']
## ############################################################################

def getConsecutiveDetectionFrames(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) > stepsize)[0]+1)


indir=r'C:\Users\xavier.mouy\Documents\Workspace\GitHub\ONC-fish-experiment\data\sonar'
outdir=r'C:\Users\xavier.mouy\Documents\Workspace\GitHub\ONC-fish-experiment\data\sonar'

gaussBlurSize=(11, 11) #gaussBlurSize=(31, 31)
binThreshold=21 #5
dilateKernel =(4,4)
min_area = 6

fps= 3

## list image files
listImageFiles = os.listdir(indir)  
pattern = "*.mat"  
files=[]
for infile in sorted(listImageFiles):  
    if fnmatch.fnmatch(infile, pattern):
        fname = os.path.join(indir,infile)
        filerootname = os.path.splitext(os.path.basename(fname))[0]
        print(' ')
        print('--------------------------------------------') 
        print (fname)
        
        outputfilename=os.path.join(outdir, filerootname + '_detections.csv')
        
        #FFMpegWriter = manimation.writers['ffmpeg']
        #metadata = dict(title='Movie Test', artist='Matplotlib',comment='Movie support!')
        #writer = FFMpegWriter(fps=3, metadata=metadata)
        
        if os.path.isfile(outputfilename) == True:
            print('File already processed...')
        else:
            # Load mat file
            mat = scipy.io.loadmat(fname)
            frames = mat['Data']['acousticData'][0,0]

            #Define axes
            StartRange = mat['Config']['windowStart'][0,0][0,0]
            StopRange = mat['Config']['windowLength'][0,0][0,0] + StartRange
            nbinsRange = frames.shape[1]
            nbinsAngle = frames.shape[0]            
            axis_range = np.linspace(StartRange,StopRange,nbinsRange)
            #ANGLEAMP=1
            #axis_angle = ANGLEAMP*np.linspace(-14*(2*np.pi)/360,14*2*np.pi/360,nbinsAngle)
            axis_angle = np.linspace(-14,14,nbinsAngle)


            # Estimate background scene
            frameStack_blurred=[]
            frameStack_original=[]
            for frame in np.rollaxis(frames,2):
                gray = cv2.GaussianBlur(frame, gaussBlurSize, 0)
                frameStack_blurred.append(gray)
                frameStack_original.append(frame)
            median = np.median(frameStack_blurred, axis=0).astype(dtype=np.uint8)
            #plt.figure()
            #plt.imshow(median)
                
            # Detect objects
            detecFrameIdx=[]
            detecFrameTime=[]
            detecBoxes=[]
            detecDataFrames=[]
            fidx=0
            #fig,ax = plt.subplots(1)
  
            for idx in range(len(frameStack_blurred)):
                frameTime = (idx+1)*(1/fps)
                frame_blurred = frameStack_blurred[idx]
                #frame_original = cv2.cvtColor(frameStack_original[idx], cv2.COLOR_GRAY2BGR)
                frame_original = frameStack_original[idx]
                frameDelta = cv2.absdiff(median, frame_blurred)
                thresh = cv2.threshold(frameDelta, binThreshold, 100, cv2.THRESH_BINARY)[1]     
                thresh = cv2.dilate(thresh, dilateKernel, iterations=1)
                (im2, cnts, hierarchy) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) 
            
                #plt.figure()
                #plt.imshow(frameDelta)
                #plt.figure()
                #plt.imshow(thresh)
                #plt.figure()
                #plt.imshow(thresh2)
            
#                # Create figure and axes
#                ax.imshow(frame_original,cmap="gray")
                  
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
#                        # get Range
                        DetecRange = axis_range[int(np.round(x +(w/2)))]
#                        # Create a Rectangle patch
#                        rect = patches.Rectangle((x,y),w,h,linewidth=1,edgecolor='r',facecolor='none')
#                        # add range number
#                        plt.text(x+w,y+h, str(round(DetecRange,1)), color='r', fontsize=10)
#                        # Add the patch to the Axes
#                        ax.add_patch(rect)                              
                        # box coord
                        #boxCoord.append([x,y,w,h,DetecRange])         
                        boxCoord.append([axis_range[int(x)],axis_angle[int(y)],axis_range[int(w)],axis_angle[int(h)],DetecRange])         
                        
                if isdetec == True:
                    detecFrameIdx.append(idx) # Idx of the frame with detections
                    detecFrameTime.append(frameTime) # time of the frame with detections in sec
                    detecBoxes.append(boxCoord) # save box coord for that frame
                    detecDataFrames.append(frame_original) # save frame
    
            # find detection periods
            print('Create output files...')
            dT = 0.6
            detections = getConsecutiveDetectionFrames(detecFrameTime, stepsize=dT)
            
            # Extract video snippets and write detection log
            durDetecThreshold = 4 # sec                
            # initialization
            detecinfo = [['File', 'DetecIdx','Tstart', 'Tend']]
            FrameStartIdx=0
            detecIdx = 0        
            # create output csv file
            myCsvFile = open(os.path.join(outdir, filerootname + '_detections.csv'), 'w')
            
            # loops through detected periods and extrcat video snippet if the duration is long enough 
            for detec in detections:
    
                lenDetec = len(detec)
                if len(detec)>0:
                    if detec[-1]-detec[0]>=durDetecThreshold: # detection is long enough
                        detecIdx += 1                    
                        #save info for CSV file
                        detecinfo.append([filerootname,detecIdx,detec[0],detec[-1]])
                        
                        # Save video
                        outfile = os.path.join(outdir,filerootname + '_DetecIdx-' + str(detecIdx) + '_Tstart-' + str(detec[0]) + '.avi')
                        #fourcc = cv2.VideoWriter_fourcc(*'XVID')
                        #out = cv2.VideoWriter(outfile,fourcc, outFps, (500,280))
                        metadata = dict(title='Movie Test', artist='Matplotlib',comment='Movie support!')
                        outvidfile = os.path.join(outdir,filerootname[62:] + '_DetecIdx-' + str(detecIdx) + '_Tstart-' + str(round(detec[0],1)) + '.mp4')
                        fig = plt.figure(1)                       
                        ax = fig.add_subplot(1,1,1)
                        ax.set_title(str(detecIdx))
                        writer = FFMpegWriter(fps=fps, metadata=metadata)
                        with writer.saving(fig, outvidfile, 200):                        
                            # Create figure and axes                        
                            for framenb in range(len(detec)): # for each frame of a detection
                                # Load and display frame
                                frame = detecDataFrames[FrameStartIdx]
                                boxes = detecBoxes[FrameStartIdx]
                                #fig = plt.figure(1)
                                #ax.clear()
                                #ax.imshow(frame,cmap="gray")
                                #ax.imshow(frame)
                                plt.imshow(frame, extent = [0.7, 5, -14,14],interpolation='nearest',aspect='auto')                                                     
                                #plt.imshow(frame, extent = [0.7, 5, -14,14],aspect='auto', interpolation='nearest',vmin=0, vmax=10)                                 
                                ax.set_xlabel('Distance (m)',fontsize=12, fontweight='bold')
                                ax.set_ylabel('Beam anglev (degree)',fontsize=12, fontweight='bold')
                                #ax2.set_title('Video detections',fontsize=12)
                                #plt.xticks(rotation=45,ha='right')
                                
                                #ax.axis('tight')
                                # Add detection boxes and ranges
                                for box in boxes:
                                    # Create a Rectangle patch
                                    x=box[0]
                                    y=box[1]
                                    w=box[2]
                                    h=box[3]
                                    DetecRange=box[4]
                                    rect = patches.Rectangle((x,y),w,h,linewidth=0.3,edgecolor='r',facecolor='none')
                                    # add range number
                                    plt.text(x+w,y+h, str(round(DetecRange,1)), color='r', fontsize=10)
                                    # Add the patch to the Axes
                                    ax.add_patch(rect)                                     
                                    #out.write(frame)
                                # plot  frame
                                fig.canvas.draw()
                                #mng = plt.get_current_fig_manager()
                                #mng.full_screen_toggle() 
                                #figManager = plt.get_current_fig_manager()
                                #figManager.window.showMaximized()
                                plt.tight_layout()
                                plt.show()                                          
                                writer.grab_frame()
                                ax.clear()
                                #plt.pause(1/fps)
                                #plt.pause(0.01)
                                # Save frame to file                                
                                
                                FrameStartIdx +=1
                            #out.release()
                            plt.show()
                        
                    else:
                        FrameStartIdx += lenDetec
                    
            # write Csv file
            with myCsvFile:
                writer = csv.writer(myCsvFile)
                writer.writerows(detecinfo)
