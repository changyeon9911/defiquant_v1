import os
import time
import base64
import datetime
from dotenv import load_dotenv
from requests import get, post, put, delete
from cryptography.hazmat.primitives.serialization import load_pem_private_key

class BinanceInterface:
    """
    BinanaceInterface is responsible for:
        - Abstraction for Binance API
            - Authentication
            - Connection
            - Trading
            - Research
            - UserData
    """

    ########## Authentication ############
    def __init__(self, API_KEY, SECRET_KEY_PATH):
        self.API_URL = "https://api.binance.com" #testnet endpoint
        self.API_KEY = API_KEY
        self.SECRET_KEY_PATH = SECRET_KEY_PATH
        self.HEADER = self.generate_header()

    ########## Connection ############
    def generate_header(self, time_unit = "MICROSECOND", content_type = "application/x-www-form-urlencoded"):
        #headers
        headers = dict()
        headers["X-MBX-TIME-UNIT"] = time_unit
        headers["content-type"] = content_type
        headers["X-MBX-APIKEY"] = self.API_KEY

        return headers

    ########## Authentication ############
    def add_signature(self, params):
        #add signature into params
        private_key = None
        payload = '&'.join([f'{param}={value}' for param, value in params.items()])
        with open(self.SECRET_KEY_PATH, 'rb') as f:
            private_key = load_pem_private_key(data=f.read(), password=None)
        
        signature = base64.b64encode(private_key.sign(payload.encode('ASCII')))
        params['signature'] = signature
        return params

    ########## Connection ############
    def test_connectivity(self):

        #endpoint
        url = self.API_URL + "/api/v3/ping"

        #call API
        try:
            response = get(url=url, headers=self.HEADER)
            if (response.status_code == 200): 
                return True
            return False
        except Exception as e:
            raise e

    ########## Connection ############
    def check_servertime(self):

        #endpoint
        url = self.API_URL + "/api/v3/time"

        #call API
        try:
            response = get(url=url, headers=self.HEADER)
            time = response.json().get("serverTime")
            return datetime.datetime.fromtimestamp((time / 1000000.0))
        except Exception as e:
            raise e

    ########## Trading ############
    def make_new_order(self, parameter_dict : dict):

        #endpoint
        url = self.API_URL + "/api/v3/order"

        #parameters
        params = self.add_signature(parameter_dict)

        #call API
        try:
            response = post(url=url, headers=self.HEADER, params=params)
            return response
        except Exception as e:
            raise e

    ########## Research ############
    def get_statistics_24hr(self, parameter_dict : dict):

        #endpoint
        url = self.API_URL + "/api/v3/ticker/24hr"

        #call API
        try:
            response = get(url=url, headers=self.HEADER, params=parameter_dict)
            return response
        except Exception as e:
            raise e

    ########## Research ############
    def get_current_price(self, parameter_dict : dict):

        #endpoint
        url = self.API_URL + "/api/v3/avgPrice"

        #call API
        try:
            response = get(url=url, headers=self.HEADER, params=parameter_dict)
            return response
        except Exception as e:
            raise e
    
    ########## Research ############
    def get_candlestick(self, parameter_dict : dict):

        #endpoint
        url = self.API_URL + "/api/v3/klines"

        #call API
        try:
            response = get(url=url, headers=self.HEADER, params=parameter_dict)
            return response
        except Exception as e:
            raise e


    ########## UserData ############
    def get_userdata(self):

        #endpoint
        url = "https://api.binance.com/api/v3/account"

        #call API
        timestamp = int(time.time() * 1000.0)
        params = self.add_signature({"timestamp" : timestamp})
        try:
            response = get(url=url, headers=self.HEADER, params=params)
            return response
        except Exception as e:
            raise e
        
if __name__ == "__main__":
    load_dotenv()
    BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY")
    BINANCE_SECRET_KEY_PATH = os.environ.get("BINANCE_PRIVATE_KEY_PATH")
    interface =  BinanceInterface(BINANCE_API_KEY, BINANCE_SECRET_KEY_PATH)
    print(interface.get_userdata().content)
#    print(interface.get_statistics_24hr({"symbol" : "BTCUSDT"}).json())