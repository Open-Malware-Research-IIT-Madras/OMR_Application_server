from imports import *
from apikey import *

logging.basicConfig(
    level=logging.DEBUG,
    format='APP_SERVER: %(asctime)s, %(name)s, %(module)s, %(funcName)s, %(lineno)s, %(levelname)s, %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filemode='w',
    filename='/var/log/omr/omr_webapp_logs.log'
)
logger = logging.getLogger(__name__)
logger.info('Logging Starts')

# Flask app configuration
logger.info('Flask config start')
app = Flask(__name__)
cache=Cache(app, config={'CACHE_TYPE':'SimpleCache'})


try:
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config["SESSION_PERMANENT"] = False
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=10)
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB max upload before desk reject.
    CORS(app)

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config['UPLOAD_FOLDER'] = '/home/omrapp/Desktop/filehash/'
    app.config['UPLOAD_EXTENSIONS'] = ['exe', 'elf', 'apk']

    app.config['DEBUG'] = True
    app.config['TESTING'] = False

    # Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'omr@cse.iitm.ac.in'
    app.config['MAIL_SENDER'] = 'omr@cse.iitm.ac.in'
    app.config['MAIL_PASSWORD'] = 'wzxy vgmz wloo gape'
    app.config['MAIL_DEFAULT_SENDER'] = None
    app.config['MAIL_MAX_EMAILS'] = None
    app.config['MAIL_ASCII_ATTACHMENTS'] = False

    app.config['SECRET_KEY'] = SECRET_KEY

    logger.info('Flask config end')

except Exception as e:
    logger.error('Flaskapp configuration error', e)

# OAuth configuration
logger.info('OAuth config start')
oauth = OAuth(app)

try:
    google = oauth.register(
        name='google',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        server_metadata_url=SERVER_METADATA_URI,
        client_kwargs=CLIENT_KWARGS,
    )
    logger.info('OAuth config end')

except Exception as e:
    logger.error('OAuth config error', e)

# PostgreSQL configuration
try:
    logger.info('PostgreSQL config start')
    connection = psycopg2.connect(
        database=POSTGRESQL_DATABASE_NAME,
        host=POSTGRESQL_HOSTNAME,
        port=5432,
        user=POSTGRESQL_USERNAME,
        password=POSTGRESQL_PASSWORD,
    )
    cursor = connection.cursor()
    connection.autocommit = True
    logger.info('PostgreSQL config end')

except Exception as e:
    logger.error('PostgreSQL config error', e)

# RabbitMQ configuration
try:
    logger.info('RabbitMQ config start')
    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    connection2 = pika.BlockingConnection(
        pika.ConnectionParameters(RABBITMQ_IP, 5672, '/', credentials)
    )
    logger.info('RabbitMQ config end')

except Exception as e:
    logger.error('RabbitMQ config error', e)

