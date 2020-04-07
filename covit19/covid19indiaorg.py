'''TODO'''

import requests

RAW_DATA_END_POINT = "/raw_data.json"

class Covid19indiaorg:
    '''TODO'''

    def __init__(self):
        '''TODO'''
        self.api_end_point = "https://api.covid19india.org"
    
    def get_raw_data(self):
        '''TODO'''
        r = requests.get(self.api_end_point + RAW_DATA_END_POINT)
        return r.json()["raw_data"]