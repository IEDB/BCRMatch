# BCRMatch

BCRMatch is a tool that accepts sequences of CDR loops of antibodies, and uses the pre-trained machine learning models developed in this study to predict which antibodies recognize the same epitope.

> **Note**: Please contact us at help@iedb.org if you wish to use antibody structure, in addition to sequence, for making predictions.

> **Releases**: All releases can be found in the [tags](https://github.com/IEDB/BCRMatch/tags) section of this repository.

> **Downloads**: Any future versions of BCRMatch can be found from the following links.
> - [IEDB Downloads Server](https://downloads.iedb.org/tools/bcrmatch/)
> - [Next-Gen Tools Downloads Page](https://nextgen-tools.iedb.org/download-all)


## Installation

There are 2 methods for installing and using the tool.  We highly recommend using the Docker container, but
installing locally is also an option.

### Prebuilt docker image (recommended)

#### Prerequisites

+ Docker (for running in containerized environment)
  * https://www.docker.com/

#### Installation steps

1. Pull and run the pre-built image:

```bash
docker pull harbor.lji.org/iedb-public/bcrmatch:latest
docker tag harbor.lji.org/iedb-public/bcrmatch:latest bcrmatch
```

> **_NOTE_**: On ARM-based systems (e.g., Mac M1/M2/M3), you may also need to pass the ``--platform=linux/amd64`` command line switch to every Docker command.<br><br>Although it seems to build properly on some ARM machines, the tensorflow libraries may cause issues and the image may be unusable.

### Local Installation

#### Prerequisites:

+ Python 3.9 or higher
  * http://www.python.org/

+ Required Python packages:
  * numpy
  * pandas
  * scikit-learn
  * xgboost
  * tensorflow
  * torch

+ Additonal tool:
  * TCRMatch 
    * https://github.com/IEDB/TCRMatch

#### Installation steps

1. Install Python requirements:
```bash
pip install -r requirements.txt
```

2. Set environment variable to TCRMatch path :
```bash
export TCRMATCH_PATH=/path/to/tcrmatch_dir
```

3. Download pre-trained models (optional, but recommended):
```bash
sh dataset-download.sh
```

## Usage

### Running with Docker

Using a TSV file:
```bash
docker run --rm \
-v $(pwd):/output \
bcrmatch bash -c \
"python3 run_bcrmatch.py \
-i /src/bcrmatch/examples/set-a/example.tsv \
-tn abpairs_abligity \
-o /output/output_file.csv"
```

Using FASTA files:
```bash
docker run --rm \
-v $(pwd):/output \
bcrmatch bash -c \
"python3 run_bcrmatch.py \
-ch /src/bcrmatch/examples/set-a/cdrh1_input.fasta /src/bcrmatch/examples/set-a/cdrh2_input.fasta /src/bcrmatch/examples/set-a/cdrh3_input.fasta \
-cl /src/bcrmatch/examples/set-a/cdrl1_input.fasta /src/bcrmatch/examples/set-a/cdrl2_input.fasta /src/bcrmatch/examples/set-a/cdrl3_input.fasta \
-tn abpairs_abligity \
-o /output/output_file.csv"
```

The examples above are relying on input files that exist inside the container, but the user
can reference a file on the host system by mounting the directory containing the input files as a volume, e.g.,:

```bash
docker run --rm \
-v /path/to/input:/input \
-v $(pwd):/output \
bcrmatch bash -c \
"python3 run_bcrmatch.py \
-i /input/input.tsv \
-tn abpairs_abligity \
-o /output/output_file.csv"
```

To view all available command-line arguments:
```bash
docker run --rm bcrmatch python3 run_bcrmatch.py -h
```

#### Predicting with full-length heavy and light-chain variable domain sequences using ANARCI to extract CDRs

> **Important**: ANARCI functionality is only available through Docker due to a Python package incompatibility issue. Local 

1. Download and tag the '-anarci' version of the container image.
```bash
docker pull harbor.lji.org/iedb-public/bcrmatch-anarci:latest
docker tag harbor.lji.org/iedb-public/bcrmatch-anarci:latest bcrmatch-anarci
```

2. Run a prediction with full-length sequences:
```bash
docker run --rm \
-v $(pwd):/output \
-e BCRMATCH_ARGS="-fh examples/set-c/updated_example_vh_seqs.fasta -fl examples/set-c/updated_example_vl_seqs.fasta -tn abpairs_abligity -o /output/output_file.csv" \
bcrmatch-anarci
```

### Running Locally

Using a TSV file:
```bash
python run_bcrmatch.py -i examples/set-a/example.tsv -tn abpairs_abligity
```

Using FASTA files:
```bash
python run_bcrmatch.py \
-ch examples/set-a/cdrh1_input.fasta examples/set-a/cdrh2_input.fasta examples/set-a/cdrh3_input.fasta \
-cl examples/set-a/cdrl1_input.fasta examples/set-a/cdrl2_input.fasta examples/set-a/cdrl3_input.fasta \
-tn abpairs_abligity
```

Saving output to a file:
```bash
python run_bcrmatch.py -i examples/set-a/example.tsv -tn abpairs_abligity -o output_file.csv
```

To view all available command-line arguments:
```bash
python run_bcrmatch.py -h
```

## Contact

For questions, bug reports, or feature requests, please contact us at help@iedb.org.
