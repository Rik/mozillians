import datetime
import ldap

from django import http
from django.shortcuts import redirect
from django.contrib import auth
from django.contrib.auth.tokens import default_token_generator

import commonware.log
import jingo
from tower import ugettext as _

from larper import RegistrarSession, get_assertion
from phonebook.models import Invite
from session_csrf import anonymous_csrf
from users import forms
from funfactory.urlresolvers import reverse

log = commonware.log.getLogger('m.users')

get_invite = lambda c: Invite.objects.get(code=c, redeemed=None)

class Anonymous:
    def __init__(self):
        self.unique_id = 0


@anonymous_csrf
def register(request):
    """ TODO... ?code=foo to pre-vouch 
    Maybe put it into the session?
    """
    intent = 'register'

    if 'code' in request.GET:
        code = request.GET['code']
        try:
            invite = get_invite(code)
            initial['email'] = invite.recipient
            initial['code'] = invite.code
        except Invite.DoesNotExist:
            log.warning('Bad register code [%s], skipping invite' % code)

    if not 'verified_email' in request.session:
        log.error("Browserid registration, but no verified email in session")
        return redirect('home')
    email = request.session['verified_email']
    initial = {}

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

    return jingo.render(request, 'phonebook/edit_profile.html',
                        dict(form=form, person=anonymous, mode='new', email=email, intent=intent))


def password_change(request):
    """
    View wraps django.auth.contrib's password_change view, so that
    we can override the form as well as logout the user.
    """
    r = auth.views.password_change(request,
                                   'registration/password_change_form.html',
                                   reverse('login'),
                                   forms.PasswordChangeForm)
    # Our session has the old password.
    if isinstance(r, http.HttpResponseRedirect):
        auth.logout(request)
    return r


def password_reset(request):
    """
    View wraps django.auth.contrib's password_reset view, so that
    we can override the form.
    """
    r = auth.views.password_reset(request,
                                  False,
                                  'registration/password_reset_form.html',
                                  'registration/password_reset_email.html',
                                  'registration/password_reset_subject.txt',
                                  forms.PasswordResetForm,
                                  default_token_generator,
                                  reverse('password_reset_check_mail'))
    return r


def password_reset_confirm(request, uidb36=None, token=None):
    """
    View wraps django.auth.contrib's password_reset_confirm view, so that
    we can override the form.
    """
    r = auth.views.password_reset_confirm(
        request,
        uidb36,
        token,
        'registration/password_reset_confirm.html',
        default_token_generator,
        forms.SetPasswordForm,
        reverse('login'))
    return r


def password_reset_check_mail(request):
    return jingo.render(
        request,
        'registration/password_reset_check_mail.html',
        dict())


def _save_new_user(request, form):
    """
    form - must be a valid form

    We persist account to LDAP. If all goes well, we
    log the user in and persist their password to the session.
    """
    # Email in the form is the "username" we'll use.
    email = request.session['verified_email']
    username = email

    registrar = RegistrarSession.connect(request)

    d = form.cleaned_data
    d['email'] = email
    uniq_id = registrar.create_person(d)
    voucher = None

    if d['code']:
        try:
            invite = get_invite(d['code'])
            voucher = invite.inviter
        except Invite.DoesNotExist:
            msg = 'Bad code in form [%s], skipping pre-vouch' % d['code']
            log.warning(msg)

    if voucher:
        registrar.record_vouch(voucher=voucher, vouchee=uniq_id)
        invite.redeemed = datetime.datetime.now()
        invite.redeemer = uniq_id
        invite.save()

    # we need to authenticate them... with their assertion
    assertion = get_assertion(request)
    user = auth.authenticate(request=request, assertion=assertion)
    auth.login(request, user)

    return uniq_id


def _set_already_exists_error(form):
    msg = _('Someone has already registered an account with %(email)s.')
    data = dict(email=form.cleaned_data['email'])
    del form.cleaned_data['email']
    error = _(msg % data)
    form._errors['username'] = form.error_class([error])
