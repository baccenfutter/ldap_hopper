"""LDAP-Hopper

Simple Python binding for easily accessing an LDAP Directory Information Tree.
"""
__author__ = "bacce <baccenfutter@c-base.org>"
__date__ = "2013-12-01"
__license__ = 'public domain'

import ldap
from ldap.modlist import addModlist


class ObjectNode(object):
    def __init__(self, server, dn, bind_dn, bind_pw):
        """
        :param server:  LDAP server url
        :param dn:      distinguishable name
        :param bind_dn: bindDN
        :param bind_pw: password for bindDN
        :param attrs:   (optional) attributes
        """
        self.server = self.__qualify_server(server)
        self.dn = dn
        self.__bind_dn = bind_dn
        self.__bind_pw = bind_pw

    def __repr__(self):
        return '<ObjectNode(%s)>' % self.dn

    def __getitem__(self, item):
        attrs = self.get_attrs()
        if item in attrs:
            return attrs[item]

    def __setitem__(self, key, value):
        self.set_attrs({key: value})

    def __initialize(self):
        """Convenience wrapper for initializing the LDAP connection"""
        self.__session = ldap.initialize(self.server)
        self.__session.simple_bind_s(self.__bind_dn, self.__bind_pw)

    def __qualify_server(self, server):
        """Convenience helper for qualifying hostname of server"""
        try:
            if not server.startswith('ldap://'):
                server = 'ldap://%s' % server
            if not ':' in server[7:]:
                server = server + ':389'
            if not server.endswith('/'):
                server = server + '/'
            return server
        except:
            raise ValueError('Malformed hostname: %s' % server)

    def get_attrs(self):
        """Load all attributes into local cache"""
        self.__initialize()
        scope = ldap.SCOPE_BASE
        filter = "objectClass=*"
        return dict(self.__session.search_s(self.dn, scope, filter, None)[0][1])

    def set_attrs(self, new_attrs):
        old_attrs = self.get_attrs()
        change_list = []
        for set_k, set_v in new_attrs.iteritems():
            # make sure the value is a list
            if not isinstance(set_v, list):
                set_v = [set_v]
            if set_k not in old_attrs:
                action = ldap.MOD_ADD
                change_list.append((action, str(set_k), set_v))
            elif old_attrs[set_k] != set_v:
                action = ldap.MOD_REPLACE
                change_list.append((action, str(set_k), set_v))

        if change_list:
            self.__session.modify_s(self.dn, change_list)

    def get_parent(self):
        """Obtain parent object

        :returns obj:   instance of ldap_hopper.ObjectNode
        """
        self.__initialize()
        dn = ','.join(self.dn.split(',')[1:])
        parent = self.__session.search_s(dn, ldap.SCOPE_BASE, "objectClass=*")
        dn = parent[0][0]
        attrs = parent[0][1]
        return ObjectNode(dn, self.__bind_dn, self.__bind_pw, attrs)

    def get_childs(self, by_attr=None):
        """Obtain all childs (onelevel)

        :param by_attr:     (optional) filter by attribute
        :returns list:      instances of ldap_hopper.ObjectNode
        """
        self.__initialize()
        if by_attr:
            filter = '%s=*' % by_attr
        else:
            filter = "objectClass=*"

        result_id = self.__session.search(self.dn, ldap.SCOPE_ONELEVEL, filter)
        output = []
        while 1:
            r_type, r_data = self.__session.result(result_id, 0)
            if (r_data == []):
                break
            else:
                if r_type == ldap.RES_SEARCH_ENTRY:
                    if isinstance(r_data, list):
                        for r in r_data:
                            dn = r[0]
                            output.append(ObjectNode(self.server, dn, self.__bind_dn, self.__bind_pw))
                    else:
                        dn = r_data[0]
                        output.append(ObjectNode(self.server, dn, self.__bind_dn, self.__bind_pw))
        return output

    def get_subs(self, by_attr=None):
        """Obtain childs (subtree)

        :param by_attr: (optional) filter by attribute
        :returns list:  instances of ldap_hopper.ObjectNode
        """
        self.__initialize()
        if by_attr:
            filter = '%s=*' % by_attr
        else:
            filter = 'objectClass=*'

        result_id = self.__session.search(self.dn, ldap.SCOPE_SUBTREE, filter)
        output = []
        while 1:
            r_type, r_data = self.__session.result(result_id, 0)
            if (r_data == []):
                break
            else:
                if r_type == ldap.RES_SEARCH_ENTRY:
                    if isinstance(r_data, list):
                        for r in r_data:
                            dn = r[0]
                            output.append(ObjectNode(self.server, dn, self.__bind_dn, self.__bind_pw))
                    else:
                        dn = r_data[0]
                        output.append(ObjectNode(self.server, dn, self.__bind_dn, self.__bind_pw))
        return output

    def add_child(self, dn, attrs):
        if not self.dn in dn:
            dn = '%s,%s' % (dn, self.dn)
        ldif = addModlist(attrs)

        self.__initialize()
        self.__session.add_s(dn, ldif)
        return ObjectNode(self.server, dn, self.__bind_dn, self.__bind_pw)

    def del_child(self, dn):
        if not self.dn in dn:
            dn = '%s,%s' % (dn, self.dn)

        self.__initialize()
        self.__session.delete_s(dn)
