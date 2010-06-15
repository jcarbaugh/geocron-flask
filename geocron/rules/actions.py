import smtplib
import urllib
from email.mime.text import MIMEText

carrier_emails = {
                    'att': 'txt.att.net',
                    'alltel': 'message.alltel.com',
                    'bell': 'txt.bell.ca',
                    'boost': 'myboostmobile.com',
                    'cellularone': 'mobile.celloneusa.com',
                    'comcast': 'comcastpcs.textmsg.com',
                    'edge': 'sms.edgewireless.com',
                    'helio': 'messaging.sprintpcs.com',
                    'metropcs': 'mymetropcs.com',
                    'nextel': 'messaging.nextel.com',
                    'sprint': 'messaging.sprintpcs.com',
                    'tmobile': 'tmomail.net',
                    'tracfone': 'txt.att.net',
                    'verizon': 'vtext.com',
                    'virgin': 'vmobl.com'
                 }


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
        msg['Subject'] = 'message from %s' % email
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

def execute_sms(email, **rule):

    if rule.has_key('phone_number') and rule.has_key('phone_carrier') and rule.has_key('sms'):
        rule['email_address'] = "%s@%s" % (rule['phone_number'], carrier_emails[rule['phone_carrier']])
        rule['email_text'] = rule['sms']
        execute_email(email, **rule)

    else:
        raise DataError('This rule has no phone number, carrier, or message to send')
