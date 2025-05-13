#!/bin/bash

#TODO: update the set flags appropriately
set -ex

TOOL_NAME=bcrmatch
# pull the tool version from the environment, otherwise set it to 'local'
TOOL_VERSION="${TOOL_VERSION:-local}"
# TOOL_DIR=$TOOL_NAME-$TOOL_VERSION
SRC_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
BUILD_DIR=$SRC_DIR/build/$TOOL_NAME

mkdir -p $BUILD_DIR

#TODO: add more exclusions here
rsync --cvs-exclude --exclude build --exclude-from='do-not-distribute.txt' -a --delete $SRC_DIR/ $BUILD_DIR/

# Use sed to replace the string with the environment variable
# if [[ "$(uname)" == "Darwin" ]]; then
#     # For MacOS
#     sed -i "" "s/TOOL_VERSION/${TOOL_VERSION}/g" "$BUILD_DIR/README"
# else
#     # For Linux
#     sed -i "s/TOOL_VERSION/${TOOL_VERSION}/g" "$BUILD_DIR/README"
# fi

# cd $BUILD_DIR/method

# git clone -b 'v0.1' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/tools-redesign/global-dependencies/allele-validator.git
# rm -rf allele-validator/.git

# # This package provides sequence input validation & conversion.
# git clone -b 'v1.0.1' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/iedbtools-utilities.git
# rm -rf iedbtools-utilities/.git

# # --- PyPA-Packaged Executable 3rd-party tools
# git clone -b 'v4.1.2' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/netmhc-4.0-executable.git
# rm -rf netmhc-4.0-executable/.git
# git clone -b 'v4.1.0.9' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/netmhcpan-4.1-executable.git
# rm -rf netmhcpan-4.1-executable/.git
# # version 1.2 for mhcflurry
# git clone -b 'v1.0.0' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/mhcflurry-2.0-predictor.git
# rm -rf mhcflurry-2.0-predictor/.git


# # PyPA-Packaged for LJI tools
# git clone -b 'v0.1.1' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/tools-redesign/backend-dependencies/mhci-comblib-predictor.git
# rm -rf mhci-comblib-predictor/.git
# git clone -b 'v0.1.0' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/tools-redesign/backend-dependencies/smm-predictor.git
# rm -rf smm-predictor/.git


# # --- Predictor percentile distributions (MHCI)
# git clone -b 'v3.0' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/predictor-percentile-data/mhci-ann-predictor-percentile-data.git
# rm -rf mhci-ann-predictor-percentile-data/.git
# git clone -b 'v1.0.1' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/predictor-percentile-data/mhci-netmhcpan-4.1-ba-percentile-data.git
# rm -rf mhci-netmhcpan-4.1-ba-percentile-data/.git
# git clone -b 'v1.0.1' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/predictor-percentile-data/mhci-netmhcpan-4.1-el-percentile-data.git
# rm -rf mhci-netmhcpan-4.1-el-percentile-data/.git
# git clone -b 'v1.0.0' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/predictor-percentile-data/mhci-smm-percentile-data.git
# rm -rf mhci-smm-percentile-data/.git
# git clone -b 'v1.0.0' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/predictor-percentile-data/mhci-comblib_sidney2008-percentile-data.git
# rm -rf mhci-comblib_sidney2008-percentile-data/.git
# git clone -b 'v1.0.0' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/predictor-percentile-data/mhcflurry-2.0-percentile-data.git
# rm -rf mhcflurry-2.0-percentile-data/.git
# git clone -b 'v1.0.1' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/predictor-percentile-data/mhcnp-percentile-data.git
# rm -rf mhcnp-percentile-data/.git

# # Install necessary methods for NetChop/NetCTL/NetCTLpan
# git clone -b 'v3.1.0.10' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/netchop-3.1-executable.git
# rm -rf netchop-3.1-executable/.git
# git clone -b 'v1.1.0.13' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/netctl-1.1-executable.git
# rm -rf netctl-1.1-executable/.git
# mv netctl-1.1-executable netctl
# git clone -b 'v1.1.0.9' --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/djangotools-deps/netctlpan-1.1-executable.git
# rm -rf netctlpan-1.1-executable/.git

# #nxg-tools==0.0.1
# git clone --single-branch --depth 1 https://gitlab+deploy-token-27:Qzryvs2zxDh3d131tdkY@gitlab.lji.org/iedb/tools/tools-redesign/global-dependencies/nxg-tools.git
# rm -rf nxg-tools/.git

# # create a version file and add the version and date
# echo ${TOOL_VERSION} > VERSION
# date >> VERSION

# remove all ._ files
cd $BUILD_DIR
find . -type f -name '._*' -delete

cd $BUILD_DIR/..

tar -czf IEDB_BCRMATCH-${TOOL_VERSION}.tar.gz $TOOL_NAME
