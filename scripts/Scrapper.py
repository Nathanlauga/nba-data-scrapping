import requests
from time import sleep


class Scrapper():
    """
    Class to simplify scrapping on website and API.

    """

    DEFAULT_HEADER = {
        'Host': 'stats.nba.com',
        'Referer': 'https://stats.nba.com',
        'Origin': 'https://stats.nba.com',
        'x-nba-stats-token': 'true',
        'x-nba-stats-origin': 'stats',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-NewRelic-ID': 'VQECWF5UChAHUlNTBwgBVw==',
        'Cache-Control': 'max-age=0'
    }

    def __init__(self, headers=None, max_call_errors=None):
        self.headers = self.DEFAULT_HEADER if headers == None else headers
        self.max_call_errors = max_call_errors

    def repeat_call_while_error(self, url):
        response = requests.get(url, headers=self.headers)
        errors_cnt = 0
        while not response.status_code != 200 & errors_cnt < self.max_call_errors:
            print('Response :',response.status_code)
            errors_cnt += 1
            sleep(1)
            response = requests.get(url, headers=self.headers)

        if errors_cnt == self.max_call_errors:
            return None

        return response

    def call_url(self, url):
        self.headers['Referer'] = url
        # self.headers['Origin'] = url
        
        response = requests.get(url, headers=self.headers)
        print('Response :',response.status_code)

        if response.status_code != 200:
            if self.max_call_errors != None:
                response = self.repeat_call_while_error(url=url)

            if response == None:
                return None

        return response

    def retrieve_json_api_from_url(self, url):
        response = self.call_url(url=url)

        if response == None:
            return None

        if response.status_code != 200:
            print('Error code : %i'%response.status_code)
            return None

        return response.json()
