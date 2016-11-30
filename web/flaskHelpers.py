# -*- coding: utf-8 -*-
from config import USERNAME, PASSWORD, DEBUG

from flask import Flask
from flask import render_template, request
from user import User

app = Flask(__name__)

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
	journeys = user.session.card.journey.get_journey_month_range(card_ref, start_month, start_year)
	#journeys = sorted(card.journeys.items(), key= lambda x: (x[1]).date, reverse=True)
	html = render_template('journeys.html', card = card, journeys = journeys)
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