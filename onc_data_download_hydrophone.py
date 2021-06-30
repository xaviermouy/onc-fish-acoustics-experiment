# -*- coding: utf-8 -*-
"""
Created on Fri May  7 16:08:42 2021

@author: xavier.mouy
"""

from onc.onc import ONC
import datetime
# Parameters
my_token = ''
device_code = 'ICLISTENAF2523'
#dataProductCode = 'ARIS'
save_dir = r'C:\Users\xavier.mouy\Desktop\New folder'
date_start = datetime.datetime(year=2017, month=5, day=18, hour=0, minute=00)
date_end = datetime.datetime(year=2017, month=5, day=18, hour=5, minute=00)
segment_dur_min = 20
segment_interval_hour = 1


# Sign in
onc = ONC(my_token, outPath=save_dir)
while date_start < date_end:
    # define start stop time of segment
    segment_end_time = date_start + datetime.timedelta(minutes=segment_dur_min)
    segment_start_time_str = date_start.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    segment_end_time_str = segment_end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    print(segment_start_time_str + ' -> ' + segment_end_time_str)
    # Download wav files
    filters ={'deviceCode':device_code,
              'dateFrom': segment_start_time_str,
              'dateTo':segment_end_time_str,
              'extension': 'wav'}
    onc.getDirectFiles(filters, overwrite=False)
    #increment to nect segment
    date_start = date_start + datetime.timedelta(hours=segment_interval_hour)