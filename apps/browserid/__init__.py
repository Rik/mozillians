from ldap.sasl import sasl, CB_USER, CB_AUTHNAME


class credentials(sasl):
    """This class handles SASL BROWSER-ID authentication."""

    def __init__(self, assertion, audience):
        auth_dict = {CB_USER: assertion,
                     CB_AUTHNAME: audience}
        sasl.__init__(self, auth_dict, 'BROWSER-ID')
