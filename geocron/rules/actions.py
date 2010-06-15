import smtplib
import urllib
from email.mime.text import MIMEText

class DataError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

def execute_action(email, **rule):

    if rule.has_key('action_type'):
        try:
            globals()['execute_'+rule['action_type']](email, **rule)
        except KeyError:
            raise Exception('No function defined for this action type')
    else:
        raise DataError('No action type defined for this rule')

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
        raise DataError('No email address or email text is defined for this rule')

def execute_webhook(email, **rule):
    
    if rule.has_key('callback_url') and rule.has_key('method'):
        response = urllib.urlopen(rule['callback_url'], data=rule['method'])

    else:
        raise DataError('This rule has no callback url or method')

