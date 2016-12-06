# -*- coding: utf-8 -*-
from config import *
import re
from bsHelpers import getSoupFromHtml
from datetime import datetime
from requests import Session
from string import split
from hashlib import md5
from collections import namedtuple, OrderedDict
import sys

import logging

class Refund():

    RefundObj = namedtuple('RefundObj', 'refund_id journey_id t_id travelDayKey refund_from refund_to refund_date refund_fare parent_card_id')

    def __init__(self, card):
        self.card = card


    def get_all(self, card_ref):
        card = self.card.get(card_ref)
        url = 'Card/Refunds?pi=' + card_ref
        refund_soup = self.card.session._tfl_get_soup(url)
        refunds = self._extract_refunds(refund_soup, card.reference)
        return (refunds)

    def start_application(self, ti_ref, ji_ref, travelDayKey):
        url = 'Refunds/Apply?ti='+ ti_ref +'&ji='+ ji_ref + '&travelDayKey=' + travelDayKey
        refund_application_soup = self.card.session._tfl_get_soup(url)
        form_soup = refund_application_soup.find(attrs={'id': 'page-content'}).form
        link_params = self.card.session.extract_link_params(form_soup["action"])

        selects_html = form_soup.findAll('select')
        selects = OrderedDict()
        for select_html in selects_html:
            select = {}
            select["name"] = select_html['name']
            options_html = select_html.findAll('option')
            select["options"] = {}
            for option_html in options_html:
                select["options"][option_html['value']] = option_html.string
            selects[select_html['name']] = select
        
        inputs_html = form_soup.findAll('input')
        inputs = OrderedDict()
        for input_html in inputs_html:
            inputs[input_html['name']] = input_html['value']

        form_data = {}
        form_data["inputs"] = inputs
        form_data["selects"] = selects
        form_data["link_params"] = link_params

        return form_data

    def submit_application(self, pi_ref, ti_ref, ji_ref, travelDayKey, month, year, sessionKey, form_data):
        url = 'Refunds/Confirm?pi='+pi_ref+'&ti='+ti_ref+'&st=Journeys&sp='+month+'|'+year+'&ji='+ji_ref+'&sessionKey='+sessionKey+'&travelDayKey='+travelDayKey
        submit_application_soup = self.card.session._tfl_post_soup(url, form_data.to_dict())

        page_content_soup = submit_application_soup.find(attrs={'id': 'page-content'})

        button_soup = page_content_soup.find(attrs={'id':'confirmrefund-submit-button'})
        logging.info(button_soup)

        form_soup = button_soup.parent.parent
        logging.info(form_soup)
        input_soup = form_soup.input

        data = {input_soup["name"]: input_soup["value"]}

        action = form_soup["action"]

        submit_application_soup = self.card.session._tfl_post_soup(action, data)        

        logging.info(submit_application_soup)

        return 

    def _extract_refunds(self, refund_soup, card_ref):
        refunds = OrderedDict()
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
            refund_id = md5((refund_from + refund_to + refund_date.strftime('%d/%m/%Y') + str(refund_fare)).encode()).hexdigest()
            refund = self.RefundObj._make([refund_id, journey_id, t_id, travelDayKey, refund_from, refund_to, refund_date, refund_fare, card_ref])
            refunds[refund_id] = refund
        return refunds

    def _extract_journey_fare(self, soup):
        text_fare = soup.find(attrs={"class": "journey-fare"})
        text_fare = text_fare.string.encode("utf-8")
        line_match = re.match("£(?P<pounds>[\d]+)\.(?P<pence>[\d]{2})",
                              text_fare)
        int_fare = (int(line_match.group("pounds")) * 100
                    + int(line_match.group("pence")))
        return int_fare