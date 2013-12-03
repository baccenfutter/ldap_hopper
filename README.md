===========
LDAP-Hopper
===========

LDAP-Hopper is a simplistic Python binding for accessing an LDAP Directory
Information Tree(DIT).::

    #!/usr/bin/env python
    from ldap_hopper import LdapNode

    # access the root-node
    LdapNode.SERVER = 'localhost'
    base_dn = 'dc=example,dc=org'
    bind_dn = 'cn=admin,dc=example,dc=org'
    bind_pw = 'secret'
    root = LdapNode(base_dn, bind_dn, bind_pw)

    # show attributes of root-node
    root.load_attrs()
    print root.attrs

    # get childs of root
    print root.get_childs()

    # get subtree of root
    print root.get_subs()

