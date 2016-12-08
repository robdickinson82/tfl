from config import *
import re
import logging
from bsHelpers import getSoupFromHtml
from datetime import datetime
from requests import Session
from string import split
from hashlib import md5
from collections import namedtuple
from journey import Journey
from card import Card
from refund import Refund

import logging


class TflSession(Session):
    LOGINURL = "https://account.tfl.gov.uk/"
    BASEURL = "https://contactless.tfl.gov.uk/"

    def __init__(self, user):
        logging.info('Creating A TflSession')
        Session.__init__(self)
        self.user = user
        self.card = Card(self)
        self.login()

    def login(self):
        logging.info('Logging in for %s', self.user.username)
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

    def logout(self):
        logging.info('Logging out for %s', self.user.username)
        home_soup = self._tfl_get_soup('')
        form_soup = home_soup.find(attrs={'id': 'signOutForm'})
        input_soup = form_soup.input
        data = {input_soup["name"]: input_soup["value"]}
        action = form_soup["action"]
        logout_soup = self.card.session._tfl_post_soup(action, data)
        self.card.session.cookies.clear_session_cookies()
        return logout_soup

    def refresh(self):
        url = "MyCards"
        cards_soup = self._tfl_get_soup(url)
        response = self.get(self.BASEURL + url)
        response_history = response.history
        needs_refresh = False
        if (len(response_history) > 0):
            for old_response in response_history:
                if ("LoginTimedOut" in old_response.headers["location"]):
                    needs_refresh = True
        if needs_refresh:
            self.login()
        return needs_refresh

    def tfl_get(self, url):
        response = self.get(self.BASEURL + url)
        return response

    def tfl_post(self, url, data):
        response = self.post(self.BASEURL + url, data)
        return response

    def _tfl_get_soup(self, url, base_url=None):
        logging.info("Getting " + url)
        if not base_url:
            base_url = self.BASEURL
        response = self.get(base_url + url)
        card_soup = getSoupFromHtml(response.text)
        return card_soup

    def _tfl_post_soup(self, url, data, base_url=None):
        logging.info("Posting " + url)
        if not base_url:
            base_url = self.BASEURL
        response = self.post(base_url + url, data)
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
