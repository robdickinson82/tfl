# -*- coding: utf-8 -*-
from config import *
import re
from bsHelpers import getSoupFromHtml
from datetime import datetime
from requests import Session
from string import split
from hashlib import md5
from collections import namedtuple

class Journey:

    JourneyObj = namedtuple('JourneyObj', 'journey_id t_id link start_time end_time fare journey_from journey_to travel_Day_key')

    def __init__(self, card):
        self.card = card
        

    def get_journey_month_range(self, pi_ref, start_month, start_year, end_month = None, end_year = None):
        start_month_since_0bc = start_year * 12 + start_month - 1
        current_month_since_0bc = start_month_since_0bc
        if ((not end_year) or (not end_month)):
            end_year = start_year
            end_month = start_month

        end_month_since_0bc = end_year * 12 + end_month

        all_journeys = ()
        while current_month_since_0bc <= end_month_since_0bc:
            current_year = int(current_month_since_0bc / 12)
            current_month = (current_month_since_0bc % 12) + 1
            month_journeys = self._get_single_month(pi_ref,
                                   current_month,
                                   current_year)
            current_month_since_0bc = current_month_since_0bc + 1
            #all_journeys.update(month_journeys)
            all_journeys = all_journeys + month_journeys

        return all_journeys

    def _get_single_month(self, pi_ref, month, year):
        view_type = "Payments"
        
        verification_token = self._get_verification_token(pi_ref)

        url = "/Statements/refresh"

        data = {
            "__RequestVerificationToken": verification_token,
            "SelectedStatementType": view_type,
            "SelectedStatementPeriod":  str(month) + "|" + str(year),
            "PaymentCardId": pi_ref
        }

        response = self.card.session.tfl_post(url, data)
        statement_soup = getSoupFromHtml(response.text)

        html_statement_dates = statement_soup.findAll(attrs=
                                                         {"data-pageobject":
                                                         "travelstatement-paymentsummary"
                                                          })
        #print (html_statement_journeys)
        journeys = ()
        for html_statement_date in html_statement_dates:
            date = self._extract_journey_date(html_statement_date)
            html_statement_journeys = html_statement_date.findAll( attrs=
                                                         {"data-pageobject":
                                                         "statement-detaillink"})

            
            for html_statement_journey in html_statement_journeys:
                
                soup = html_statement_journey
                link = html_statement_journey["href"]
                params = self.card.session.extract_link_params(html_statement_journey["href"])
                start_time, end_time = self._extract_journey_times(soup) 
                if start_time:
                    if end_time:
                        start_time = start_time.replace(year=date.year, month=date.month, day=date.day)
                        end_time = end_time.replace(year=date.year, month=date.month, day=date.day)
                    else:
                        start_time = start_time.replace(year=date.year, month=date.month, day=date.day)
                        end_time = start_time
                else:
                    if end_time:
                        end_time = end_time.replace(year=date.year, month=date.month, day=date.day)
                        start_time = end_time
                    else:
                        start_time = date
                        end_time = date
                    
                
                    
                journey_id = params["ji"]
                t_id = params["ti"]
                travelDayKey = params["travelDayKey"]
                fare = self._extract_journey_fare(soup)
                journey_from = self._extract_journey_field(soup, "journey-from")
                journey_to = self._extract_journey_field(soup, "journey-to")
                journey = self.JourneyObj._make([journey_id, t_id, link, start_time, end_time, fare, journey_from, journey_to, travelDayKey])
                #if journey.journey_id not in journeys:
                    #journeys[journey.journey_id] = journey
                journeys = journeys + (journey,)

        return journeys

    def _get_verification_token(self, card_ref):
        url = "/Statements/TravelStatement?pi=" + card_ref
        response = self.card.session.tfl_get(url)
        statement_soup = getSoupFromHtml(response.text)

        verification_token = statement_soup.find(attrs=
                                                 {"name":
                                                  "__RequestVerificationToken"
                                                  })
        verification_token = verification_token["value"]

        return verification_token        

    def get(self):    
        url = journey_view_link
        response = self.card.user.session.tfl_get(url)
        soup = getSoupFromHtml(response.text)
        self.date = self._extract_journey_date(soup)
        self.fare = self._extract_journey_fare(soup)
        self.taps = self._extract_taps(soup)
        self._set_journey_date_from_taps()
        self._set_journey_id()
        return

    def _extract_journey_date(self, soup):
        text_date = soup.find(attrs={"data-pageobject": "statement-date"}).get_text()
        text_date = text_date.strip()
        date = datetime.strptime(text_date, '%d/%m/%Y')
        return date


    def _extract_journey_times(self, soup):
        end_time = None
        start_time = None
        start_end =  self._extract_journey_field(soup, "journey-time")
        start_end_parts = split(start_end, " - ")
        if start_end_parts[0] != "--:--":
            start_time = datetime.strptime(start_end_parts[0], '%H:%M')

        if len(start_end_parts) == 2:
            if start_end_parts[1] != "--:--":
                end_time = datetime.strptime(start_end_parts[1], '%H:%M')
        return start_time, end_time

    def _extract_journey_field(self, soup, field):
        journey_field = soup.find(attrs={"data-pageobject": field})
        if journey_field:
            journey_field = journey_field.get_text()
            journey_field = journey_field.strip()
        return journey_field

    def _extract_journey_fare(self, soup):
        text_fare = soup.find(attrs={"data-pageobject": "journey-fare"})
        text_fare = text_fare.string.encode("utf-8")
        line_match = re.match(r"£(?P<pounds>[\d]+)\.(?P<pence>[\d]{2})",
                              text_fare)
        int_fare = (int(line_match.group("pounds")) * 100
                    + int(line_match.group("pence")))
        return int_fare