# Source ROOT setup
source /your/root/dir/bin/thisroot.sh
source /your/directory/too/neut/build/Linux/setup.sh
export ROOTSYS=/your/root/dir/ROOT/v6_30_02_cxx17
#export ROOT_INCLUDE_PATH="$ROOT_INCLUDE_PATH:/your/path/ROOT/v6_30_02_cxx17/include"
### GENIE
export GENIE=/your/directory/too/genie
export GENIE_INSTALL_DIR=$GENIE/install
#export GENIE_VERSION=v3_06_00
export PATH=$GENIE_INSTALL_DIR/bin:$PATH
export LD_LIBRARY_PATH=$GENIE_INSTALL_DIR/lib:$LD_LIBRARY_PATH

export GENIEXSECPATH=/your/genie/xsec/path/including/tune/data
export GENIE_XSEC_FILE=$GENIEXSECPATH/gxspl-NUsmall.xml
export GXMLPATH=/your/generator/xml/path/N24_20i/N24_20i_02_11b        
export GENIE_XSEC_TUNE=N24_20i_02_11b
export GENIE_XSEC_GENLIST=Default
export GENIE_XSEC_KNOTS=250
export GENIE_XSEC_EMAX=1000.0
export GMSGLPATH=$GENIE/config
export TUNEDIR="$GENIE/config/N24_20i"
export GENIE_VERSION=x-xx-xx

### Neut
export NEUT=/your/path/too/neut/build/Linux
export PATH=$PATH:$NEUT/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$NEUT/lib
export NEUT_VERSION=x.x.x  
### Nuisance
export NUISANCE=/your/path/too/nuisance/build/Linux
export PATH=$NUISANCE/bin:$PATH
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$NUISANCE/lib
export PKG_CONFIG_PATH=/your/path/too/neut/build/Linux:$PKG_CONFIG_PATH
source /path/too/nuisance/install/setup.sh
### nusystematics
export NUSYSTEMATICS=/your/path/too/nusystematics/install
export PATH=$NUSYSTEMATICS/bin:$PATH
export LD_LIBRARY_PATH=$NUSYSTEMATICS/lib:$LD_LIBRARY_PATH
### TBB (if needed explicitly by downstream builds)
export TBB_DIR=/path/too/nusystematics/tbb/tbb-install/lib64/cmake/TBB
### NIWGReWeight
source /your/path/too/NIWGReWeight/build/Linux/bin/setup.NIWG.sh
## T2KReWeight
source /your/path/too/T2KReWeight24.12/build/Linux/bin/setup.T2K.sh
## LHAPDF
export LHAPDF_LIB_DIR=/path/too/lib64
export LHAPDF_INC_DIR=/path/too/include/LHAPDF


# Set PUfIN OUT location
export PUFIN_OUT=/put/your/own/path/here/for/generator/outputs
# Check for Generator Variables

# Setup Python Alisis For Commands
alias Gen-Main="python $(realpath ./GenMain.py)"
alias Gen-Submit="python $(realpath ./GenSubmit.py)"
alias Plot-Main="python $(realpath ./PlotMain.py)"
alias Weight-Main="python $(realpath ./WeightMain.py)"