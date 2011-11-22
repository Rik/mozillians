from ldap.sasl import CB_USER, CB_AUTHNAME, sasl as Sasl


class Credentials(Sasl):
    """This class handles SASL BROWSER-ID authentication."""

    def __init__(self, assertion, audience):
        """Prepares credentials for LDAP/sasl bind.

        Prepares assertion and audience to be used
        as the ``CB_USER`` and ``CB_AUTHNAME`` fields of a
        sasl interactive LDAP bind.
        """
        auth_dict = {CB_USER: assertion,
                     CB_AUTHNAME: audience}
        Sasl.__init__(self, auth_dict, 'BROWSER-ID')
