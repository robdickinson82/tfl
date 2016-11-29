# -*- coding: utf-8 -*-
import re
from hashlib import md5
from string import split
from bsHelpers import getSoupFromHtml
from card_notification import Card_Notification
from journey import Journey
from datetime import datetime



class Card:

    journey_start_month = 10
    journey_start_year = 2016

    ### TODO and fix
    def __init__(self, user, pi_ref):
        self.user = user
        self.notifications = []
        self.journeys = {}
        card_obj = self.user.session.card(pi_ref)
        print (card_obj)
        self.get_card_details(card_view_link)
        today = datetime.today()
        self.get_journey_history_multiple_months("Payments",
                                                 self.journey_start_month,
                                                 self.journey_start_year,
                                                 today.month,
                                                 today.year)
        return

    def get_card_details(self, card_view_link):
        url = card_view_link
        response = self.user.session.tfl_get(url)
        card_soup = getSoupFromHtml(response.text)
        self.links = {}
        self.links["view"] = card_view_link
        self.pi_ref = split(self.links["view"], "=")[1]
        self.card_nickname = card_soup.find(attrs=
                                            {"class": "current-nickname"})
        self.card_nickname = self.card_nickname.get_text()
        self.card_nickname = self.card_nickname.replace('\n', '')
        self.card_nickname = re.sub(r"(.*) card number:ending in ([0-9]{4}).*",
                                    r"\1 ending in \2", self.card_nickname)

        self.card_status = card_soup.find(attrs={"class": "card-status"})
        self.card_status = self.card_status.stripped_strings.next()
        self.expiry = card_soup.find(attrs={"id": "view-card-cardexpiry"})
        self.expiry = self.expiry.string
        self.reference = card_soup.find(attrs=
                                        {"id": "view-card-referencenumber"})
        self.reference = self.reference.string
        self.card_id = md5(self.card_nickname.encode()).hexdigest()
        self.extract_notifications(card_soup)
        return

    def get_refunds(self):
        url = url = "/Card/Refunds?pi=" + self.pi_ref
        response = self.user.session.tfl_get(url)
        card_soup = getSoupFromHtml(response.text)
        print (card_soup)
        return

    def extract_notifications(self, card_soup):
        html_notifications = card_soup.findAll(attrs=
                                               {"data-pageobject":
                                                "card-notification"})

        for html_notification in html_notifications:
            notification = Card_Notification(self, html_notification)
            self.notifications.append(notification)
        return

    def get_journey_history_multiple_months(self,
                                            view_type,
                                            start_month,
                                            start_year,
                                            end_month,
                                            end_year):
        start_month_since_0bc = start_year * 12 + start_month - 1
        current_month_since_0bc = start_month_since_0bc
        end_month_since_0bc = end_year * 12 + end_month

        while current_month_since_0bc <= end_month_since_0bc:
            current_year = int(current_month_since_0bc / 12)
            current_month = (current_month_since_0bc % 12) + 1
            self.get_journey_history_single_month(view_type,
                                                  current_month,
                                                  current_year)
            current_month_since_0bc = current_month_since_0bc + 1
        return

    def get_journey_history_single_month(self, view_type, month, year):
        # view_type: "Payments"
        url = "/Statements/TravelStatement?pi=" + self.pi_ref
        response = self.user.session.tfl_get(url)
        statement_soup = getSoupFromHtml(response.text)

        verification_token = statement_soup.find(attrs=
                                                 {"name":
                                                  "__RequestVerificationToken"
                                                  })
        verification_token = verification_token["value"]
        url = "/Statements/refresh"

        data = {
            "__RequestVerificationToken": verification_token,
            "SelectedStatementType": view_type,
            "SelectedStatementPeriod":  str(month) + "|" + str(year),
            "PaymentCardId": self.pi_ref
        }

        response = self.user.session.tfl_post(url, data)
        statement_soup = getSoupFromHtml(response.text)

        html_statement_journeys = statement_soup.findAll(attrs=
                                                         {"data-pageobject":
                                                         "statement-detaillink"
                                                          })

        for html_statement_journey in html_statement_journeys:
            journey = Journey(self, html_statement_journey["href"])
            if journey.hash not in self.journeys:
                self.journeys[journey.hash] = journey

        return

    def output(self, indent=""):
        output = (indent + "Ref: " + self.reference
                  + " Name: " + self.card_nickname
                  + " Expiry: " + self.expiry
                  + " Status: " + self.card_status
                  + "\n")
        output = output + indent + "...Notifications:\n"
        for notification in self.notifications:
            output = output + indent + notification.output(indent + "...")
        output = output + indent + "...Journeys:\n"
        for journey in self.journeys:
            output = (output
                      + indent
                      + self.journeys[journey].output(indent + "..."))

        output = output + "\n"
        return output.encode("utf-8")
