import ldap


from django.contrib import auth
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

import commonware.log
from funfactory.urlresolvers import reverse
from funfactory.utils import absolutify
#from django_browserid.forms import BrowserIDForm
from session_csrf import anonymous_csrf

from browserid.forms import ModalBrowserIdForm
from larper import store_assertion, UserSession


log = commonware.log.getLogger('m.browserid')

# I think I need to write a backend auth package.
# Consider renaming this app to sasl-browserid
# Follow django-browserid's user creation 

# login should redirect to register and say "shout@ozten.com" is 
# an unknown account, would you like to create one?

@require_POST
def browserid_login(request):
    """Handles login and register browserid verification. If
    the mode is login, we are done. If the mode is register
    then we start new profile flow. Also handles corner cases.

    Login and register sasl-browserid verification steps are very similar
    and the corner cases blur the lines, so this is best as one
    url.

    We use contextprocessor, form, and ??? from django-browserid,
    but since the LDAP server does the BrowserID auth behind the
    scenes, we don't use it's auth code nor it's views."""
    form = ModalBrowserIdForm(data=request.POST)
    if form.is_valid():
        log.debug("form looks good, doing authentication")
        assertion = form.cleaned_data['assertion']
        mode = form.cleaned_data['mode']
        log.debug("mode=%s assertion=%s" % (mode, assertion))
        #auth.logout(request)
        user = auth.authenticate(request=request, assertion=assertion)
        # DO we need a retry page?
        if user:
            auth.login(request, user)
            return redirect('profile', request.user.unique_id)
        else:
            url = absolutify("%s?link=%s" % (reverse('register'), mode))
            return redirect(url)
    else:
        # raise 500?
        log.debug("Form didn't validate %s" % str(request.POST))


def browserid_register(request):
    """TODO registration w/o passwords"""
    if request.session['verified_email']:
        asdf
    else:
        log.error("Browserid registration, but no verified email in session")
        return redirect('home')
