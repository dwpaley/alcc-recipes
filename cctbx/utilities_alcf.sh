#!/bin/bash



export ROOT_PREFIX=$(readlink -f $(dirname ${BASH_SOURCE[0]}))
export CONDA_ENV_ROOT=${ROOT_PREFIX}/opt/mamba/envs

setup-env () {
    source $IDPROOT/bin/activate
}



mk-env () {
    setup-env

    #
    # Install mamba and create the psana_env environment, cloning the Aurora base environment
    #
    conda create -p ${CONDA_ENV_ROOT}/mybasenv --yes --clone $AURORA_BASE_ENV
    conda activate ${CONDA_ENV_ROOT}/mybasenv
    conda env list
    conda install mamba --yes -c conda-forge

    if [[ $2 == "perlmutter" ]]
    then
        mamba create -p ${CONDA_ENV_ROOT}/psana_env -f ${ROOT_PREFIX}/perlmutter_environment.yml --yes --clone ${CONDA_ENV_ROOT}/mybasenv
    else
        mamba create -p ${CONDA_ENV_ROOT}/psana_env -f ${ROOT_PREFIX}/psana_environment.yml --yes --clone ${CONDA_ENV_ROOT}/mybasenv
    fi
    mamba activate ${CONDA_ENV_ROOT}/psana_env

    #
    # switch MPI backends -- the psana package explicitly downloads openmpi
    # which is incompatible with some systems
    #
    conda remove --force mpi4py mpi openmpi mpich --yes || true
    if [[ $1 == "conda-mpich" ]]
    then
        mamba install mpich mpi4py mpich -c defaults --yes
    elif [[ $1 == "mpicc" ]]
    then
        MPICC="$(which mpicc)" pip install --no-binary mpi4py --no-cache-dir \
            mpi4py mpi4py
    elif [[ $1 == "cray-mpich" ]]
    then
        MPICC="cc -shared" pip install --no-binary mpi4py --no-cache-dir \
            mpi4py mpi4py
    elif [[ $1 == "cray-cuda-mpich" ]]
    then
        MPICC="$(which cc) -shared -lcuda -lcudart -lmpi -lgdrapi"\
            pip install --no-binary mpi4py --no-cache-dir mpi4py mpi4py
    elif [[ $1 == "cray-cuda-mpich-perlmutter" ]]
    then
        MPICC="$(which cc) -shared -target-accel=nvidia80 -lmpi -lgdrapi"\
            pip install --no-binary mpi4py --no-cache-dir mpi4py mpi4py
    elif [[ $1 == "cray-hip-mpich" ]]
    then
       MPICC="$(which cc) -shared -lmpi -I${ROCM_PATH}/include -L${ROCM_PATH}/lib -lamdhip64 -lhsa-runtime64"\
           pip install --no-binary mpi4py --no-cache-dir mpi4py mpi4py
    fi

    mamba deactivate
}



patch-env () {

    python \
        ${ROOT_PREFIX}/opt/util/patch-rpath.py \
        ${MAMBA_ROOT_PREFIX}/envs/psana_env/lib

}



patch-env-parallel () {

cat << EOF > $ROOT_PREFIX/opt/util/do_patch.sh
source $ROOT_PREFIX/utilities_alcf.sh
setup-env
micromamba activate patchelf_env
$ROOT_PREFIX/opt/util/patch_all_parallel.sh $MAMBA_ROOT_PREFIX/envs/psana_env/lib
EOF

    chmod +x $ROOT_PREFIX/opt/util/do_patch.sh

    echo "Please patch your .so files using Patchelf. Follow these steps:"
    echo "(1) $ salloc --nodes=1 --constraint=haswell --time=30 -A lcls -q interactive"
    echo "(2) $ $ROOT_PREFIX/opt/util/do_patch.sh"

}



env-activate () {
    setup-env
    micromamba activate psana_env
}



mk-cctbx () {
    env-activate

    pushd ${ROOT_PREFIX}

    if [[ $1 == "classic" ]]
    then
        python bootstrap.py --builder=dials \
                            --python=37 \
                            --use-conda ${CONDA_PREFIX} \
                            --nproc=${NPROC:-8} \
                            --config-flags="--enable_cxx11" \
                            --config-flags="--no_bin_python" \
                            --config-flags="--enable_openmp_if_possible=True" \
                            --config-flags="--use_environment_flags" \
                            ${@:2}
    elif [[ $1 == "no-boost" ]]
    then
        python bootstrap.py --builder=dials \
                            --python=37 \
                            --use-conda ${CONDA_PREFIX} \
                            --nproc=${NPROC:-8} \
                            --config-flags="--enable_cxx11" \
                            --config-flags="--no_bin_python" \
                            --config-flags="--enable_openmp_if_possible=True" \
                            --config-flags="--use_environment_flags" \
                            --no-boost-src \
                            ${@:2}
    elif [[ $1 == "cuda" ]]
    then
        python bootstrap.py --builder=dials \
                            --python=37 \
                            --use-conda ${CONDA_PREFIX} \
                            --nproc=${NPROC:-8} \
                            --config-flags="--enable_cxx11" \
                            --config-flags="--no_bin_python" \
                            --config-flags="--enable_openmp_if_possible=True" \
                            --config-flags="--enable_cuda" \
                            --config-flags="--use_environment_flags" \
                            ${@:2}
    elif [[ $1 == "kokkos" ]]
    then
        python bootstrap.py --builder=dials \
                            --python=37 \
                            --use-conda ${CONDA_PREFIX} \
                            --nproc=${NPROC:-8} \
                            --config-flags="--enable_cxx11" \
                            --config-flags="--no_bin_python" \
                            --config-flags="--enable_openmp_if_possible=True" \
                            --config-flags="--enable_kokkos" \
                            ${@:2}
    fi
    popd
}



patch-dispatcher () {
    activate

    pushd ${ROOT_PREFIX}/build
    ln -fs ${ROOT_PREFIX}/opt/site/dispatcher/dispatcher_include_$1.sh \
           dispatcher_include.sh
    popd

    libtbx.refresh
}



activate () {
    env-activate
    source ${ROOT_PREFIX}/build/setpaths.sh
}
