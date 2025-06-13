"""
-----------------------------------@INFO---------------------------------
Author        : Allan Pais
Created On    : [Insert Date]
Filename      : [Insert Filename]

Description   : 
This module contains the function `error_mail`, which is responsible 
for sending email notifications based on various operational scenarios.

Function Signature:
    error_mail(option, msg, job_id, receiver_email, receiver_name)

Supported Email Categories:
    - admin_error_report : For reporting critical system/admin-level errors.
    - job_sent_ack       : Acknowledgment email after a job is successfully sent.
    - user_error_report  : For reporting user-level or job-specific errors.

Usage Notes:
- The function handles email construction, formatting, and sending.
- Email templates may be customized based on the `option` parameter.

Dependencies:
- 
--------------------------------------------------------------------
"""
import pika
import json
import os
import psycopg2
import smtplib
from imports import *
from pradar import network_scripts_production_ready, os_scripts_production_ready
from multipurpose_email import *
from database_config import *

# Constants
RETRY_LIMIT = 3
sender_email = "omr@cse.iitm.ac.in"
password = 'wzxy vgmz wloo gape'
smtp_server = 'smtp.gmail.com'

# RabbitMQ credentials and connection setup
credentials = pika.PlainCredentials('OMR_RMQ', 'Omr@123')
connection2 = pika.BlockingConnection(
    pika.ConnectionParameters('172.23.254.74', 5672, '/', credentials)
)

# PostgreSQL connection setup
connection1 = psycopg2.connect(
    database="omrdatabase",
    host="172.23.254.74",
    port=5432,
    user="omruser",
    password="Omr@123"
)
cursor = connection1.cursor()
connection1.autocommit = True

# Retry tracker
current_retries = 0


def on_message_received(ch, method, properties, body):
    """Callback when a message is received from the queue."""

    logger.info('Email function has received a message')

    # Save RabbitMQ channel state
    channel = ch
    channel_method = method
    channel_body = body
    channel_properties = properties

    global current_retries
    global RETRY_LIMIT

    # Load message data
    json_value = json.loads(body)
    report_file_name = json_value["File_uuid"]
    job_id = json_value["Jobid"]

    # Fetch user information
    enterTH(job_id, report_file_name)
    user_ids = getUIDS(job_id)
    email_id = getEmail(user_ids)

    logger.info(
        f'Email function has processed a message: {report_file_name} - '
        f'{job_id} - {user_ids} - {email_id}'
    )

    user_names_list = []

    logger.info('Starting the RaDAR purification')
    print("Starting the RaDAR purification")
    logger.info('Compiling the OS + Network files')
    print("Compiling the OS + Network files")

    # Change file permissions for OS and network logs
    try:
        os.system(
            f"echo jug@@d*%$ | sudo -s chmod 777 "
            f"/home/omrapp/Desktop/reporthash/returned_os_logs/{report_file_name}.csv"
        )
        os.system(
            f"echo jug@@d*%$ | sudo -s chmod 777 "
            f"/home/omrapp/Desktop/reporthash/returned_network_logs/trafficLogs/eno1_{report_file_name}.pcap"
        )
    except Exception as e:
        logger.error('Permission changing error for returned trails', e)

    logger.info('Changed file permissions for the returned pcap[NETWORK] and csv[OS] files')

    try:
        # Run RaDAR processing scripts
        network_scripts_production_ready.zeek_process(report_file_name)
        os_scripts_production_ready.os_scripts(report_file_name)

        logger.info('Ended the RaDAR processing')
        print("Ended the RaDAR purification")

        # Change permissions of processed output
        os.system(
            f"echo jug@@d*%$ | sudo -s chmod 777 "
            f"/home/omrapp/Desktop/reporthash/radar_processed_ostrails_{report_file_name}.csv"
        )
        os.system(
            f"echo jug@@d*%$ | sudo -s chmod 777 "
            f"/home/omrapp/Desktop/reporthash/radar_processed_networktrails_{report_file_name}.csv"
        )

        # Create ZIP archive of logs
        os.system(
            f"zip -j /home/omrapp/Desktop/reporthash/radar_processed_{report_file_name}.zip "
            f"/home/omrapp/Desktop/reporthash/radar_processed_ostrails_{report_file_name}.csv "
            f"/home/omrapp/Desktop/reporthash/radar_processed_networktrails_{report_file_name}.csv "
            f"/home/omrapp/Desktop/reporthash/returned_os_logs/{report_file_name}.csv "
            f"/home/omrapp/Desktop/reporthash/returned_network_logs/trafficLogs/eno1_{report_file_name}.pcap"
        )

        # Clean up intermediate CSV files
        os.system("rm /home/omrapp/Desktop/reporthash/*.csv")

        print("The user ids are", user_ids)

        # Fetch usernames for each user ID
        for x in user_ids:
            uname = str(x)
            print(uname)
            user_names_list.append(getUserName(uname))

        # Send success email to each user
        for email, user in zip(email_id, user_names_list):
            email = email.split()
            print("Usertype:", type(user[0]))
            print("Sending success email:", report_file_name, job_id, email, user[0])
            multi_mail("send_success_email", report_file_name, job_id, list(email), str(user[0]))

        # Acknowledge message consumption
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("There has been an error ---", e)
        logger.error('There has been an error while sending the email', e)

        # Specific case: missing logs
        if e == "NoZeekLogs":
            logger.error(f'No zeek logs found for Job ID {job_id}')
            print(f'No zeek logs found for Job ID {job_id}')
            channel.basic_ack(delivery_tag=channel_method.delivery_tag)
            return

        # Retry logic
        current_retries += 1
        if current_retries <= RETRY_LIMIT:
            time.sleep(10)
            print(f"Email Server Retry triggered. Retry No: {current_retries}")
            logger.warning(
                f'Email Server Error for Job ID {job_id} - Retry No: {current_retries}'
            )
            on_message_received(channel, channel_method, channel_properties, channel_body)
        else:
            print("Skipping emailing the trails and logging error")
            logger.info('Skipping emailing the trails and logging error')
            print("Error Info (JSON):", json_value)
            logger.info('Error Info (JSON):', json_value)

            # Notify admin and user of the failure
            for email, user in zip(email_id, user_names_list):
                email = email.split()
                logger.info(
                    f'Sending error message to Admin and user: {job_id} - {email} - {str(user[0])}'
                )
                multi_mail('admin_error_report', json_value, job_id, None, str(user[0]))
                multi_mail('user_error_report', 'Error', job_id, email, str(user[0]))

            logger.info(f'There has been an error in the job: {job_id}')
            channel.basic_ack(delivery_tag=channel_method.delivery_tag)


# RabbitMQ consumer setup
channel = connection2.channel()
channel.queue_declare("queue_2")
channel.basic_consume(
    queue='queue_2',
    auto_ack=False,
    on_message_callback=on_message_received
)

print("Starting the sending of emails")
logger.info('Starting the sending of Trail emails')

# Begin consuming messages
channel.start_consuming()
