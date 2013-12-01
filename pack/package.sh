#!/bin/bash

author="Brian Wiborg"
mail="baccenfutter@c-base.org"
pn="LDAP-Hopper"
description="Simple access to LDAP Directory Information Tree."

p="$(echo ${pn} | tr '[:upper:]' '[:lower:]' | tr '-' '_')"
v="$1"
pv="${p}-${v}"
workdir=$(mktemp -d --tmpdir=/tmp ${p}-build.XXXXXX)
projectdir="$workdir/${p}"
sourcedir="$projectdir/${p}"

if grep / <(echo $0) &>/dev/null; then
echo 'Please run this script from its directory.'
fi

if [[ -z $v ]]; then
    echo "Please provide version tag, e.g. '$0 0.1.0'"
    exit 1
fi

read -n 1 -p "Can haz package: ${pv} [y|N]: " answer
echo
if [[ ! "$answer" == y ]]; then
echo "Bailing out by user request."
    exit 0
fi

cleanup() {
    rm -rf "$workdir"
}

# bootstrap working directory
#trap cleanup INT TERM QUIT
echo $workdir

mkdir -p "$sourcedir"

# copy source to working directory
cp ../*.py "$sourcedir"

# copy meta-files to working directory
cp *.txt "$projectdir"
cp *.in "$projectdir"

# create setup.py
setup_stanza="from distutils.core import setup

setup(
name='${pn}',
version='${v}',
author='${author}',
author_email='${mail}',
packages=['${p}'],
scripts=[],
url='http://pypi.python.org/pypi/${pn}/',
license='LICENSE.txt',
description='${description}',
long_description=open('README.txt').read(),
install_requires=[],
)
"

echo "$setup_stanza" > "$projectdir/setup.py"

# run setup.py
cd "$projectdir"
python setup.py sdist

# register and upload
read -n 1 -p "Can haz upload: ${pv} [y|N]: " answer
echo
if [[ ! "$answer" == y ]]; then
echo "Bailing out by user request."
    exit 0
fi

python setup.py register
python setup.py sdist upload
