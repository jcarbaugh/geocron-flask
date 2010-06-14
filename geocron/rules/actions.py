import smtplib
from email.mime.text import MIMEText


def execute_action(email, **rule):

    if rule.has_key('action_type'):
        try:
            globals()['execute_'+rule['action_type']](email, **rule)
        except KeyError:
            print "no function"
    else:
        print 'no action'

def execute_email(email, **rule):

    if rule.has_key('email_address') and rule.has_key('email_text'):
        msg = MIMEText(rule['email_text'])
        msg['Subject'] = 'message from geocron'
        msg['From'] = email
        msg['To'] = rule['email_address']
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login('geocron.us', 'bloodmonkey')
        s.sendmail(email, [rule['email_address']], msg.as_string())
        s.quit()

    else: 
        print "no email address or text"
