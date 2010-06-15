from geocron.web import application
from geocron import settings

if not settings.DEBUG:
    
    import logging
    
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler(settings.SMTP_HOST,
                               'geocron.us@gmail.com',
                               settings.ADMINS,
                               'Our application failed',
                               (settings.SMTP_USER, settings.SMTP_PASSWORD))
    mail_handler.setLevel(logging.ERROR)
    application.logger.addHandler(mail_handler)
    
    from logging.handlers import FileHandler
    file_handler = FileHandler("/tmp/geocron.log")
    file_handler.setLevel(logging.WARNING)
    application.logger.addHandler(file_handler)

applications = {
    '/': application,
}