import os
import uuid
import pika
import hashlib
import json
import psycopg2
import subprocess
import zipfile
#from zipfile import ZipFile
import datetime
import time
import requests
import smtplib
import file_checks
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, jsonify, flash, render_template, request, session, url_for, redirect
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import logout_user
from flask_cors import CORS
from flask_caching import Cache

from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import logging
import inspect

from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

# --------------------------
# OAuth settings
SERVER_METADATA_URI = 'https://accounts.google.com/.well-known/openid-configuration'
CLIENT_KWARGS = {'scope': 'openid profile email'}
CLIENT_ID = "489653581798-lt3j8q5hpsb0qoljocagl179arg3tmf9.apps.googleusercontent.com"
CLIENT_SECRET = "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"

# Flask app settings
APPLICATION_HOST = '127.0.0.1'
APPLICATION_PORT = 5000
DEBUG = False
SECRET_KEY = "ffu3jmfq9c8u4owm738hw8374hnc4387cfhnic"

# RabbitMQ settings
RABBITMQ_USERNAME = 'OMR_RMQ'
RABBITMQ_PASSWORD = 'Omr@123'
RABBITMQ_IP = '192.168.5.1'
RABBITMQ_PORT = 5672

# PostgreSQL settings
POSTGRESQL_USERNAME = "omruser"
POSTGRESQL_DATABASE_NAME = "omrdatabase"
POSTGRESQL_PORT = 5432
POSTGRESQL_HOSTNAME = "10.21.238.137"
POSTGRESQL_PASSWORD = "Omr@123"

# Google SMTP server settings
SENDER_EMAIL = "omr@cse.iitm.ac.in"
SENDER_PASSWORD = "wzxy vgmz wloo gape"
SMTP_SERVER_URI = 'smtp.gmail.com'
SMTP_PORT = 587
