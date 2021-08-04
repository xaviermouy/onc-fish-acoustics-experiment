# -*- coding: utf-8 -*-
"""
This script goes through the mp4 files in the video_dir folder and subfolders,
find the duration of each video file, then writes a csv file (video_files_durations.csv)
in the out_dir folder with teh luist of file names and durations.

Created on Tue Aug  3 21:42:48 2021

@author: xavier.mouy
"""
import pandas as pd
import os
import cv2

video_dir = r'C:\Users\xavier.mouy\Documents\PhD\Projects\ONC\ONC_Fish_Acoustic_Experiment\Dragonfish_camera\Video_detection_results\test'
out_dir =r'C:\Users\xavier.mouy\Documents\PhD\Projects\ONC\ONC_Fish_Acoustic_Experiment\Dragonfish_camera\Video_detection_results\test'
file_extension = ".mp4"

files_list = []
durations_list = []
# Loop through all videos files in video_dir and its subfolders
for root, directories, files in os.walk(video_dir):
    for file in files:
        if file.endswith(file_extension): # only select mp4 files        
            print(file)
            filename = os.path.join(root, file)            
            # open video file
            cap = cv2.VideoCapture(filename)
            # Get duration of video file
            nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # number of frames in the file
            fps = int(cap.get(cv2.CAP_PROP_FPS)) # frames per seconds            
            duration = nframes/fps # duration of the file in sec
            # save file name and duration to a list
            files_list.append(file)
            durations_list.append(duration)
            # close video file
            cap.release()
            
# convert files and durations list into a dataframe
dataframe = pd.DataFrame({'file':files_list, 'duration_sec': durations_list})

# Save dataframe to csv file
dataframe.to_csv(os.path.join(out_dir,'video_files_durations.csv'), index=False)