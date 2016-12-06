# -*- coding: utf-8 -*-
import sys
sys.path.append(".")
sys.path.append("..")
from config import HELPER_PATH, LOG_FORMAT, LOG_PATH
sys.path.append(HELPER_PATH)

from flaskHelpers import start_server

import logging



start_server()
