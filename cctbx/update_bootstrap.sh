#!/usr/bin/env bash

# this () { echo $(readlink -f $(dirname ${BASH_SOURCE[0]})); }
shopt -s expand_aliases
alias this="readlink -f \$(dirname \${BASH_SOURCE[0]})"
# export BOOTSTRAP_SOURCE="https://raw.githubusercontent.com/cctbx/cctbx_project/master/libtbx/auto_build/bootstrap.py"
export BOOTSTRAP_SOURCE="https://raw.githubusercontent.com/cctbx/cctbx_project/refs/heads/jpb/update_boostrap/libtbx/auto_build/bootstrap.py"

pushd $(this)
if [[ -f bootstrap.py ]]
then
    if [[ -z ${LEAVE_BOOTSTRAP+x} ]]
    then
        rm bootstrap.py
    fi
fi
if [[ ! -e bootstrap.py ]]
then
    wget $BOOTSTRAP_SOURCE --no-check-certificate
fi
popd
