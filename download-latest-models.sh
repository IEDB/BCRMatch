#!/bin/bash

model_file="models.tgz"

# Remove models.tgz file if already exists
if [ -e "$model_file" ]; then
    rm "$model_file"
    echo "Successfully removed existing models.tgz file."
fi

# pull the latest models
echo "Downloding the latest models"
wget https://downloads.iedb.org/datasets/bcrmatch-data/LATEST/models.tgz

# unzip - this will expand to include dataset-db & the pickles directory
# and will overwrite anything in the current directory without asking
tar -xvzf models.tgz

rm models.tgz