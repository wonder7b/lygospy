import requests
import uuid

class Lygos:
    def __init__(self, api_key: str, api_url: str ="https://api.lygosapp.com/v1/"):
        self.api_key = api_key
        self.api_url = api_url

    def url_info(self) -> str:
        return self.api_url

    def verify_url(self):
        ...

    def getaways(self, id:str) -> list:
        ...

    def payment_links(self, getaway_id:str, all: bool=False):
        ...

    def create_getaways(self, id:str, shop_name:str, product_name, amount, multiple:bool=False ):
        ...

    def delete_getaways(self, getaway_id:str, multiple:bool=False):
        ...

    def update_getaways(self, getaways_id:str, multiple:bool=False, **kwargs):
        ...

