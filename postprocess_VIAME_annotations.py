# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 13:26:31 2021

This script ingests all annotation files from VIAME, transform data into
specific fields (e.g. absolute times), and saves everything into a single
csv file.

This was written for the annotations made by on the DRAGONFISH video data.
It may need to be slightly adjusted to post process the annotations made on
the ARIS data.

@author: xavier.mouy
"""

import os
import pandas as pd
import csv
from datetime import datetime, timedelta
import copy

def init_dataframe(behavior_labels, zeros = False):
    # initialize final datframe
    df = pd.DataFrame({'filename':[],
                       'file_start_date':[],
                       'fps':[],
                       'detection_frame_idx':[],
                       'detection_frame_sec':[],
                       'detection_date':[],
                       'detection_year':[],
                       'detection_day':[],
                       'detection_hour':[],
                       'detection_minute':[],
                       'detection_second':[],
                       'detection_id':[],
                       'track_relative_id':[],
                       'track_global_id':[],
                       'behavior':[],
                       'TL_x':[],
                       'TL_y':[],
                       'BR_x':[],
                       'BR_y':[],                     
                       })
    for label in behavior_labels:
        if zeros:
            df[label]=[0]
        else:
            df[label]=[]
                
    return df


indir = r'C:\Users\xavier.mouy\Documents\PhD\Projects\ONC\ONC_Fish_Acoustic_Experiment\manual_annotations'
infile = r'DRAGONFISHSUBC13113_20171201T170752.csv'
outdir = r'C:\Users\xavier.mouy\Documents\PhD\Projects\ONC\ONC_Fish_Acoustic_Experiment\manual_annotations\merged'
filename_date_start_idx = 20
filename_date_end_idx = 35
behavior_labels = ['SHD', 'FIN','SWM','CRWL','STRT','DIVE','APPR','REST','SNAP']

# Initialize the glabal dataframe for the entire dataset
annot_dataset = init_dataframe(behavior_labels)
global_track_id = 0

# Go through each file
file_idx = 0
for file in os.listdir(indir):
    if file.endswith(".csv"):
        file_idx += 1
        print(infile)
        
        # date of the file
        file_date = datetime.strptime(infile[filename_date_start_idx:filename_date_end_idx], "%Y%m%dT%H%M%S")
        
        # loop through each line of the file
        with open(os.path.join(indir, infile), newline='') as f:
            csv_reader = csv.reader(f)
            # retrieve meta-data (namely fps) and header
            csv_headings = next(csv_reader)
            metadata = next(csv_reader)
            fps = float(metadata[1][4:])
            previous_track_id = 0  
            local_track_id = 0
            # retrieve annotations
            an_idx = 0
            for row in csv_reader:
                an_idx += 1
                print('file', str(file_idx), '- annotation', str(an_idx))
                detec_rel_time_sec = timedelta(seconds = float(row[2])/fps)
                detec_time = file_date +  detec_rel_time_sec
                single_annot = init_dataframe(behavior_labels, zeros=True)
                single_annot['filename'] = infile,
                single_annot['file_start_date'] = file_date
                single_annot['fps'] = fps
                single_annot['detection_frame_idx'] = int(row[2])
                single_annot['detection_frame_sec'] = int(row[2])/fps     
                single_annot['detection_date'] = detec_time
                single_annot['detection_year'] = detec_time.year
                single_annot['detection_day'] = detec_time.day
                single_annot['detection_hour'] = detec_time.hour
                single_annot['detection_minute'] = detec_time.minute
                single_annot['detection_second'] = detec_time.second
                single_annot['detection_id'] = row[9]
                current_track_id = int(row[0])
                if current_track_id != previous_track_id:
                    global_track_id +=1
                single_annot['track_relative_id'] = current_track_id
                single_annot['track_global_id'] = global_track_id        
                single_annot['TL_x'] = float(row[3]),
                single_annot['TL_y'] = float(row[4]),
                single_annot['BR_x'] = float(row[5]),
                single_annot['BR_y'] = float(row[6]),
                
                behavior_strs = '-'.join(row[11:])
                for label in behavior_labels:
                    find_result = behavior_strs.find('(trk-atr) ' + label)
                    if find_result > -1:
                        single_annot[label] = 1                
                    
                previous_track_id = copy.copy(current_track_id)        
                annot_dataset = annot_dataset.append(single_annot,ignore_index=True)


# write csv file
annot_dataset.to_csv(os.path.join(outdir,'merged_annotation_dataset.csv'))

