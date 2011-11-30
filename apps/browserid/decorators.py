from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required

def browserid_login_required(function=None,
                             redirect_field_name=REDIRECT_FIELD_NAME,
                             login_url='/'):
    """BrowserID sepcific login_required decorator.

    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    return login_required(function=function,
                          redirect_field_name=redirect_field_name,
                          login_url=login_url)
