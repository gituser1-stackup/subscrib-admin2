import smtplib, sys, json, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate


def read_json(filename):
    with open(filename, 'r') as template_file:
        file_content = json.loads(template_file.read().encode('utf-8'))
    return file_content

BASE_DIR = os.getcwd() + '/users'
def mail(to_address, username, purpose, hciId=None, link=None, app=None, grace=None, start=None, end=None, companyName=None):
    try:
        mail = read_json(BASE_DIR + '/mail_config.json')
        # set up the SMTP server
        if int(mail['mails']['mail_server_out_port']) == 587:
            s = smtplib.SMTP(host=str(mail['mails']['mail_server']), port=int(mail['mails']['mail_server_out_port']))
            s.ehlo()
            s.starttls()
        else:
            s = smtplib.SMTP_SSL(host=str(mail['mails']['mail_server']),
                                 port=int(mail['mails']['mail_server_out_port']))
        # s.set_debuglevel(1)
        s.login(mail['mails']['mail_from'], mail['mails']['mail_password'])
        msg = MIMEMultipart()  # create a message

        # setup the parameters of the message
        msg['From'] = mail['mails']['mail_user']
        msg['Subject'] = mail[purpose]["subject"]

        # add in the message body
        html = open(BASE_DIR+mail[purpose]["message"],'r').read()
        mail_body = html.format(mail_info=mail[purpose]["mail_info"],username=username, link=link, purpose=mail[purpose]["type"], hciId=hciId, app=app, grace=grace, start=start, end=end, to_address=to_address, companyName=companyName)
        msg.attach(MIMEText(mail_body,"html"))

        # send the message via the server set up earlier.
        msg['To'] = to_address
        s.sendmail(mail['mails']['mail_from'], msg['To'], msg.as_string())

        del msg

        # Terminate the SMTP session and close the connection
        s.quit()

        return True
    except Exception as err:
        print(err)
        return False