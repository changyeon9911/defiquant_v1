import os
import jwt # type: ignore
import uuid
import time
import hashlib
from dotenv import load_dotenv # type: ignore
from requests import get, post, put, delete # type: ignore
from urllib.parse import urlencode, unquote

class UpbitInterface:
    """
    BinanaceInterface is responsible for:
        - Abstraction for Upbit API
            - Trading
            - Research
            - UserData
    """

    ########## INIT ############
    def __init__(self, API_KEY, SECRET_KEY):
        self.API_URL = "https://api.upbit.com" #testnet endpoint
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY

    ########## Trading ############
    def make_new_order(self, parameter_dict : dict):

        #endpoint
        url = self.API_URL + "/v1/orders"

        #parameters
        query_string = unquote(urlencode(parameter_dict, doseq=True)).encode("utf-8")
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        #payload
        payload = {
            'access_key': self.API_KEY,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        #authentication
        jwt_token = jwt.encode(payload, self.SECRET_KEY)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
          'Authorization': authorization,
        }

        #call API
        try:
            response = post(url=url, json=parameter_dict, headers=headers)
            return response
        except Exception as e:
            raise e
    
    ########## Research ############
    def get_candlestick(self, units, parameter_dict : dict):

        #endpoint
        url = self.API_URL + f"/v1/candles/{units}"

        #headers
        headers = {"accept": "application/json"}

        #call API
        try:
            response = get(url=url, headers=headers, params=parameter_dict)
            return response
        except Exception as e:
            raise e


    ########## UserData ############
    def get_userdata(self):

        #endpoint
        url = self.API_URL + "/v1/accounts"

        #payload
        payload = {
            'access_key': self.API_KEY,
            'nonce': str(uuid.uuid4()),
        }

        #authenticate
        jwt_token = jwt.encode(payload, self.SECRET_KEY)
        authorization = 'Bearer {}'.format(jwt_token)
        headers = {
          'Authorization': authorization,
        }

        try:
            response = get(url=url, headers=headers)
            return response
        except Exception as e:
            raise e
        
if __name__ == "__main__":
    load_dotenv()
    UPBIT_API_ACCESS_KEY = os.environ.get("UPBIT_API_ACCESS_KEY")
    UPBIT_API_SECRET_KEY = os.environ.get("UPBIT_API_SECRET_KEY")
    interface =  UpbitInterface(UPBIT_API_ACCESS_KEY, UPBIT_API_SECRET_KEY)
    print(interface.get_userdata().content)
#    print(interface.get_statistics_24hr({"symbol" : "BTCUSDT"}).json())