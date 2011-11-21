from ldap.sasl import sasl, CB_USER, CB_AUTHNAME


class Credentials(sasl):
    """This class handles SASL BROWSER-ID authentication."""

    def __init__(self, assertion, audience):
        """Credentials constructor.

        Prepares assertion and audience to be used
        as the CB_USER and CB_AUTHNAME fields of a
        sasl interactive LDAP bind."""
        auth_dict = {CB_USER: assertion,
                     CB_AUTHNAME: audience}
        sasl.__init__(self, auth_dict, 'BROWSER-ID')
