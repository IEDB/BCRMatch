# BCRMatch

BCRMatch is a tool that accepts sequences of CDR loops of antibodies, and uses the pre-trained machine learning models developed in this study to predict which antibodies recognize the same epitope.

> **Note**: Please contact us at help@iedb.org if you wish to use antibody structure, in addition to sequence, for making predictions.

## Installation

### 1. Prebuilt docker image (highly recommended)

Pull and run the pre-built image:

```bash
docker pull harbor.lji.org/iedb-public/bcrmatch:latest
docker tag harbor.lji.org/iedb-public/bcrmatch:latest bcrmatch
```

### 2. Docker build (recommended)

To build an image from `Dockerfile`:

```bash
docker build -t bcrmatch .
```

Now you can run commands using the ``bcrmatch`` container image as described below.

> **_NOTE_**: On ARM-based systems (e.g., Mac M1/M2/M3), you may also need to pass the ``--platform=linux/amd64`` command line switch to every Docker command.<br><br>Although it seems to build properly on some ARM machines, the tensorflow libraries may cause issues and the image may be unusable.


### Local Installation

1. Install Python requirements:
```bash
pip install -r requirements.txt
```

2. Install TCRMatch and set environment variable:
```bash
export TCRMATCH_PATH=/path/to/tcrmatch_dir
```

3. Download pre-trained models:
```bash
sh dataset-download.sh
```

## Usage

To view all available command-line arguments:
```bash
python run_bcrmatch.py -h
# or
python run_bcrmatch.py --help
```

### Basic Prediction

Using a TSV file:
```bash
python run_bcrmatch.py -i examples/set-a/example.tsv -tn abpairs_abligity
```

Using FASTA files:
```bash
python run_bcrmatch.py \
-ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta \
-cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta \
-tn abpairs_abligity
```


## Training

Train models on your custom dataset:

```bash
python run_bcrmatch.py \
-tm \
-tc datasets/your_dataset.csv \
-tn your_dataset_name \
-tv YYYYMMDD
```

Example using the Abligity dataset:
```bash
python run_bcrmatch.py \
-tm \
-tc datasets/abpairs_abligity.csv \
-tn abpairs_abligity \
-tv 20240916
```

This will train all classifiers and save them to the models directory. By default, models are saved to `models/abpairs_abligity/20240916/`. You can specify a custom models directory using the `--models-dir` option.

## Anarci

> **Important**: ANARCI functionality is only available through Docker containers due to Python package incompatibility issues. Local installation is not supported.

For processing full antibody sequences:

1. Prebuilt docker image
```bash
docker pull harbor.lji.org/iedb-public/bcrmatch-anarci:latest
docker tag harbor.lji.org/iedb-public/bcrmatch-anarci:latest bcrmatch-anarci
```

2. Build the ANARCI container:
```bash
docker build -t bcrmatch-anarci -f anarci.Dockerfile .
```

3. Run with full sequences:
```bash
docker run -it bcrmatch-anarci /bin/bash

python run_bcrmatch.py -fh examples/set-c/updated_example_vh_seqs.fasta -fl examples/set-c/updated_example_vl_seqs.fasta -tn abpairs_abligity
```

## Contact

For questions, bug reports, or feature requests, please contact us at help@iedb.org.
