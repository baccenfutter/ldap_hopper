"""An OOP approach to accessing and manipulating and LDAP directory-information-tree
"""

from dataclasses import dataclass

import enum
import ldap
from ldap.modlist import addModlist


class Scope(enum.Enum):
    base = ldap.SCOPE_BASE
    onelevel = ldap.SCOPE_ONELEVEL
    subtree = ldap.SCOPE_SUBTREE


@dataclass
class Config:
    server: str = 'localhost'
    dn: str = 'dc=example,dc=com'
    bind_dn: str = ''
    bind_pw: str = ''
    use_tls: bool = False

    def __repr__(self):
        return f"<Config(dn='{self.dn}', bind_dn='{self.bind_dn}')>"

    def dict(self):
        return {
            'server': self.server,
            'dn': self.dn,
            'bind_dn': self.bind_dn,
            'bind_pw': self.bind_pw,
        }


class Cursor(object):
    def __init__(self, config: Config = None, conn: ldap.ldapobject.SimpleLDAPObject = None):
        if config is None:
            config = Config()
        self.config = config
        self.conn = conn
        if self.conn is None:
            self.conn = ldap.initialize(self.config.server)
            if self.config.use_tls:
                self.conn.start_tls_s()
            if self.config.bind_dn:
                self.conn.bind_s(self.config.bind_dn, self.config.bind_pw)

    def __repr__(self):
        return self.config.dn

    def __get_item__(self, item):
        return self.attrs[item]
    
    def __set_item__(self, item, value):
        self.attrs = {item: value}

    def __del_item__(self, item):
        self.conn.modify_s(self.config.dn, [(ldap.MOD_DELETE, item)])

    def __iter__(self):
        for k in self.attrs:
            return k

    def __len__(self):
        return len(self.attrs)

    def keys(self):
        return self.attrs.keys()

    def values(self):
        return self.attrs.values()

    def has_key(self, key):
        return self.attrs.has_key(key)

    @property
    def attrs(self):
        scope = ldap.SCOPE_BASE
        filter = "objectClass=*"
        result = dict(self.conn.search_s(self.config.dn, scope, filter, None)[0][1])
        return result

    @attrs.setter
    def attrs(self, new_attrs: dict):
        old_attrs = self.attrs
        change_list = []
        for set_k, set_v in new_attrs.iteritems():
            if not isinstance(set_v, list):
                set_v = [set_v]

            action = None
            if set_k not in old_attrs:
                action = ldap.MOD_ADD
            elif old_attrs[set_k] != set_v:
                action = ldap.MOD_REPLACE
            else:
                raise NotImplementedError("BUG! BUG! BUG!")

            change_list.append((action, str(set_k), set_v))

        if change_list:
            self.conn.modify_s(self.config.dn, change_list)

    @property
    def children(self):
        filter = "objectClass=*"
        result_id = self.conn.search(self.config.dn, ldap.SCOPE_ONELEVEL, filter)
        while 1:
            r_type, r_data = self.conn.result(result_id, 0)
            if not r_data:
                break
            else:
                if r_type == ldap.RES_SEARCH_ENTRY:
                    if isinstance(r_data, list):
                        for r in r_data:
                            dn = r[0]
                            config = Config(**self.config.dict())
                            config.dn = dn
                            yield Cursor(config=config, conn=self.conn)
                    else:
                        print(r_data)
                        dn = r_data[0]
                        config = Config(**self.config.dict())
                        config.dn = dn
                        yield Cursor(config=config, conn=self.conn)
                        # output.append(Cursor(self.server, dn, self.__bind_dn, self.__bind_pw))

    @property
    def subtree(self):
        ldap_filter = "objectClass=*"
        result_id = self.conn.search(self.config.dn, ldap.SCOPE_SUBTREE, ldap_filter)
        while 1:
            r_type, r_data = self.conn.result(result_id, 0)
            if not r_data:
                break
            else:
                if r_type == ldap.RES_SEARCH_ENTRY:
                    if isinstance(r_data, list):
                        for r in r_data:
                            dn = r[0]
                            config = Config(**self.config.dict())
                            config.dn = dn
                            yield Cursor(config=config, conn=self.conn)
                    else:
                        print(r_data)
                        dn = r_data[0]
                        config = Config(**self.config.dict())
                        config.dn = dn
                        yield Cursor(config=config, conn=self.conn)

    def add(self, dn: str, attrs: dict):
        ldif = addModlist(attrs)

        config = self.config.dict()
        config.dn = dn
        self.conn.add_s(dn, ldif)
        return Cursor(config=config, conn=self.conn)

    def modify(self, attrs: dict):
        ldif = addModlist(attrs)
        change = ldap.modlist.modifyModlist(self.attrs, attrs)
        self.conn.modify_s(self.config.dn, change)
        return self

    def delete(self):
        return self.conn.delete_s(self.config.dn)

    def search(self, search_filter: str, scope: Scope = None):
        if scope is None:
            scope = ldap.SCOPE_SUBTREE
        
        result_id = self.conn.search(self.config.dn, scope, search_filter)
        while 1:
            r_type, r_data = self.conn.result(result_id, 0)
            if (r_data == []):
                break
            else:
                if r_type == ldap.RES_SEARCH_ENTRY:
                    if isinstance(r_data, list):
                        for r in r_data:
                            config = Config(**self.config.dict())
                            config.dn = r[0]
                            yield Cursor(config=config, conn=self.conn)
                    else:
                        config = Config(**self.config.dict())
                        config.dn = r[0]
                        yield Cursor(config=config, conn=self.conn)
