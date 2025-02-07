#!/bin/bash


# this () { echo $(readlink -f $(dirname ${BASH_SOURCE[0]})); }
shopt -s expand_aliases
alias this="readlink -f \$(dirname \${BASH_SOURCE[0]})"


pushd $(this)
mkdir -p bin
# wget -qO- https://micromamba.snakepit.net/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
# wget -qO- https://github.com/mamba-org/micromamba-releases/releases/latest/download/micromamba-linunx-64 > bin/micromamba
wget -qO- https://github.com/mamba-org/micromamba-releases/releases/download/1.5.10-0/micromamba-linux-64 > bin/micromamba
chmod u+x bin/micromamba

popd
