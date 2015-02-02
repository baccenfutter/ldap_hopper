===========
LDAP-Hopper
===========

LDAP-Hopper is a simplistic Python binding for accessing an LDAP Directory
Information Tree(DIT).

    #!/usr/bin/env python
    from ldap_hopper import Cursor

    # access the root-node
    server = 'localhost'
    base_dn = 'dc=example,dc=org'
    bind_dn = 'cn=admin,dc=example,dc=org'
    bind_pw = 'secret'
    root = Cursor(server, base_dn, bind_dn, bind_pw)

    # show attributes of root-node
    print root.attrs

    # get childs of root
    print root.childs

    # get subtree of root
    print root.subs
    
    # Filter uid objects from all subs
    print filter(lambda x: x['uid'], root.subs)

    # add child node
    new_child = {
        'objectClass': ['organizationalUnit'],
        'ou': ['padawans'],
    }
    new_node = root.add_child('ou=node_1,dc=example,dc=org', new_child)
    new_node = root.add_child('ou=node_2', new_child)     # will auto-expand self.dn
    print new_node

    # search for an object
    root.search('ou', new_node['ou'])    # no scope defaults to onelevel
    root.search('ou', new_node['ou'], ldap.SCOPE_SUBTREE)    # default can be overwritten

    # delete child node
    node_1.delete()


=========
Resources
=========

Source: https://github.com/baccenfutter/ldap_hopper
PyPi  : https://pypi.python.org/pypi/LDAP-Hopper/
