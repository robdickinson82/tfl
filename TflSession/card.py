# -*- coding: utf-8 -*-
from config import *
import re
from bsHelpers import getSoupFromHtml
from datetime import datetime
from requests import Session
from string import split
from hashlib import md5
from collections import namedtuple
from journey import Journey
from refund import Refund

import logging

class Card():

    CardObj = namedtuple('CardObj', 'pi_ref nickname status expiry reference card_id notifications')
    NotifObj = namedtuple('NotifObj', 'category text')
    

    def __init__(self, session):
        self.session = session
        self.journey = Journey(self)
        self.refund = Refund(self)
        return

    def get(self, card_ref):
        logging.debug('Entering Card GET')
        url = "Card/View?pi=" + card_ref
        card_soup = self.session._tfl_get_soup(url)
        #card = self._create_card_tuple()
        pi_ref = card_ref
        card_nickname = self._extract_nickname(card_soup)
        card_status = self._extract_card_status(card_soup)
        expiry = self._extract_expiry(card_soup)
        reference = self._extract_reference(card_soup)
        card_id = md5(card_nickname.encode()).hexdigest()
        notifications = []
        card = self.CardObj._make([pi_ref, card_nickname, card_status, expiry, reference, card_id, notifications])

        #print([method for method in dir(card) if callable(getattr(card, method))])
        return card

    def get_all(self):
        logging.debug('Entering Card GET ALL')
        url = "MyCards"
        cards_soup = self.session._tfl_get_soup(url)
        html_cards = cards_soup.findAll("a",
                                        attrs=
                                        {"data-pageobject":
                                        "mycards-card-cardlink"
                                         })

        cards = {}
        for html_card in html_cards:
            link = html_card["href"]
            pi_ref = self.session.extract_link_params(link)["pi"]
            card = self.get(pi_ref)
            cards[card.reference] = card
        return cards


    def _extract_nickname(self, card_soup):
        card_nickname = card_soup.find(attrs=
                                               {"class": "current-nickname"})
        card_nickname = card_nickname.get_text()
        card_nickname = card_nickname.replace('\n', '')
        card_nickname = re.sub(r"(.*) card number:ending in ([0-9]{4}).*",
                                    r"\1 ending in \2", card_nickname)
        return card_nickname

    def _extract_card_status(self, card_soup):
        card_status = card_soup.find(attrs={"class": "card-status"})
        card_status = card_status.stripped_strings.next()
        return card_status

    def _extract_expiry(self, card_soup):
        expiry = card_soup.find(attrs={"id": "view-card-cardexpiry"})
        expiry = expiry.string
        return expiry

    def _extract_reference(self, card_soup):
        reference = card_soup.find(attrs=
                                        {"id": "view-card-referencenumber"})
        reference = reference.string
        return reference    

    def _extract_notifications(self, card_soup):
        html_notifications = card_soup.findAll(attrs=
                                               {"data-pageobject":
                                                "card-notification"})

        notifications = []
        for html_notification in html_notifications:
            category = html_notification.p["data-pageobject"]
            text = html_notification.p.string
            notification = self.NotifObj._make([category, text])
            notifications.append(notification)
        return notifications