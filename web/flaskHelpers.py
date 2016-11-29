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

@app.route('/download/')
def statement(card_pi):
	statement = download_statement_for_card(card, month = None, year = None, num_months = 0)
	return download_statement(card["links"]["statement_csv"], 2, 2016, 0)


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

@app.route('/card/<pi_ref>/csv_statement/<int:year>/<int:month>')
def csv_statement(pi_ref, month, year):
	num_months = int(request.args.get('num_months', 0))
	cards = get_cards()
	selected_card = cards["card_list"][cards["card_index"][pi_ref]] 
	statement = download_statement_for_card(selected_card, month, year, num_months)
	print (statement)
	html = render_template('statement.html', statement = statement)
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