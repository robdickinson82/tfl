# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
sys.path.append(".")

import unittest

import logging

from config import USERNAME, PASSWORD, LOG_PATH, LOG_FORMAT
from user import User

logging.basicConfig(filename=LOG_PATH+'tflSession_tests.log',
                    format=LOG_FORMAT,
                    level=logging.DEBUG)


class TestBasicTests(unittest.TestCase):
# python tests.py TestBasicTests

    def test_create_user(self):
        logging.info('START: Testing Creating User')
        user = User(USERNAME, PASSWORD)
        self.assertIsNotNone(user)
        logging.info('END: Testing Creating User')

    def test_logout(self):
        logging.info('START: Testing Logging Out User')
        user = User(USERNAME, PASSWORD)
        self.assertIsNotNone(user)
        cards = user.session.card.get_all()
        self.assertNotEqual(0, len(cards.keys()))
        logout = user.session.logout()
        cards = user.session.card.get_all()
        self.assertEqual(0, len(cards.keys()))

        logging.info('END: Testing Logging Out User')

    def test_refresh(self):
        logging.info('START: Testing Refreshing Session')
        user = User(USERNAME, PASSWORD)
        self.assertIsNotNone(user)
        cards = user.session.card.get_all()
        self.assertNotEqual(0, len(cards.keys()))
        logout = user.session.logout()
        cards = user.session.card.get_all()
        self.assertEqual(0, len(cards.keys()))
        needs_refresh = user.session.refresh()
        self.assertTrue(needs_refresh)
        cards = user.session.card.get_all()
        self.assertNotEqual(0, len(cards.keys()))
        needs_refresh = user.session.refresh()
        self.assertFalse(needs_refresh)
        logging.info('END: Testing Refreshing Session')


    def test_get_cards(self):
        logging.info('START: Testing Getting Cards for a User')
        user = User(USERNAME, PASSWORD)
        self.assertIsNotNone(user)
        cards = user.session.card.get_all()
        self.assertIsNotNone(cards)
        logging.info('Got Cards %s', cards.keys())
        logging.debug('Got Cards %s', cards)
        logging.info('END: Testing Getting Cards for a User')

    def test_get_single_card(self):
        logging.info('START: Testing Getting Card Detail')
        user = User(USERNAME, PASSWORD)
        self.assertIsNotNone(user)
        cards = user.session.card.get_all()
        self.assertIsNotNone(cards)
        card = cards[cards.keys()[0]]
        card_pi_ref = card.pi_ref
        card = user.session.card.get(card_pi_ref)
        self.assertIsNotNone(card)
        logging.info('Got Card : %s', card.reference)
        logging.debug('Got Card : %s', card)
        logging.info('END: Testing Getting Card Detail')

    def test_get_journeys(self):
        logging.info('START: Testing Getting Journeys')
        user = User(USERNAME, PASSWORD)
        card = self.get_a_card(user)
        card_pi_ref = card.pi_ref
        journeys = user.session.card.journey.get_journey_month_range(card_pi_ref, 
                                                                     7, 
                                                                     2016, 
                                                                     8, 
                                                                     2016)
        return

    def test_get_refunds(self):
        logging.info('START: Testing Getting Journeys')
        user = User(USERNAME, PASSWORD)
        card = self.get_a_card(user)
        card_pi_ref = card.pi_ref
        refunds = user.session.card.refund.get_all(card_pi_ref)
        logging.info('Got refunds - %s', refunds)

    def test_refund_apply(self):
        logging.info('START: Testing Refund Apply')
        user = User(USERNAME, PASSWORD)
        card = self.get_a_card(user)
        refunds = user.session.card.refund.get_all(card.pi_ref)
        if len(refunds.keys()) > 0:
            refund = refunds[refunds.keys()[0]]
            output = user.session.card.refund.start_application(refund.t_id, refund.journey_id, refund.travelDayKey)
        else:
            output = "No refunds available"
        logging.info(output)

    def get_a_card(self, user):
        cards = user.session.card.get_all()
        card = cards[cards.keys()[0]]
        return card


if __name__ == '__main__':
    logging.info('Starting TflSessionTests')
    unittest.main()
    logging.info('Starting TflSessionTests')
