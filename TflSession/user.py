# -*- coding: utf-8 -*-
from bsHelpers import getSoupFromHtml
#from card import Card
from session import TflSession


class User:

    cards = {}

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = TflSession(self)
 