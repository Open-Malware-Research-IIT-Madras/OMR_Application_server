"""
Module Name: app.py

Description:
    Entry point for the OMR WebApp. Loads all configuration modules 
    (API keys, imports, database, controller, email, and app settings),
    initializes logging, and starts the Flask application.

Functions:
    None defined explicitly in this file.

Classes:
    None defined explicitly in this file.

Usage:
    Run this script directly to start the Flask server:
        python main.py

Author:
    Allan Pais
"""

from apikey import *
from imports import *
from database_config import *
from controller_config import *
from email_config import *
from app_config import *



if __name__=="__main__":
   
    logger.info('Flask initialization')
    app.debug=bool(True)
    logger.info('Flask start')
    app.run(host=APPLICATION_HOST, port=APPLICATION_PORT)
    
