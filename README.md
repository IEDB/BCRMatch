# BCRMatch

BCRMatch is a tool that accepts sequences of CDR loops of antibodies (with and without known epitopes), and uses the pre-trained machine learning models developed in this study to predict which antibodies recognize the same epitope.

## Installation

### Docker (recommended)

Follow these steps to run the program using Docker.

1. Build image from `Dockerfile`:
    ```bash
    docker build -t bcrmatch .
    ```
2. Run the container with a volume mounted to the current directory:
   ```bash
   docker run -it -v $(pwd):/src/bcrmatch bcrmatch /bin/bash
   ```

**NOTE**: On ARM-based systems (e.g., Mac M1/M2/M3), you may also need to pass the ```--platform=linux/amd64``` command line
switch to every Docker command.

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

@hkim this should be a simple script that uses curl/wget to pull files from the downloads server

Run the script ```dataset-download.sh``` to download the most up-to-date pre-trained datasets from the IEDB servers:

```bash
sh dataset-download.sh
```

## Usage

Example commands for using BCRMatch are shown as if running locally or when attached to the container.  Example commands for running BCRMatch
from outside of the container are in the section "`Running outside fo the container`" below.


### Prediction

@hkim please fill this in

#### Input format

@hkim please fill this in

#### Output format

@hkim please fill this in

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
