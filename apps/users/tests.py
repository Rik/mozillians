from django.core import mail
from django.contrib.auth.models import User

from funfactory.urlresolvers import reverse
from nose.tools import eq_
from pyquery import PyQuery as pq

from groups.models import Group
from phonebook.tests import LDAPTestCase, PENDING


Group.objects.get_or_create(name='staff', system=True)

class TestThingsForPeople(LDAPTestCase):
    """Verify that the wrong users don't see things."""

    def test_searchbox(self):
        url = reverse('home')
        r = self.client.get(url)
        doc = pq(r.content)
        assert not doc('input[type=search]')
        r = self.pending_client.get(url)
        doc = pq(r.content)
        assert not doc('input[type=search]')
        r = self.mozillian_client.get(url)
        doc = pq(r.content)
        assert doc('input[type=search]')

    def test_invitelink(self):
        url = reverse('home')
        r = self.client.get(url)
        doc = pq(r.content)
        assert not doc('a#invite')
        r = self.pending_client.get(url)
        doc = pq(r.content)
        assert not doc('a#invite'), "Unvouched can't invite."
        r = self.mozillian_client.get(url)
        doc = pq(r.content)
        assert doc('a#invite')

    def test_register_redirects_for_authenticated_users(self):
        """Ensure only anonymous users can register an account."""
        r = self.client.get(reverse('home'))
        self.assertTrue(200 == r.status_code,
                        'Anonymous users can access the homepage to begin registration flow')

        r = self.mozillian_client.get(reverse('register'))
        eq_(302, r.status_code,
            'Authenticated users are redirected from registration.')

    def test_vouchlink(self):
        """No vouch link when PENDING looks at PENDING."""
        url = reverse('profile', args=[PENDING['uniq_id']])
        r = self.mozillian_client.get(url)
        doc = pq(r.content)
        assert doc('#vouch-form button')
        r = self.pending_client.get(url)
        doc = pq(r.content)
        errmsg = 'Self vouching... silliness.'
        assert not doc('#vouch-form button'), errmsg
        assert 'Vouch for me' not in r.content, errmsg

def get_profile(email):
    """Get a UserProfile for a particular user."""
    return User.objects.get(email=email).get_profile()
