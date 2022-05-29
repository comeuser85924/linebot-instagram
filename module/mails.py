import sys
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def mails(txt):
    content = MIMEMultipart()
    content["subject"] = "[BUG] Instagram 小幫手" 
    content["from"] = os.environ['from_email']
    content["to"] =  os.environ['to_email']
    content.attach(MIMEText(txt))

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo() 
            smtp.starttls()
            smtp.login(os.environ['from_email'], os.environ['from_mail_pw'])
            smtp.send_message(content)
            print("Email Complete!")
        except Exception as e:
            print("Email error message: ", e)

sys.modules[__name__] = mails