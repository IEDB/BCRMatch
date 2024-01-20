#!/bin/bash

# pull the latest models
echo "Downloding the latest models"
wget https://downloads.iedb.org/datasets/bcrmatch-data/LATEST/models.tgz

# unzip - this will expand to include dataset-db & the pickles directory
# and will overwrite anything in the current directory without asking
tar -xvzf models.tgz