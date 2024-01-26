# BCRMatch

BCRMatch is a tool that accepts sequences of CDR loops of antibodies (with and without known epitopes), and uses the pre-trained machine learning models developed in this study to predict which antibodies recognize the same epitope.

## Installation

There are 3 methods of installation, listed in order of our recommendation.

### Prebuilt docker image (highly recommended)

Pull the image from our public registry and tag it locally as 'bcrmatch':

```bash
docker pull harbor.lji.org/iedb-public/bcrmatch:latest
docker tag harbor.lji.org/iedb-public/bcrmatch:latest bcrmatch
```
Now you can run commands using the ```bcrmatch``` container image as described below.

### Docker build (recommended)

To build an image from `Dockerfile`:

```bash
docker build -t bcrmatch .
```

Now you can run commands using the ```bcrmatch``` container image as described below.

**NOTE**: On ARM-based systems (e.g., Mac M1/M2/M3), you may also need to pass the ```--platform=linux/amd64``` command line
switch to every Docker command.  Although it seems to build properly on some ARM machines, the tensorflow libraries may
cause issues and the image may be unusable.

### Local installation

1. Install python requirments

In a Python virtual environment, running version ```3.8.10``` or later, install the requirements with ```pip```:

```bash
pip install -r requirements.txt
```

2. Install TCRMatch

[TCRMatch](https://github.com/IEDB/TCRMatch) is also required to run BCRMatch.  If you are running via Docker (recommended), this dependency is managed by using this [Docker image](https://harbor.lji.org/harbor/projects/5/repositories/iedb-public%2Ftcrmatch/tags/0.1.1).

Once TCRMatch is installed, the ```TCRMATCH_PATH``` environment variable must be set before running BCRMatch, e.g.:

```bash
export TCRMATCH_PATH=/path/to/tcrmatch_dir
```

3. Download pre-trained datasets (optional, but recommended)

Run the script ```download-latest-models.sh``` to download the most up-to-date pre-trained datasets from the IEDB servers:

```bash
sh download-latest-model.sh
```

**NOTE:** This is a very rudimentary script that *MUST* be run from inside the BCRMatch directory.  *This script will overwrite any existing ```dataset-db``` file and model files inside the ```pickles``` directory.

## Usage

Example commands for using BCRMatch are shown as if running locally or when attached to the container.  Example commands for running BCRMatch
from outside of the container are in the section "`Running outside fo the container`" below.


### Prediction

**List available datsets**

```
$ python run_bcrmatch.py --list-datasets
Starting program...
    dataset_name  dataset_version
abpairs_abligity         20240125
    abpairs_iedb         20240125
```

**Predict using the abpairs_abligity dataset with TSV inputs**

```
$ python run_bcrmatch.py -tn abpairs_abligity -i examples/example.tsv 
Starting program...
Retrieving all files containing the TCRMatch result...
Retrieve scores as dictionary...
Writing the final output to CSV...
Completed!
```

Output is saved to ```output.csv``` by default, but can be redirected by passing the ```-o``` option.

**Predict using the abpairs_iedb model with FASTA inputs**

```
$ python run_bcrmatch.py \
-tn abpairs_iedb \
-ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta \
-cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta 
Starting program...
Retrieving all files containing the TCRMatch result...
Retrieve scores as dictionary...
Writing the final output to CSV...
Completed!
```

#### Input format

Input can be provided in either TSV format with 1 row per antibody or 6 paired fasta files.

**TSV input format**

A TSV with the following format is accepted with the ```-i``` option:

```
Seq_Name        CDRL1   CDRL2   CDRL3   CDRH1   CDRH2   CDRH3
1       NNIGSKS DDS     WDSSSDHA        GFTFDDY SWNTGT  RSYVVAAEYYFH
2       SQDISNY YTS     DFTLPF  GYTFTNY YPGNGD  GGSYRYDGGFD
3       ASGNIHN YYT     HFWSTPR GFSLTGY WGDGN   RDYRLD
4       SESVDNYGISF     AAS     SKEVPL  GYTFTSS HPNSGN  RYGSPYYFD
5       ASQDISN YFT     QYSTVPW GYDFTHY NTYTGE  PYYYGTSHWYFD
```

See (example.tsv)[examples/example.tsv] as well.


**Paired FASTA input format**

A set of 3 heavy chain CDR and 3 light chain CDR FASTA files can be accepted as input with the
```-ch``` and ```-cl``` options, respectively.  Each FASTA file must be of the same length.  See the
FASTA files in the (examples)[examples] directory.

#### Output format

Output is provided as a CSV in the following format:

```
Antibody pair,RF Prediction,RF Percentile Rank,LR Prediction,LR Percentile Rank,GNB Prediction,GNB Percentile Rank,XGB 
Prediction,XGB Percentile Rank,FFNN Prediction,FFNN Percentile Rank
```

One row per antibody and a set of two columns per predictor:

 * The ```Prediction``` column indicates the score for the given predictor (higher is better).
 * The ```Percentile Rank``` column indicates the rank of the score within a set of ~300,000 random scores (Range: 0-100; lower is better).

### Training

This step is only necessary if you have a custom dataset upon which to train.  Otherwise, it is recommended to download the pre-trained
models from the IEDB (described above).

Users can specify the dataset that the classifiers can be trained on. If the user provides the path to the dataset, all 5 classifiers (`rf`, `gnb`, `log_reg`, `xgb`, and `ffnn`) will be trained and stored under the `pickles` folder.

> Required flags:
> * `--training_mode`/`-tm`: Sets the program to perform only training.
> * `--training-dataset-csv`/`-tc`: Path to the CSV file that will be used for training.
>
> Optional flags:
> * `--training_dataset-version`/`-tv`:  A version number of the dataset (default=`v1`).  This is useful if you will be maintaining multiple dataset versions.
> * `--force-training`/`-f`: Force classifiers to be retrained on an existing dataset name and version.

Example input training files can be found in the [examples](examples) directory.

Here is an example on training classifiers with `Abligity` dataset.
```
python run_bcrmatch.py \
-tm \
-tc datasets/abpairs_abligity.csv \
-tv v1
```

The above code will save the classifier as a pickle file to `pickles/<dataset_name>/<dataset_version>/<classifier>_<dataset_name>.pkl`.
> **_EXAMPLE_**<br>
> The `rf_classifier` that's trained under `v1` of `Abligity` dataset will be saved to `pickles/abpairs_abligity/v1/rf_abpairs_abligity.pkl`

#### Forced training
If the same dataset name and version is provided to train, the program will raise an error.
```
Exception: All models have already been train under the abpairs_abligity (v1) dataset.
```

However, if classifiers still needs to be updated with the same dataset, use the `--force-training`/`-f` flag.
This will force the program to retrain the classifiers.
```
python run_bcrmatch.py -tm -tc datasets/abpairs_abligity.csv -tv v1 -f
```

### Running outside the container

All of the command line arguments can be stored in the ```BCRMATCH_ARGS``` environment variable.
This makes passing parameters that include special characters more consistent across platforms. For
example:

```
docker run \
-it \
-e BCRMATCH_ARGS="-ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta -cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta" \
bcrmatch
```

## Development notes

Gitlab CI will build container images for all tags and push them to harbor.  They will need to be manually tagged with
```latest```.