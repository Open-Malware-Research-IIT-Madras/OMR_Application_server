#!/home/omrapp/Desktop/Jugaad_testV1/bin/python
#Location of the virtual environment 

from apikey import *
from imports import *
from database_config import *
from controller_config import *
from email_config import *
from app_config import *



if __name__=="__main__":
   
    logger.info('Flask initialization')
    app.debug=bool(DEBUG)
    logger.info('Flask start')
    app.run(host=APPLICATION_HOST, port=APPLICATION_PORT)
    
