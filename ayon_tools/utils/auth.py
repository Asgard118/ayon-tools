import os
os.environ['USE_AYON_SERVER'] = '1'
import ayon_api

__all__ = ['auth']


class Auth:
    def __init__(self):
        self.SERVER_URL = None
        self.API_KEY = None
        self.HEADERS = {}

    def set_credentials(self, server_url: str = 'http://localhost:5000', api_key: str = 'veryinsecurapikey'):
        ayon_api.close_connection()
        os.environ['AYON_SERVER_URL'] = self.SERVER_URL = server_url.rstrip('/')
        os.environ['AYON_API_KEY'] = self.API_KEY = api_key
        self.HEADERS['x-api-key'] = self.API_KEY


auth = Auth()
