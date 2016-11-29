# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
from config import USERNAME, PASSWORD, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, HELPER_PATH, EMAIL_TEMPLATE_PATH
sys.path.append(HELPER_PATH)
print(sys.path)

from flask import Flask
from flask import render_template
from jinja2 import Environment, FileSystemLoader

from helpers.aws import Ses
from TflSession import user




env = Environment(loader=FileSystemLoader(EMAIL_TEMPLATE_PATH + 'refund_notifier'))
template = env.get_template('email_refunds.html')


user = user.User(USERNAME, PASSWORD)

ses = Ses(AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY)

cards = user.session.card.get_all()

all_refunds = ()
for card in cards:
    refunds = user.session.card.refund.get_all(cards[card].pi_ref)
    all_refunds = all_refunds + refunds

print(all_refunds)

html = template.render(refunds=all_refunds)

ses.send_email('dickinson.rob@gmail.com', ['dickinson.rob@gmail.com'], "TFL Refunds Available", html)
