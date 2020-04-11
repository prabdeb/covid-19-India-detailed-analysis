'''TODO'''

import csv
import requests

RAW_DATA_END_POINT = "/raw_data.json"
RECOVERED_DATA_END_POINT = "/states_daily_csv/recovered.csv"
DECEASED_DATA_END_POINT = "/states_daily_csv/deceased.csv"

class Covid19indiaorg:
    '''TODO'''

    def __init__(self):
        '''TODO'''
        self.api_end_point = "https://api.covid19india.org"
    
    def get_raw_data(self):
        '''TODO'''
        r = requests.get(self.api_end_point + RAW_DATA_END_POINT)
        return r.json()["raw_data"]
    
    def get_recovered_data(self):
        '''TODO'''
        r = requests.get(self.api_end_point + RECOVERED_DATA_END_POINT)
        decoded_content = r.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        return cr
    
    def get_deceased_data(self):
        '''TODO'''
        r = requests.get(self.api_end_point + DECEASED_DATA_END_POINT)
        decoded_content = r.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        return cr