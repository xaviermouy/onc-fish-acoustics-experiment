# -*- coding: utf-8 -*-
"""
Created on Fri May  7 16:08:42 2021

@author: xavier.mouy
"""

from onc.onc import ONC

# Parameters
my_token = ''
device_code = 'DRAGONFISHSUBC13113'
#dataProductCode = 'ARIS'
save_dir = r'C:\Users\xavier.mouy\Documents'
date_start = '2017-05-18T00:00:00.000Z'
date_end = '2017-05-18T02:00:00.000Z'

# Sign in
onc = ONC(my_token, outPath=save_dir)

# Download mp4 files
filters_mp4 ={'deviceCode':device_code, 'dateFrom': date_start, 'dateTo':date_end, 'extension': 'mp4'}
onc.getDirectFiles(filters_mp4, overwrite=False)

# # Download mat files
# filters_mat ={'deviceCode':device_code, 'dateFrom': date_start, 'dateTo':date_end, 'extension': 'mat','dataProductCode':dataProductCode}
# onc.orderDataProduct(filters_mat, overwrite=False)
