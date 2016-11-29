# -*- coding: utf-8 -*-
#from config import *
import re
from string import split
from hashlib import md5
from datetime import datetime
from bsHelpers import getSoupFromHtml
from collections import namedtuple



class Journey2:

    def __init__(self, card, journey_view_link):
        self.card = card
        url = journey_view_link
        response = self.card.user.session.tfl_get(url)
        soup = getSoupFromHtml(response.text)
        self.date = self._extract_journey_date(soup)
        self.fare = self._extract_journey_fare(soup)
        self.taps = self._extract_taps(soup)
        self._set_journey_date_from_taps()
        self._set_journey_id()
        return


 


    def __getitem__(self, key):
        return getattr(self, key)

    def output(self, indent=""):
        output = (indent + "Date: "
                  + self.date.strftime('%A %d %B %Y %H:%M')
                  + " Fare: " + str(self.fare/100.0) + " ")
        output = (output + "Stops: "
                  + self.taps[0]["station"]
                  + " ("
                  + self.taps[0]["time"].strftime('%H:%M')
                  + ") ")
        for tap in self.taps[1:]:
            output = (output
                      + " -> " + tap["station"]
                      + " (" + tap["time"].strftime('%H:%M')
                      + ") ")
            if "sub-message" in tap:
                output = output + "[" + tap["sub-message"] + "]"
        output = output + "\n"
        return output.encode("utf-8")

    def _extract_journey_date(self, soup):
        text_date = soup.find(attrs={"id": "journey-date"}).get_text()
        text_date = text_date.strip()
        text_date = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", text_date)
        date = datetime.strptime(text_date, '%A %d %B %Y')
        return date

    def _extract_journey_fare(self, soup):
        text_fare = soup.find(attrs={"id": "journey-fare"})
        text_fare = text_fare.string.encode("utf-8")
        line_match = re.match("£(?P<pounds>[\d]+)\.(?P<pence>[\d]{2})",
                              text_fare)
        int_fare = (int(line_match.group("pounds")) * 100
                    + int(line_match.group("pence")))
        return int_fare

    def _extract_tap_time(self, raw_tap, date):
        text_time = raw_tap.find(attrs={"class": "time-and-mode"})
        text_time = text_time.get_text()
        text_time = text_time.replace('\n', '')
        text_time = text_time.replace('\r', '')
        text_time = text_time.strip()
        if text_time != '--:--':
            time = datetime.strptime(date.strftime('%A %d %B %Y')
                                     + " " + text_time,
                                     '%A %d %B %Y %H:%M')
        else:
            time = date
        return time

    def _extract_tap_station(self, raw_tap):
        station = raw_tap.find(attrs={"class": "journey-station"})
        station = station.p
        station = station.get_text()
        station = station.replace('\n', '')
        station = station.replace('\r', '')
        station = station.strip()
        return station

    def _extract_tap_sub_message(self, raw_tap):
        sub_message = raw_tap.find("p", attrs={"class": "sub-message"})
        if sub_message:
            sub_message = sub_message.string
            sub_message = sub_message.replace('\n', '')
            sub_message = sub_message.replace('\r', '')
            sub_message = sub_message.strip()
        return sub_message

    def _extract_taps(self, soup):
        taps = []
        raw_taps = soup.findAll(attrs={"class": "journey-tap"})
        for raw_tap in raw_taps:
            tap = {}
            tap["time"] = self._extract_tap_time(raw_tap, self.date)
            tap["station"] = self._extract_tap_station(raw_tap)
            tap["sub_message"] = self._extract_tap_sub_message(raw_tap)
            taps.append(tap)
        return taps

    def _set_journey_date_from_taps(self):
        if self.taps[0]["time"]:
            self.date = self.taps[0]["time"]
        return

    def _set_journey_id(self):
        self.hash = (md5(self.taps[0]["station"]
                     + self.date.strftime('%A %d %B %Y %H:%M'))
                     .hexdigest())
        return
