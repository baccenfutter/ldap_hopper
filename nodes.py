"""ldap_hopper.nodes"""
__author__ = "Brian Wiborg <baccenfutter@c-base.org>"
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

    def __unbind(self):
        self.__session.unbind_s()

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
        result = dict(self.__session.search_s(self.dn, scope, filter, None)[0][1])
        self.__unbind()
        return result

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
            self.__initialize()
            self.__session.modify_s(self.dn, change_list)
            self.__unbind()

    def set_password(self, old_pw, new_pw):
        self.__initialize()
        self.__session.passwd_s(self.dn, old_pw, new_pw)
        self.__unbind()

    def get_parent(self):
        """Obtain parent object

        :returns obj:   instance of ldap_hopper.ObjectNode
        """
        self.__initialize()
        dn = ','.join(self.dn.split(',')[1:])
        parent = self.__session.search_s(dn, ldap.SCOPE_BASE, "objectClass=*")
        self.__unbind()
        dn = parent[0][0]
        attrs = parent[0][1]
        return ObjectNode(self.server, dn, self.__bind_dn, self.__bind_pw)

    def get_childs(self, by_attr=None):
        """Obtain all childs (onelevel)

        :param by_attr:     (optional) filter by attribute
        :returns list:      instances of ldap_hopper.ObjectNode
        """
        self.__initialize()
        if by_attr:
            filter = by_attr
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
        self.__unbind()
        return output

    def get_subs(self, by_attr=None):
        """Obtain childs (subtree)

        :param by_attr: (optional) filter by attribute
        :returns list:  instances of ldap_hopper.ObjectNode
        """
        self.__initialize()
        if by_attr:
            filter = by_attr
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
        self.__unbind()
        return output

    def add_child(self, dn, attrs):
        """Add a child-node to this object-node

        :param dn:      either dn or rdn relative to self.dn
        :param attrs:   attributes dictionary
        :returns obj:   instance of ObjectNode
        """
        if not self.dn in dn:
            dn = '%s,%s' % (dn, self.dn)
        ldif = addModlist(attrs)

        self.__initialize()
        self.__session.add_s(dn, ldif)
        self.__unbind()
        return ObjectNode(self.server, dn, self.__bind_dn, self.__bind_pw)

    def del_child(self, dn):
        """Delete a child-node of this object-node

        :param dn:      either dn or rdn relative to self.dn
        :returns None:  or passes python-ldap exception
        """
        if not self.dn in dn:
            dn = '%s,%s' % (dn, self.dn)

        self.__initialize()
        self.__session.delete_s(dn)
        self.__unbind()

    def search(self, attribute, value, scope=None):
        """Search from this node as search-base

        :param attribute:   name of the attribute to look-up
        :param value:       value of the attribute to look-up
        :param scope:       search_scope, e.g. ldap.SCOPE_SUBTREE
                            (defaults to ldap.SCOPE_ONELEVEL)
        """
        if scope is None:
            scope = ldap.SCOPE_ONELEVEL
        search_filter = '%s=%s' % (attribute, value)

        self.__initialize()
        result_id = self.__session.search(self.dn, scope, search_filter)
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
                        dn = r[0]
                        output.append(ObjectNode(self.server, dn, self.__bind_dn, self.__bind_pw))
        return output

    def as_tuple(self):
        """Convenience method for obtaining a ldap result-like tuple

        :returns tuple:     ( str(dn), dict(attrs) )
        """
        return (self.dn, self.get_attrs())
