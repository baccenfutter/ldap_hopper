"""LDAP-Hopper

Simple Python binding for easily accessing an LDAP Directory Information Tree.
"""
__author__ = "bacce <baccenfutter@c-base.org>"
__date__ = "2013-12-01"
__license__ = 'public domain'

import ldap


class LdapNode(object):
    SERVER = "localhost"

    def __new__(cls, *args, **kwargs):
        if not cls.SERVER:
            raise ValueError('Please define SERVER, first!')
        if not cls.SERVER.startswith('ldap://'):
            cls.SERVER = 'ldap://%s' % cls.SERVER
        if not ':' in cls.SERVER.split('://')[1]:
            cls.SERVER = '%s:389' % cls.SERVER
        if not cls.SERVER.endswith('/'):
            cls.SERVER = '%s/' % cls.SERVER
        return object.__new__(cls, *args, **kwargs)

    def __init__(self, dn, bind_dn, bind_pw, attrs={}):
        """
        :param dn:      distinguishable name
        :param bind_dn: bindDN
        :param bind_pw: password for bindDN
        :param attrs:   (optional) attributes
        """
        self.dn = dn
        self.bind_dn = bind_dn
        self.bind_pw = bind_pw
        self.attrs = dict(attrs)

        if not self.attrs:
            self.load_attrs()

    def initialize(self):
        self.session = ldap.initialize(self.SERVER)
        self.session.simple_bind_s(self.bind_dn, self.bind_pw)

    def __repr__(self):
        return '<LdapNode(%s)>' % self.dn

    def load_attrs(self):
        """Load all attributes into local cache"""
        self.initialize()
        scope = ldap.SCOPE_BASE
        filter = "objectClass=*"
        self.attrs = self.session.search_s(self.dn, scope, filter, None)[0][1]

    def get_attr(self, attr):
        """Obtain a specific attribute

        :returns None:  if attr wasn't found
        :returns dict:  {attr_name: attr_value}
        """
        self.load_attrs()
        for k, v in self.attrs.iteritems():
            if str(k).lower() == str(attr).lower():
                return {k: v}

    def set_attr(self, attrs):
        change_list = []
        for set_k, set_v in attrs.iteritems():
            if set_k not in self.attrs:
                action = ldap.MOD_ADD
                change_list.append((action, str(set_k), set_v))
            elif self.attrs[set_k] != set_v:
                action = ldap.MOD_REPLACE
                change_list.append((action, str(set_k), set_v))

        self.initialize()
        result = self.session.modify_s(self.dn, change_list)
        self.load_attrs()
        return result

    def get_parent(self):
        """Obtain parent object

        :returns obj:   instance of ldap_hopper.LdapNode
        """
        self.initialize()
        dn = ','.join(self.dn.split(',')[1:])
        parent = self.session.search_s(dn, ldap.SCOPE_BASE, "objectClass=*")
        dn = parent[0][0]
        attrs = parent[0][1]
        return LdapNode(dn, self.bind_dn, self.bind_pw, attrs)

    def get_childs(self, by_attr=None):
        """Obtain all childs (onelevel)

        :param by_attr:     (optional) filter by attribute
        :returns list:      instances of ldap_hopper.LdapNode
        """
        self.initialize()
        if by_attr:
            filter = '%s=*' % by_attr
        else:
            filter = "objectClass=*"

        result_id = self.session.search(self.dn, ldap.SCOPE_ONELEVEL, filter)
        output = []
        while 1:
            r_type, r_data = self.session.result(result_id, 0)
            if (r_data == []):
                break
            else:
                if r_type == ldap.RES_SEARCH_ENTRY:
                    if isinstance(r_data, list):
                        for r in r_data:
                            dn = r[0]
                            attrs = r[1]
                            output.append(LdapNode(dn, self.bind_dn, self.bind_pw, attrs))
                    else:
                        dn = r_data[0]
                        attrs = r_data[1]
                        output.append(LdapNode(dn, self.bind_dn, self.bind_pw, attrs))
        return output

    def get_subs(self, by_attr=None):
        """Obtain childs (subtree)

        :param by_attr: (optional) filter by attribute
        :returns list:  instances of ldap_hopper.LdapNode
        """
        self.initialize()
        if by_attr:
            filter = '%s=*' % by_attr
        else:
            filter = 'objectClass=*'

        result_id = self.session.search(self.dn, ldap.SCOPE_SUBTREE, filter)
        output = []
        while 1:
            r_type, r_data = self.session.result(result_id, 0)
            if (r_data == []):
                break
            else:
                if r_type == ldap.RES_SEARCH_ENTRY:
                    if isinstance(r_data, list):
                        for r in r_data:
                            dn = r[0]
                            attrs = r[1]
                            output.append(LdapNode(dn, self.bind_dn, self.bind_pw, attrs))
                    else:
                        dn = r_data[0]
                        attrs = r_data[1]
                        output.append(LdapNode(dn, self.bind_dn, self.bind_pw, attrs))
        return output
