""" The frontend for the print-my-brain project for Insight Data Engineering
    more context: https://github.com/danjonpeterson/print-my-brain

"""
__author__ = 'Daniel Jon Peterson'

from flask import Flask

app = Flask(__name__)


from app import views

app.config.from_object('config')
