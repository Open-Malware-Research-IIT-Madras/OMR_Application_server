# This is a standard email sender to be deployed on all servers for non-trail mails

from imports import *
import smtplib
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart

# Email server configuration
sender_email = SENDER_EMAIL
sender_password = SENDER_PASSWORD
smtp_server_uri = SMTP_SERVER_URI
smtp_port = 587


BOLD = ""
END = ""

def collect_subject_body(option, msg, jobid, receiver_email, send_to_name):
    jobid = str(jobid)

    if option == 'admin_error_report':
        receiver_email = ['omr@cse.iitm.ac.in']
        subject = (
            "MASTER ALERT!! ERROR!- An error has been thrown, "
            "Please look into it immediately!!"
        )
        body = (
            "This email is meant to inform the Admins that an error has occurred!\n"
            f"The error is -- {BOLD + jobid + END}\n"
            f"The job ID is -- {BOLD + jobid + END}\n"
            f"Job submitter name is -- {BOLD + send_to_name + END}\n"
            "Please look into it immediately.\n\n"
            "OpenMalwareResearch sysmaster"
        )
        return (subject, body, receiver_email)

    elif option == 'user_error_report':
        subject = f"{send_to_name}, Job ID - {jobid} has faced an error in processing"
        body = (
            f"Dear {send_to_name},\n"
            f"We deeply apologize that your job [{BOLD + jobid + END}] could not be processed "
            "and that an error has occurred.\n"
            "Please submit the file again on the website.\n"
            "If this is the second time that you are receiving this message, "
            "then please use the link below to generate an email for us to look into:\n"
            "mailto:omr@cse.iitm.ac.in?subject=%5B{jobid}%5D%20-%20This%20job%20has%20failed%20"
            "processing%20&body=I%20have%20faced%20an%20issue%20during%20the%20processing%20of"
            "%20this%20job.%20Please%20look%20into%20it.%20%0A%0AThanks\n"
            "We again deeply apologize for the inconvenience caused and will resolve your issue "
            "as soon as possible!\n\n"
            "OpenMalwareResearch Team"
        )
        return (subject, body, list(receiver_email))

    elif option == 'job_sent_ack':
        subject = f"{send_to_name}! Your file submission has been received!"
        body = (
            f"Dear {send_to_name},\n"
            "This email is meant to inform you that your file submission has been received!\n\n"
            f"The filename is -- {BOLD + msg + END}\n"
            f"The job ID is -- {BOLD + jobid + END}\n\n"
            "Please keep these in hand for accessing your runtime trails\n"
            "Best Regards,\n"
            "OpenMalwareResearch Team"
        )
        return (subject, body, list(receiver_email))

    elif option == 'send_success_email':
        subject = (
            f"Greetings {send_to_name}! "
            "OpenMalwareResearch has processed your report successfully!"
        )
        body = f'''Dear {send_to_name},

I hope this email finds you well. Please find the runtime trails attached for your review.

-----------------------
Your Job ID -- {jobid}
Your Filehash -- {msg}
-----------------------

Your Download Link -- http://openmalwareresearch.in/OmrUserFileDownload/{msg}.zip

-----------------------
{send_to_name}, please note that you need to download your files within 1 week, 
after which the files will be auto deleted from the server.

We appreciate your continued trust in the Open Malware Research Service. 
If you have any further questions or require additional assistance, feel free to reach out.

Thank you {send_to_name} for choosing our services!

Best regards,  
Team OpenMalwareResearch'''

        return (subject, body, list(receiver_email))

    else:
        raise ValueError("Unknown email option provided.")


def multi_mail(option, msg, job_id, receiver_email, send_to_name=""):
    """
    Sends an email to one or more recipients based on the selected template option.
    """
    subject, body, emails = collect_subject_body(
        option, msg, job_id, receiver_email, send_to_name
    )

    for email in emails:
        try:
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = email
            message['Subject'] = subject
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(smtp_server_uri, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, message.as_string())
                print(f"Successfully mailed to {email}")

        except Exception as e:
            print(f"There is an error in the email script: {e}")
