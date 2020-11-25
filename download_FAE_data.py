from onc.onc import ONC

my_token = 'your-token-here'
device_code = 'ARIS3000-1099'
save_dir = r'C:\Users\xavier.mouy\Documents'
date_start = '2017-05-18T00:00:00.000Z'
date_end = '2017-05-18T02:00:00.000Z'


onc = ONC(my_token, outPath=save_dir)
filters = {'deviceCode':device_code, 'dateFrom': date_start, 'dateTo':date_end, 'extension': 'mp4'}
onc.getDirectFiles(filters, overwrite=False)