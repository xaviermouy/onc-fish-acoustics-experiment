from onc.onc import ONC
import datetime

# Parameters
my_token = "a23161bc-180d-4c28-b46c-288ce9daeb5e"


save_dir = r"D:\ONC"
# date_start = "2017-05-18T00:00:00.000Z"
# date_end = "2017-05-18T00:20:00.000Z"

# date_start = "2018-01-18T19:00:00.000Z"
# date_end = "2018-01-18T19:30:00.000Z"

date_start = "2022-05-21T00:00:00.000Z"
date_end = "2022-12-02T00:00:00.000Z"

aris_code = "DIDSON3000SN374"  # "ARIS3000-1099"
video_code = "AXISCAMB8A44F04DEEA"  # "DRAGONFISHSUBC13113"
hydrophone_code = "ICLISTENHF1252"  # "ICLISTENAF2523"

# date_start = datetime.datetime(year=2017, month=5, day=18, hour=0, minute=00)
# date_end = datetime.datetime(year=2017, month=5, day=18, hour=5, minute=00)
# dataProductCode = "ARIS"
# segment_dur_min = 20
# segment_interval_hour = 1


# Sign in
onc = ONC(my_token, outPath=save_dir)

## ARIS DATA *****************************************************************
# Download mp4 files
filters_mp4 = {
    "deviceCode": aris_code,
    "dateFrom": date_start,
    "dateTo": date_end,
    "extension": "mp4",
}
onc.getDirectFiles(filters_mp4, overwrite=False)

# # Download mat files
# filters_mat = {
#     "deviceCode": aris_code,
#     "dateFrom": date_start,
#     "dateTo": date_end,
#     "extension": "mat",
#     "dataProductCode": "ARIS",
# }
# onc.orderDataProduct(filters_mat, overwrite=False)

## Hydrophone data ***********************************************************

# while date_start < date_end:
#     # define start stop time of segment
#     segment_end_time = date_start + datetime.timedelta(minutes=segment_dur_min)
#     segment_start_time_str = date_start.strftime("%Y-%m-%dT%H:%M:%S.000Z")
#     segment_end_time_str = segment_end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")
#     print(segment_start_time_str + ' -> ' + segment_end_time_str)
#     # Download wav files
#     filters ={'deviceCode':hydrophone_code,
#               'dateFrom': segment_start_time_str,
#               'dateTo':segment_end_time_str,
#               'extension': 'wav'}
#     onc.getDirectFiles(filters, overwrite=False)
#     #increment to nect segment
#     date_start = date_start + datetime.timedelta(hours=segment_interval_hour)

filters = {
    "deviceCode": hydrophone_code,
    "dateFrom": date_start,
    "dateTo": date_end,
    "extension": "wav",
}
onc.getDirectFiles(filters, overwrite=False)

## Video **********************************************************************
filters_mp4 = {
    "deviceCode": video_code,
    "dateFrom": date_start,
    "dateTo": date_end,
    "extension": "mp4",
}
onc.getDirectFiles(filters_mp4, overwrite=False)
