# -*- coding: utf-8 -*-
from config import *
import re
from bsHelpers import getSoupFromHtml
from datetime import datetime
from requests import Session
from string import split
from hashlib import md5
from collections import namedtuple


class Refund():

    RefundObj = namedtuple('RefundObj', 'journey_id t_id travelDayKey refund_from refund_to refund_date refund_fare')

    def __init__(self, card):
        self.card = card


    def get_all(self, card_ref):
        url = 'Card/Refunds?pi=' + card_ref
        refund_soup = self.card.session._tfl_get_soup(url)
        refunds = self._extract_refunds(refund_soup)
        return (refunds)

    def _extract_refunds(self, refund_soup):
        refunds = ()
        refunds_html = refund_soup.findAll('a', attrs={'data-pageobject': 'statement-detaillink'})
        for refund_html in refunds_html:
            params = self.card.session.extract_link_params(refund_html["href"])
            journey_id = params["ji"]
            t_id = params["ti"]
            travelDayKey = params["travelDayKey"]           
            refund_from = refund_html.find(attrs={'data-pageobject': 'journey-from'}).string
            refund_to = refund_html.find(attrs={'data-pageobject': 'journey-to'}).string
            refund_date = refund_html.find(attrs={'data-pageobject': 'journey-time'}).string
            refund_date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", refund_date)
            refund_date = datetime.strptime(refund_date, '%A %d %B %Y')
            refund_fare = self._extract_journey_fare(refund_html)
            refund = self.RefundObj._make([journey_id, t_id, travelDayKey, refund_from, refund_to, refund_date, refund_fare])
            refunds = refunds + (refund, )
        return refunds

    def _extract_journey_fare(self, soup):
        text_fare = soup.find(attrs={"class": "journey-fare"})
        text_fare = text_fare.string.encode("utf-8")
        line_match = re.match("£(?P<pounds>[\d]+)\.(?P<pence>[\d]{2})",
                              text_fare)
        int_fare = (int(line_match.group("pounds")) * 100
                    + int(line_match.group("pence")))
        return int_fare