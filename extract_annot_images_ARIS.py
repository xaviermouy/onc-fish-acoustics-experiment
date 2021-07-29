import csv
import pandas as pd
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt

def frame_capture(file):    
    grayFrameStack=[]
    cap = cv2.VideoCapture(file)
    if (cap.isOpened()== False):        
        print("Error opening video stream or file")
    else:
     	# Read until video is completed
        while(cap.isOpened()):            
            ret, frame = cap.read()
            if ret == True:                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                #cv2.imshow('Frame',gray)
                grayFrameStack.append(gray) 
            # Break the loop
            else:
                break
        cap.release()
        cv2.destroyAllWindows()
    return grayFrameStack

def loadcsv(file):
    df = pd.read_csv(file) # load csv file as dataframe
    df['filename'] = df['filename'].apply(lambda x: x[0:28]) # truncates file names to remove extension
    return df

def find_annotations(file, csvdata):
    root_file_name = file[0:28] # removes extension of the aris file name
    csv_filtered = csvdata[csvdata['filename']==root_file_name] # only keeps annotations for that aris file
    return csv_filtered
    
## THE SCRIPT STARTS HERE ####################################################

csvfile = r'C:\Users\xavier.mouy\Documents\PhD\Projects\ONC\Detector\merged_annotation_updateddataset.csv'
aris_dir = r'C:\Users\xavier.mouy\Documents\PhD\Projects\ONC\Detector\data'
out_dir = r'C:\Users\xavier.mouy\Documents\PhD\Projects\ONC\Detector\annotation_images'

# load CSV file with manual annotations
csvdata = loadcsv(csvfile)

# Loop through all aris files
for file in os.listdir(aris_dir):
    if file.endswith(".mp4"):
        print(file)
        # find annotations for that aris file
        annots = find_annotations(file, csvdata)
        print( '-> ', str(len(annots)), 'annotations')
        
        # extract annotations frames and save as separate images
        if len(annots)>0: # if there are annotatiosn for that file...        
            
            # load all frames from the video             
            frames = frame_capture(os.path.join(aris_dir,file))
            # go through each annotations and save annotation box as separate image
            for idx, annot in annots.iterrows():
                frame_idx = int(annot['detection_frame_idx'])
                track_global_id = annot['track_global_id']
                detection_id = annot['detection_id']
                # Calculate cneter of annotation box
                midpoint_X = int(annot['TL_x']) + int(round((annot['BR_x'] - annot['TL_x'])/2))
                midpoint_Y = int(annot['TL_y']) + int(round((annot['BR_y'] - annot['TL_y'])/2))
                frame = frames[frame_idx]
                
                # crop to fit annotation box
                # frame2 = frame[int(annot['TL_y']):int(annot['BR_y']), int(annot['TL_x']):int(annot['BR_x'])  ]
                           
                # crop to fixed width and height
                half_width = 20
                half_height = 20
                frame2 = frame[int(midpoint_Y-half_height):int(midpoint_Y+half_height), int(midpoint_X-half_width):int(midpoint_X+half_width) ]
                              
                # plt.imshow(frame)
                # plt.plot(midpoint_X,midpoint_Y,'.', color = 'red')
                # plt.draw()
                
                image_name = detection_id + '_' + str(int(track_global_id)) + '_' + str(int(frame_idx)) + '_' + file[0:-4] + '.png'
                cv2.imwrite(os.path.join(out_dir,image_name), frame2)

            
            