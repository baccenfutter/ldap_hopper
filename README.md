# LDAP-Hopper

`ldap_hopper` is a small `Python3` package that allows you to easily navigate and manipulate an LDAP directory-information-tree(DIT).
It neatly wraps around the standard `ldap` package and takes away all the nasty bits and pieces of boiler-plating, while making your code more readable.

## Installation

```
pip install ldap_hopper
```

## Usage
```python
#!/usr/bin/env python3
from ldap_hopper import Config, Cursor

# define an access configuration
config = Config(
    server='ldap://localhost',
    dn='dc=example.dc=com',
#    bind_dn='',
#    bind_pw='',
#    use_tls=True,
)

# creating a cursor
root = Cursor(config)
print(root.attrs)

# traversal via standard generators
[child for child in root.children]
[sub for sub in root.subtree]

# adding a child node
dn = 'ou=crew,dc=example,dc=com'
attrs = {
    'objectClass': ['organizationalUnit'],
    'ou': ['crew'],
}
cursor = root.add(dn, attrs)

# searching defaults to ldap.SCOPE_SUBTREE
[result for result in root.search('ou=crew')]

from ldap_hopper import Scope
[r for r in root.search('objectClass=*', Scope.onelevel)]

# manipulating attributes
cursor.attrs['description'] = 'Lorem ipsum...'
del cursor.attrs['desciption']

# deleting an entire object
cursor.delete()
```

## Development

```
git clone github.com:baccenfutter/ldap_hopper.git
cd ldap_hopper
pipenv install --dev
```

## Resources

Source: https://github.com/baccenfutter/ldap_hopper  
PyPi  : https://pypi.python.org/pypi/ldap_hopper/
