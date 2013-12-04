===========
LDAP-Hopper
===========

LDAP-Hopper is a simplistic Python binding for accessing an LDAP Directory
Information Tree(DIT).::

    #!/usr/bin/env python
    from ldap_hopper import ObjectNode

    # access the root-node
    server = 'localhost'
    base_dn = 'dc=example,dc=org'
    bind_dn = 'cn=admin,dc=example,dc=org'
    bind_pw = 'secret'
    root = ObjectNode(server, base_dn, bind_dn, bind_pw)

    # show attributes of root-node
    print root.attrs

    # get childs of root
    print root.get_childs()

    # get subtree of root
    print root.get_subs()

    # add child node
    attrs_1 = {
        'objectClass': ['organizationalUnit'],
        'ou': ['node_1'],
    }
    attrs_2 = {
        'objectClass': ['organizationalUnit'],
        'ou': ['node_2'],
    }
    node_1 = root.add_child('ou=node_1,dc=example,dc=org', attrs)
    node_2 = root.add_child('ou=node_2', attrs)     # will auto-expand self.dn
    print node_1, node_2

    # search for an object
    node_1 = root.search('ou', 'node_1')    # no scope defaults to onelevel
    node_2 = root.search('ou', 'node_2', ldap.SCOPE_SUBTREE)    # default can be overwritten
    print node_1, node_2

    # delete child node
    root.del_child('ou=node_1,dc=example,dc=org')
    root.del_child('ou=node_2')                     # shortcut also allowed


=========
Resources
=========

Source: https://github.com/baccenfutter/ldap_hopper

PyPi  : https://pypi.python.org/pypi/LDAP-Hopper/
