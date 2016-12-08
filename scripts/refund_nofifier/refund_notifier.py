# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
from config import (USERNAME, 
                   PASSWORD, 
                   AWS_ACCESS_KEY, 
                   AWS_SECRET_KEY, 
                   AWS_REGION, 
                   HELPER_PATH, 
                   EMAIL_TEMPLATE_PATH, 
                   LOG_PATH, LOG_FORMAT,
                   SERVER_URL)
sys.path.append(HELPER_PATH)

import db.tflDb as db

from flask import Flask
from flask import render_template
from jinja2 import Environment, FileSystemLoader

from helpers.aws import Ses
from TflSession import user

from collections import OrderedDict

import logging

logging.basicConfig(filename=LOG_PATH+'refund_notifier.log', format=LOG_FORMAT, level=logging.DEBUG)

logging.info('Setting up environment')
env = Environment(loader=FileSystemLoader(EMAIL_TEMPLATE_PATH + 'refund_notifier'))
template = env.get_template('email_refunds.html')

logging.info('Setting up ses')
ses = Ses(AWS_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY)

db_users = db.User.query.all()

for db_user in db_users:
  tfl_user = user.User(db_user.username, db_user.password)
  
  logging.info('Getting all cards')
  cards = tfl_user.session.card.get_all()

  all_refunds = OrderedDict()
  for card in cards:
      logging.info('Getting refunds for card - %s', cards[card].reference)
      refunds = tfl_user.session.card.refund.get_all(cards[card].pi_ref)
      logging.info('Got refunds - %s', refunds.keys())
      all_refunds.update(refunds)

  logging.debug('Getting all refunds for cards - %s', all_refunds)

  logging.info('Rendering template')
  html = template.render(refunds=all_refunds, base_url=SERVER_URL)

  logging.info('Sending email')
  ses.send_email('dickinson.rob@gmail.com', [db_user.email], "TFL Refunds Available", html)
