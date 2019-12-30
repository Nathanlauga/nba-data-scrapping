import requests
from time import sleep


class Scrapper():
    """
    Class to simplify scrapping on website and API.

    """

    DEFAULT_HEADER = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0'
    }

    def __init__(self, headers=None, max_call_errors=None):
        self.headers = self.DEFAULT_HEADER if headers == None else headers
        self.max_call_errors = max_call_errors

    def repeat_call_while_error(self, url):
        response = requests.get(url, headers=self.headers)
        errors_cnt = 0
        while not response.status_code != 200 & errors_cnt < self.max_call_errors:
            errors_cnt += 1
            sleep(1)
            response = requests.get(url, headers=self.headers)

        if errors_cnt == self.max_call_errors:
            return None
        return response

    def call_url(self, url):
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            if max_error != None:
                response = self.repeat_call_while_error(url=url)

            if response == None:
                return None

        return response

    def retrieve_json_api_from_url(self, url):
        response = self.call_url(url=url)
        if response == None:
            return None
        return response.json()
