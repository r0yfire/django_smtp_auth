import smtplib

from django.conf import settings
from django.contrib.auth.models import User


EMAIL_HOST = settings.EMAIL_HOST # Django default setting
EMAIL_USE_TLS = settings.EMAIL_USE_TLS # Django default setting
SMTP_AUTH_HOST = getattr(settings, 'SMTP_AUTH_HOST', None) # smtp_auth setting
SMTP_AUTH_USE_TLS = getattr(settings, 'SMTP_AUTH_USE_TLS', None) # smtp_auth setting

class SMTPBackend(object):
    """
    Authenticates against an SMTP server
    """
    supports_inactive_user = True
    
    def authenticate(self, username=None, password=None):
        #
        # SMTP Authentication
        #
        if SMTP_AUTH_HOST:
            srv = smtplib.SMTP(SMTP_AUTH_HOST)
        else:
            srv = smtplib.SMTP(EMAIL_HOST)
            
        if SMTP_AUTH_USE_TLS is not None:
            if SMTP_AUTH_USE_TLS:
                srv.starttls()
        else:
            if EMAIL_USE_TLS:
                srv.starttls()
        
        status_code = srv.login(username, password)
        srv.quit()
        if status_code[0] in [235, 503]:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                return User.objects.create_user(username, username, password)
        else:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
                else:
                    return None
            except User.DoesNotExist:
                return None
