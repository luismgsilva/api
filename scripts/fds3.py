import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

text_file_path = sys.argv[1]
attachment_path = sys.argv[2]
with open(text_file_path, "r") as file:
  email_body = file.read()

subject = "Email Subject"
body = "This is the body of the text message"
body = email_body
sender = "bsf.ci.noreply@gmail.com"
recipients = ["luiss@synopsys.com", "luis.m.silva99@hotmail.com", "linun77@gmail.com"]
cc_recipients = ["luiss@synopsys.com"]
password = "xvscfirnoipabpff"


def send_email(subject, body, sender, recipients, password, attachment_path):
    #msg = MIMEText(body, "plain")
    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg['Cc'] = ', '.join(cc_recipients)
  
    plain_text = "ai"
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(body, "html"))
  
    if attachment_path:
      with open(attachment_path, "rb") as attachment_file:
        attachment = MIMEApplication(attachment_file.read())
        attachment.add_header("Content-Disposition", "attachment", filename=attachment_path)
        msg.attach(attachment)
    
    with smtplib.SMTP_SSL('localhost', 2525) as smtp_server:
      smtp_server.login(sender, password)
      all_recipients = recipients + cc_recipients
      smtp_server.sendmail(sender, all_recipients, msg.as_string())
    print("Message sent!")


send_email(subject, body, sender, recipients, password, attachment_path)
