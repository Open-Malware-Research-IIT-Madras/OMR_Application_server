"""
Module Name: email_config.py

Description:
    Provides functionality to send processed malware report results via
    email. Builds a message with subject, body, and file attachments,
    then sends it through Gmail’s SMTP server using TLS.

Functions:
    direct_mail_sent(emails, file_hash):
        Sends an email with a processed report (.txt file) attached to
        the given recipient address. Uses Gmail SMTP for delivery.

Classes:
    None defined in this file.

Usage:
    Call direct_mail_sent() with the recipient email and file hash:
        direct_mail_sent("user@example.com", "hash123")

Author:
    Allan Pais
"""

from app_config import *

def direct_mail_sent(emails,file_hash):


    subject=f"Greetings {emails}! Open Malware Research has processed your report!"

    body=f'''Dear {emails},

    I hope this email finds you well. Please find the runtime trails attached for your review.
    We appreciate your continued trust in the Open Malware Research Service. If you have any further questions or require additional assistance, feel free to reach out.
    Thank you for choosing our services.

    Best regards,
    OpenMalwareResearch'''

    sender_email="allan.n.pais@gmail.com"
    password='fgyy axcd depv vexe'
    smtp_server='smtp.gmail.com'
    smtp_port=587

    message = MIMEMultipart()
    message['Subject']=subject
    message['From']=sender_email
    message['To']=emails 

    files=[f'/home/omrapp/Desktop/reporthash/{file_hash}.txt']

    message.attach(MIMEText(body))

    for f in files :
            with open(f, "rb") as fil:
                part = MIMEApplication(
                fil.read(),
                Name=basename(f)
                )
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            message.attach(part)

    smtp = smtplib.SMTP(smtp_server, 587)
    smtp.starttls()
    smtp.login(sender_email,password)
    smtp.sendmail(sender_email, emails, message.as_string())
    smtp.close()
    print("Email Sent!")