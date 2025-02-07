#!/bin/bash


# this () { echo $(readlink -f $(dirname ${BASH_SOURCE[0]})); }
shopt -s expand_aliases
alias this="readlink -f \$(dirname \${BASH_SOURCE[0]})"


pushd $(this)
mkdir -p bin
wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-ppc64le/latest | tar -xvj bin/micromamba
chmod u+x bin/micromamba

popd
