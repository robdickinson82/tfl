# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
from config import USERNAME, PASSWORD, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, HELPER_PATH, EMAIL_TEMPLATE_PATH
sys.path.append(HELPER_PATH)

from flaskHelpers import start_server

start_server()
