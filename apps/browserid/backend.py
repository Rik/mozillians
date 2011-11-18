from django.contrib.auth.models import User

import ldap

import commonware.log

from larper import store_assertion, UserSession


log = commonware.log.getLogger('m.browserid')


class SaslBrowserIDBackend(object):
    """Authenticates the user's BrowserID assertion and our audience
    with the LDAP server via the SASL BROWSER-ID authentication
    mechanism."""
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, request=None, assertion=None):
        if request == None or assertion == None:
            return None
        store_assertion(request, assertion)

        directory = UserSession(request)
        login_valid = False
        try:
            (registered, details) = directory.registered_user()
            login_valid = registered
            if registered:
                request.session['unique_id'] = details
            else:
                # TODO, use this on a browserid registration page
                request.session['verified_email'] = details
        except ldap.OTHER, o:
            log.error("LDAP error, clearing session assertion")
            log.error(o)
            store_assertion(request, None)
            # such as stale assertion - timeout
        except Exception, e:
            log.error("Unknown error, clearing session assertion")
            log.error(e)
            store_assertion(request, None)

        if login_valid:
            try:
                person = directory.get_by_unique_id(details)
                user = User.objects.get(username=person.username)
            except User.DoesNotExist:
                # TODO aok - do we want this to happen from registration only?
                log.info("Mirroring user data into DB for metrics")
                user = User(username=person.username,
                            first_name=person.first_name,
                            last_name=person.last_name,
                            email=person.username)
                user.set_unusable_password()
                user.is_active = True
                user.is_staff = False
                user.is_superuser = False
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            log.debug("No user found")
            return None
