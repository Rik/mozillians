from django.core import mail
from django.contrib.auth.models import User

from nose.tools import eq_
from pyquery import PyQuery as pq

from funfactory.urlresolvers import reverse
from phonebook.models import Invite
from phonebook.tests import LDAPTestCase


class InviteTest(LDAPTestCase):
    def invite_someone(self, email):
        """
        This method will invite a user.

        This will verify that an email with link has been sent.
        """
        # Send an invite.
        url = reverse('invite')
        d = dict(recipient=email)
        r = self.mozillian_client.post(url, d, follow=True)
        eq_(r.status_code, 200)
        assert ('mr.fusion@gmail.com has been invited to Mozillians.' in
                pq(r.content)('div#main-content p').text())

        # See that the email was sent.
        eq_(len(mail.outbox), 1)

        i = Invite.objects.get()
        invite_url = i.get_url()

        assert 'no-reply@mozillians.org' in mail.outbox[0].from_email
        assert invite_url in mail.outbox[0].body, "No link in email."
        return i

    def get_register(self, invite):
        r = self.client.get(invite.get_url(), follow=True)
        eq_(self.client.session['invite-code'], invite.code)
        return r

    def redeem_invite(self, invite, **kw):
        """Given an invite_url go to it and redeem an invite."""
        # Now let's look at the register form.
        self.client.logout()
        d = kw

        # Login
        login_d = dict(assertion=d['assertion'],
                       email=d['email'],
                       mode='register')

        # first time we hit /register
        self.client.get(invite.get_url(), follow=True)
        self.client.post(reverse('browserid_login'), login_d, follow=True)

        # Now let's register
        d.update(
                first_name='Akaaaaaaash',
                last_name='Desaaaaaaai',
                optin=True
                )

        r = self.client.post(reverse('register'), d, follow=True)

        u = User.objects.filter(email=d['email'])[0].get_profile()
        u.is_confirmed = True
        u.save()

        return r

    def test_send_invite_flow(self):
        """
        Test the invitation flow.

        Send an invite.  See that email is sent.
        See that link allows us to sign in and be auto-vouched.
        Verify that we can't reuse the invite_url
        Verify we can't reinvite a vouched user
        """
        email = 'mr.fusion@gmail.com'
        assertion = 'mrfusionsomereallylongstring'
        invite = self.invite_someone(email)
        d = dict(assertion=assertion, email=email, mode='register')

        r = self.get_register(invite)
        r = self.redeem_invite(invite, **d)

        uniq_id = r.context['user'].unique_id
        r = self.client.get(reverse('profile', args=[uniq_id]))

        eq_(r.context['user'].unique_id,
            Invite.objects.get(pk=invite.pk).redeemer)

        eq_(r.context['user'].get_profile().is_vouched, True)

        # Don't reuse codes.
        r = self.redeem_invite(invite, assertion='mr2reallylongstring',
                               email='mr2@gmail.com')
        eq_(r.context['user'].get_profile().is_vouched, False)

    def test_unvouched_cant_invite(self):
        """
        Let's make sure the unvouched don't let in their friends...

        Their stupid friends...
        """
        url = reverse('invite')
        d = dict(recipient='mr.fusion@gmail.com')
        r = self.pending_client.post(url, d, follow=True)
        eq_(r.status_code, 403)
