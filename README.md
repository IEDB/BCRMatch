# BCRMatch

BCRMatch is a tool that accepts sequences of CDR loops of antibodies, and uses the pre-trained machine learning models developed in this study to predict which antibodies recognize the same epitope.

> **Note**: Please contact us at help@iedb.org if you wish to use antibody structure, in addition to sequence, for making predictions.

> **Releases**: All releases can be found in the [tags](https://github.com/IEDB/BCRMatch/tags) section of this repository.

> **Downloads**: Any future versions of BCRMatch can be found from the following links.
> - [IEDB Downloads Server](https://downloads.iedb.org/tools/bcrmatch/)
> - [Next-Gen Tools Downloads Page](https://nextgen-tools.iedb.org/download-all)


## Prerequisites:

+ Docker (for running in containerized environment)
  * https://www.docker.com/

+ Python 3.9 or higher
  * http://www.python.org/

+ Required Python packages:
  * numpy
  * pandas
  * scikit-learn
  * xgboost
  * tensorflow
  * torch

+ Dependency tool:
  * TCRMatch 
    * https://github.com/IEDB/TCRMatch



## Installation

### 1. Prebuilt docker image (recommended)

Pull and run the pre-built image:

```bash
docker pull harbor.lji.org/iedb-public/bcrmatch:latest
docker tag harbor.lji.org/iedb-public/bcrmatch:latest bcrmatch
```

> **_NOTE_**: On ARM-based systems (e.g., Mac M1/M2/M3), you may also need to pass the ``--platform=linux/amd64`` command line switch to every Docker command.<br><br>Although it seems to build properly on some ARM machines, the tensorflow libraries may cause issues and the image may be unusable.

### 2. Local Installation

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

To view all available command-line arguments:
```bash
python run_bcrmatch.py -h
# or
python run_bcrmatch.py --help
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

### Running with Docker

Using a TSV file:
```bash
docker run --rm -v $(pwd):/src/bcrmatch bcrmatch bash -c "python3 run_bcrmatch.py -i /src/bcrmatch/examples/set-a/example.tsv -tn abpairs_abligity"
```

Using FASTA files:
```bash
docker run --rm -v $(pwd):/src/bcrmatch bcrmatch bash -c "python3 run_bcrmatch.py \
-ch /src/bcrmatch/examples/set-a/cdrh1_input.fasta /src/bcrmatch/examples/set-a/cdrh2_input.fasta /src/bcrmatch/examples/set-a/cdrh3_input.fasta \
-cl /src/bcrmatch/examples/set-a/cdrl1_input.fasta /src/bcrmatch/examples/set-a/cdrl2_input.fasta /src/bcrmatch/examples/set-a/cdrl3_input.fasta \
-tn abpairs_abligity"
```

Saving output to a file (output_file.csv will be in your current directory):
```bash
docker run --rm -v $(pwd):/src/bcrmatch bcrmatch bash -c "python3 run_bcrmatch.py -i /src/bcrmatch/examples/set-a/example.tsv -tn abpairs_abligity -o /src/bcrmatch/output_file.csv"
```

## Training

## Anarci

> **Important**: ANARCI functionality is only available through Docker containers due to Python package incompatibility issues. Local installation is not supported.

For processing full antibody sequences:

1. Prebuilt docker image
```bash
docker pull harbor.lji.org/iedb-public/bcrmatch-anarci:latest
docker tag harbor.lji.org/iedb-public/bcrmatch-anarci:latest bcrmatch-anarci
```

2. Run with full sequences:
```bash
docker run -it bcrmatch-anarci /bin/bash

python run_bcrmatch.py -fh examples/set-c/updated_example_vh_seqs.fasta -fl examples/set-c/updated_example_vl_seqs.fasta -tn abpairs_abligity
```

## Contact

For questions, bug reports, or feature requests, please contact us at help@iedb.org.
