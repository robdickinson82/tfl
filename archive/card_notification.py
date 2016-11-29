# -*- coding: utf-8 -*-
class Card_Notification:

    def __init__(self, card, html_notification):
        self.card = card
        self.category = html_notification.p["data-pageobject"]
        self.text = html_notification.p.string
        return

    def output(self, indent=""):
        output = (indent
                  + "Category: "
                  + self.category
                  + " Text: "
                  + self.text
                  + "\n")
        return output.encode("utf-8")
