from fileinput import filename
import smtplib
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

_FROM = 'daedae11@126.com'
_user_name = _FROM
_passport = 'LXMBVYEJYOEJEGLW'
_TO = _FROM


def send_html_as_attachment(title, html):
    email = EmailMessage()
    email['Subject'] = title
    email['From'] = _FROM
    email['To'] = _TO
    email.add_attachment(
        html.encode('utf-8'), maintype='application',
        subtype='octet-stream', filename='data.html')
    with smtplib.SMTP_SSL('smtp.126.com', 465) as smtp:
        smtp.login(_user_name, _passport)
        smtp.send_message(email)


def send_html(title, html):
    email = EmailMessage()
    email['Subject'] = title
    email['From'] = _FROM
    email['To'] = _TO
    email.set_content(html, subtype='html')
    # email.add_attachment(
    #     html.encode('utf-8'), maintype='application',
    #     subtype='octet-stream', filename='data.html')
    with smtplib.SMTP_SSL('smtp.126.com', 465) as smtp:
        smtp.login(_user_name, _passport)
        smtp.send_message(email)
