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

# Replace the title in README.md with version
if [[ "$(uname)" == "Darwin" ]]; then
    # For MacOS
    sed -i "" "1s/^# BCRMatch$/# BCRMatch v${TOOL_VERSION}/" "$BUILD_DIR/README.md"
else
    # For Linux
    sed -i "1s/^# BCRMatch$/# BCRMatch v${TOOL_VERSION}/" "$BUILD_DIR/README.md"
fi

# Generate underline based on title length
# TITLE="BCRMatch - version ${TOOL_VERSION}"
# UNDERLINE=$(printf '=%.0s' $(seq 1 ${#TITLE}))

# # Replace the underline in README.md
# if [[ "$(uname)" == "Darwin" ]]; then
#     # For MacOS
#     sed -i "" "s/^=.*$/${UNDERLINE}/" "$BUILD_DIR/README.md"
# else
#     # For Linux
#     sed -i "s/^=.*$/${UNDERLINE}/" "$BUILD_DIR/README.md"
# fi

# remove all ._ files
cd $BUILD_DIR
find . -type f -name '._*' -delete

cd $BUILD_DIR/..

tar -czf IEDB_BCRMATCH-${TOOL_VERSION}.tar.gz $TOOL_NAME
