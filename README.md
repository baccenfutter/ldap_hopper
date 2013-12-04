===========
LDAP-Hopper
===========

LDAP-Hopper is a simplistic Python binding for accessing an LDAP Directory
Information Tree(DIT).::

    #!/usr/bin/env python
    from ldap_hopper import ObjectNode

    # access the root-node
    ObjectNode.SERVER = 'localhost'
    base_dn = 'dc=example,dc=org'
    bind_dn = 'cn=admin,dc=example,dc=org'
    bind_pw = 'secret'
    root = ObjectNode(base_dn, bind_dn, bind_pw)

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

    # delete child node
    root.del_child('ou=node_1,dc=example,dc=org')
    root.del_child('ou=node_2')                     # shortcut also allowed
