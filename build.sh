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

# remove all ._ files
cd $BUILD_DIR
find . -type f -name '._*' -delete

cd $BUILD_DIR/..

tar -czf IEDB_BCRMATCH-${TOOL_VERSION}.tar.gz $TOOL_NAME
