# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
sys.path.append("..")
from config import HELPER_PATH, USERNAME, PASSWORD, DEBUG, LOG_PATH, LOG_FORMAT
sys.path.append(HELPER_PATH)

from flask import Flask
from flask import render_template, request, redirect
from TflSession.user import User

import logging

app = Flask(__name__)
app.logger.addHandler(logging.basicConfig(filename=LOG_PATH+'tfl_web.log', format=LOG_FORMAT, level=logging.DEBUG))


user = User(USERNAME, PASSWORD)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/cards/')
def cards():
	cards = user.session.card.get_all()
	html = render_template('cards.html', cards=cards)
	return html


@app.route('/card/<card_ref>')
def view_card(card_ref):
    cards = user.session.card.get_all()
    pi_ref = cards[card_ref].pi_ref
    card = user.session.card.get(pi_ref)
    journeys = user.session.card.journey.get_journey_month_range(pi_ref, 9, 2016)
    #sorted(league.items(), key= lambda x: x[1]['totalpts'], reverse=True)
    journeys = sorted(journeys, key= lambda x: x.start_time, reverse=True)
    html = render_template('card.html', card = card, journeys = journeys)
    return html


@app.route('/card/<card_ref>/journeys/<start_year>/<start_month>')
def card_journeys_update(card_ref, year, month):
    cards = user.session.card.get_all()
    pi_ref = cards[card_ref].pi_ref
    card = user.session.card.get(pi_ref)
    journeys = user.session.card.journey.get_journey_month_range(pi_ref, start_month, start_year)
	#journeys = sorted(card.journeys.items(), key= lambda x: (x[1]).date, reverse=True)
    html = render_template('journeys.html', card = card, journeys = journeys)
    return html

@app.route('/card/<card_ref>/refunds')
def card_refunds_update(card_ref):
    cards = user.session.card.get_all()
    pi_ref = cards[card_ref].pi_ref
    card = user.session.card.get(pi_ref)
    refunds = user.session.card.refund.get_all(pi_ref)
    #journeys = sorted(card.journeys.items(), key= lambda x: (x[1]).date, reverse=True)
    html = render_template('refunds.html', card = card, refunds = refunds)
    return html

@app.route('/card/<card_ref>/refund/<refund_id>/application', methods = ['GET', 'POST'])
def card_refund_create_application(card_ref, refund_id):
    cards = user.session.card.get_all()
    pi_ref = cards[card_ref].pi_ref
    card = user.session.card.get(pi_ref)
    refunds = user.session.card.refund.get_all(pi_ref)
    refund = refunds[refund_id]
    if request.method == 'GET':
        application_data = user.session.card.refund.start_application(refund.t_id, refund.journey_id, refund.travelDayKey)
        inputs = application_data["inputs"]
        selects = application_data["selects"]
        session_key = application_data["link_params"]["sessionKey"]
        html = render_template('refund_application.html', card = card, refund = refund, inputs=inputs, selects=selects, session_key=session_key)
    elif request.method == 'POST':
        month = refund.refund_date.strftime('%m')
        year = refund.refund_date.strftime('%Y')
        session_key = request.args.get('sessionKey')
        application_data = user.session.card.refund.submit_application(pi_ref, refund.t_id, refund.journey_id, refund.travelDayKey, month, year, session_key, request.form) 

        return redirect("/card/"+card_ref+"/refunds", code=302)
    return html

def start_server():
	app.debug = DEBUG
	app.run()

@app.context_processor
def format_fare():
    def format_fare(amount, currency=u'£'):
        return u'{1}{0:.2f}'.format(amount/100.0, currency)
    

    def format_time(time, format):
    	return_string = ""
    	if time:
    		return_string = time.strftime(format)
    	else:
    		return_string = "--:--"
    	return return_string

    return dict(format_fare=format_fare, format_time=format_time)	