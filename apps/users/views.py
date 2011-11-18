import datetime
import ldap

from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.contrib import auth
from django.core.mail import send_mail

import commonware.log
from funfactory.urlresolvers import reverse
from tower import ugettext as _

from larper import RegistrarSession, get_assertion
from phonebook.models import Invite
from session_csrf import anonymous_csrf
from users import forms
from users.models import UserProfile

log = commonware.log.getLogger('m.users')

get_invite = lambda c: Invite.objects.get(code=c, redeemed=None)


class Anonymous:
    def __init__(self):
        self.unique_id = 0


def _send_confirmation_email(user):
    """This sends a confirmation email to the user."""
    subject = _('Confirm your account')
    message = (_("Please confirm your Mozillians account:\n\n %s") %
               user.get_profile().get_confirmation_url())
    send_mail(subject, message, 'no-reply@mozillians.org', [user.username])


def send_confirmation(request):
    user = request.GET['user']
    user = get_object_or_404(auth.models.User, username=user)
    _send_confirmation_email(user)
    return render(request, 'users/confirmation_sent.html')


def confirm(request):
    """Confirms a user.

    1. Recognize the code or 404.
    2. On recognition, mark user as confirmed.
    """
    code = request.GET['code']
    profile = get_object_or_404(UserProfile, confirmation_code=code)
    profile.is_confirmed = True
    profile.save()
    return render(request, 'users/confirmed.html')


@anonymous_csrf
def register(request):
    """ TODO... ?code=foo to pre-vouch
    Maybe put it into the session?
    """
    # Legacy URL shenanigans - A GET to register with invite code
    # is a legal way to start the BrowserID registration flow.

    if 'code' in request.GET:
        request.session['invite-code'] = request.GET['code']
        return redirect('home')

    if request.user.is_authenticated():
        return redirect(reverse('profile', args=[request.user.unique_id]))

    if not 'verified_email' in request.session:
        log.error("Browserid registration, but no verified email in session")
        return redirect('home')

    email = request.session['verified_email']

    intent = 'register'

    # Check for optional invite code
    initial = {}
    if 'invite-code' in request.session:
        code = request.session['invite-code']
        try:
            invite = get_invite(code)
            initial['email'] = invite.recipient
            initial['code'] = invite.code
        except Invite.DoesNotExist:
            log.warning('Bad register code [%s], skipping invite' % code)

    form = forms.RegistrationForm(request.POST or None, initial=initial)

    if request.method == 'POST':
        if form.is_valid():
            try:
                uniq_id = _save_new_user(request, form)
                return redirect('profile', uniq_id)
            except ldap.CONSTRAINT_VIOLATION:
                log.error("User already exists")
                _set_already_exists_error(form)
    else:
        if 'link' in request.GET:
            intent = request.GET['link']
    anonymous = Anonymous()

    return render(request, 'phonebook/edit_profile.html',
                  dict(form=form,
                       edit_form_action=reverse('register'),
                       person=anonymous,
                       mode='new',
                       email=email,
                       intent=intent))


def password_reset_confirm(request, uidb36=None, token=None):
    """Legacy URL, keep around until 1.4 release."""
    return redirect('home')


def _save_new_user(request, form):
    """
    form - must be a valid form

    We persist account to LDAP. If all goes well, we
    log the user in and persist their BID assertion to the
    session.
    """
    # Email in the form is the "username" we'll use.
    email = request.session['verified_email']
    username = email

    registrar = RegistrarSession.connect(request)

    code = None
    if 'invite-code' in request.session:
        code = request.session['invite-code']

    d = form.cleaned_data
    d['email'] = email
    uniq_id = registrar.create_person(d)
    voucher = None

    if code:
        try:
            invite = get_invite(code)
            voucher = invite.inviter
        except Invite.DoesNotExist:
            msg = 'Bad code in form [%s], skipping pre-vouch' % d['code']
            log.warning(msg)

    if voucher:
        registrar.record_vouch(voucher=voucher, vouchee=uniq_id)
        invite.redeemed = datetime.datetime.now()
        invite.redeemer = uniq_id
        invite.save()
    # auto vouch moz.com:
    elif any(username.endswith('@' + x) for x in settings.AUTO_VOUCH_DOMAINS):
        registrar.record_vouch(voucher='ZUUL', vouchee=uniq_id)

    # we need to authenticate them... with their assertion
    assrtn_hsh, assertion = get_assertion(request)
    user = auth.authenticate(request=request, assertion=assertion)

    # Should never happen
    if not user or not user.is_authenticated():
        msg = 'Authentication for new user (%s) failed' % username
        # TODO: make this a unique exception.
        raise Exception(msg)
    else:
        log.info("Logging user in")
        auth.login(request, user)

    return uniq_id


def _set_already_exists_error(form):
    msg = _('Someone has already registered an account with %(email)s.')
    data = dict(email=form.cleaned_data['email'])
    del form.cleaned_data['email']
    error = _(msg % data)
    form._errors['email'] = form.error_class([error])
