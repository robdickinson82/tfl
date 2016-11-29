from config import *
import re
from bsHelpers import getSoupFromHtml
from datetime import datetime
from requests import Session
from string import split
from hashlib import md5
from collections import namedtuple
from journey import Journey
from card import Card
from refund import Refund


class TflSession(Session):
    LOGINURL = "https://account.tfl.gov.uk/"
    BASEURL = "https://contactless.tfl.gov.uk/"


    def __init__(self, user):
        Session.__init__(self)
        self.user = user
        self.card = Card(self)
        self.login()

    def login(self):
        response = self.get(self.BASEURL)
        url = self.LOGINURL + "Login"
        data = {
            "UserName": self.user.username,
            "Password": self.user.password,
            "AppId": "a3ac81d4-80e8-4427-b348-a3d028dfdbe7",
            "App": "a3ac81d4-80e8-4427-b348-a3d028dfdbe7",
            "ReturnUrl": "https://contactless.tfl.gov.uk/DashBoard"
        }
        response = self.post(url, data)
        return

    def tfl_get(self, url):
        print("Getting " + url)
        response = self.get(self.BASEURL + url)
        return response

    def tfl_post(self, url, data):
        print("Posting " + url)
        response = self.post(self.BASEURL + url, data)
        return response

    def _tfl_get_soup(self, url):
        print("Getting " + url)
        response = self.get(self.BASEURL + url)
        card_soup = getSoupFromHtml(response.text)
        return card_soup

    def _tfl_post_soup(self, url, data):
        print("Posting " + url)
        response = self.post(self.BASEURL + url, data)
        card_soup = getSoupFromHtml(response.text)
        return card_soup

    def _check_for_relogin_required():
        return


    def extract_link_params(self, link):
        
        param_string = split(link, "?")[1]
        param_string = re.sub(r"&amp;", r"&", param_string)
        
        params = split(param_string, "&")
        param_dict = {}
        for param in params:
            key_value = split(param, "=")
            key = key_value[0]
            value = key_value[1]
            param_dict[key] = value

        return param_dict 

