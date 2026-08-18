# ----------------Genie Paths------------------------
export GENIE_FQ_DIR=/your/path/too/GENIE_vx_xx_xx/Generator
export GENIE_VERSION=vx_xx_xx
export GENIE=${GENIE_FQ_DIR}
export GENIE_LIB=${GENIE_FQ_DIR}/lib
export GENIE_INC=${GENIE_FQ_DIR}/install/include/GENIE/
export GENIE_REWEIGHT=/your/path/too/GENIEReWeight_v1_04_00/Reweight
export LD_LIBRARY_PATH=${GENIE_FQ_DIR}/lib/:${LD_LIBRARY_PATH}
export LD_LIBRARY_PATH=${GENIE_REWEIGHT}/lib/:${LD_LIBRARY_PATH}
export PATH=${GENIE_FQ_DIR}/bin/:${PATH}
export PATH=${GENIE_REWEIGHT}/bin/:${PATH}
export ROOT_INCLUDE_PATH=${GENIE_FQ_DIR}/include/GENIE/:${ROOT_INCLUDE_PATH}
export CMAKE_PREFIX_PATH=${GENIE_FQ_DIR}:${CMAKE_PREFIX_PATH}
export PKG_CONFIG_PATH=${GENIE_FQ_DIR}:${PKG_CONFIG_PATH}
export GENIE_XSEC_DIR=$GENIE_FQ_DIR/xsec/G1810a0211a-k250-e1000/
export GENIE_XSEC_FILE=$GENIE_XSEC_DIR/gxspl-NUbig.xml
export GENIE_XSEC_TUNE=N24_20i_02_11b
export PYTHIA6_LIB_DIR=/usr/lib/

# ----------------ROOT Paths------------------------
export ROOT_INCLUDE_PATH=/your/path/too/nusystematics/install/include:$ROOT_INCLUDE_PATH
export ROOT_INCLUDE_PATH=${GENIE_INC}:$ROOT_INCLUDE_PATH
export ROOT_INCLUDE_PATH=${fhiclcpp_ROOT}/include/:$ROOT_INCLUDE_PATH
export ROOT_INCLUDE_PATH=${cetlib_ROOT}/include/:$ROOT_INCLUDE_PATH
export ROOT_INCLUDE_PATH=${cetlib_except_ROOT}/include:$ROOT_INCLUDE_PATH
export ROOT_INCLUDE_PATH=${hep_concurrency_ROOT}/include:$ROOT_INCLUDE_PATH
export ROOT_INCLUDE_PATH=${Boost_INCLUDE_DIR}:$ROOT_INCLUDE_PATH
export ROOT_INCLUDE_PATH=${SQLite3_INLUDE_DIR}:$ROOT_INCLUDE_PATH
export ROOT_INCLUDE_PATH=${TBB_INCLUDE_DIR}:$ROOT_INCLUDE_PATH
export ROOT_INCLUDE_PATH=${NUISANCE_INCLUDE_DIR}:$ROOT_INCLUDE_PATH

# ----------------Boost Paths------------------------
export Boost_INCLUDE_DIR=/path/too/include/boost1.78/
export Boost_LIBRARY=/path/too/lib64/
export SQLite3_INCLUDE_DIR=/path/too/include
export SQLite3_LIBRARY=/path/too/lib64/

# ----------------Nuisance and other Paths------------------------
export fhiclcpp_ROOT=/path/too/nuisance/nusyst_dev/fhicl-cpp-standalone/build-mazen/fhicl-cpp-install/
export PATH=${fhiclcpp_ROOT}/bin/:${PATH}
export LD_LIBRARY_PATH=${fhiclcpp_ROOT}/lib/:${LD_LIBRARY_PATH}
export cetlib_ROOT=/path/too/nuisance/nusyst_dev/fhicl-cpp-standalone/build-mazen/cetlib-install/
export PATH=${cetlib_ROOT}/bin/:${PATH}
export LD_LIBRARY_PATH=${cetlib_ROOT}/lib/:${LD_LIBRARY_PATH}
export cetlib_except_ROOT=/path/too/nuisance/nusyst_dev/fhicl-cpp-standalone/build-mazen/cetlib-except-install/
export PATH=${cetlib_except_ROOT}/bin/:${PATH}
export LD_LIBRARY_PATH=${cetlib_except_ROOT}/lib/:${LD_LIBRARY_PATH}
export hep_concurrency_ROOT=/path/too/nuisance/nusyst_dev/fhicl-cpp-standalone/build-mazen/hep-concurrency-install
export PATH=${hep_concurrency_ROOT}/bin/:${PATH}
export LD_LIBRARY_PATH=${hep_concurrency_ROOT}/lib/:${LD_LIBRARY_PATH}

# ----------------C++ Paths------------------------
export CPLUS_INCLUDE_PATH=/path/too/nuisance/nusyst_dev/nusystematics/build/Linux/include/:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=${GENIE_INC}:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=${fhiclcpp_ROOT}/include/:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=${cetlib_ROOT}/include/:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=${cetlib_except_ROOT}/include:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=${hep_concurrency_ROOT}/include:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=${Boost_INCLUDE_DIR}:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=${SQLite3_INLUDE_DIR}:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=${TBB_INCLUDE_DIR}:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=/path/too/ROOT/v6_26_06_pythia6/include:$CPLUS_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=${NUISANCE_INCLUDE_DIR}:$CPLUS_INCLUDE_PATH



# ### Nuisance Code breaks if I don't include this??
export NUISANCE=/your/path/too/nuisance/build/Linux
export PATH=$NUISANCE/bin:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$NUISANCE/lib
export PKG_CONFIG_PATH=/your/path/too/neut/build/Linux:$PKG_CONFIG_PATH
source /your/path/too/nuisance/install/setup.sh
### nusystematics
export NUSYSTEMATICS=/your/path/too/nusystematics/install
export PATH=$NUSYSTEMATICS/bin:$PATH
export LD_LIBRARY_PATH=$NUSYSTEMATICS/lib:$LD_LIBRARY_PATH
# Source ROOT setup
source /project/ROOT/v6_30_02_cxx17/bin/thisroot.sh
source /your/path/too/neut/build/Linux/setup.sh
export ROOTSYS=/project/ROOT/v6_30_02_cxx17