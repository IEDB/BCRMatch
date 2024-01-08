# BCRMatch

> **_NOTE:_** <br>
> TCRMatch is required to run BCRMatch. Currently, Docker is using [Harbor TCRMatch](https://harbor.lji.org/harbor/projects/5/repositories/iedb-public%2Ftcrmatch/tags/0.1.1) as the base image.


## Setup
### Linux
> **_NOTE_**<br>
> Highly suggest to setup virtual environment with `Python 3.8.10`.

1. Install requirements.
    ```bash
    pip install -r requirements.txt
    ```


### Docker
Follow the steps to run the program through Docker.
1. Build image form `Dockerfile`:
    ```bash
    docker build -t bcrmatch .
    ```
2. Run the container with a volume mounted to the current directory:
   ```bash
   docker run -it -v $(pwd):/src/bcrmatch bcrmatch /bin/bash
   ```


#### Running inside the container

All of the command line arguments can be stored in the ```BCRMATCH_ARGS``` environment variable.
This makes passing parameters that include special characters more consistent across platforms. For
example:

```bash
docker run -it -e BCRMATCH_ARGS="-ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta -cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta" \
bcrmatch
```

#### What is the Input?
BCRMatch requires sequences of each of the 6 CDR loops of the antibodies.<br>Typically, all the sequence files will be in `FASTA` format.
<br><br>
As of now, in order to minimize input parameters, all of the sequence file names are added to the `text.txt` file.
```
cdrh1_seqs.fasta
cdrh2_seqs.fasta
cdrh3_seqs.fasta
cdrl1_seqs.fasta
cdrl2_seqs.fasta
cdrl3_seqs.fasta
```

## Training classifiers
Users can specify dataset that the classifiers can be trained on. If the user provides the path to the dataset and the version for that dataset, all 5 classifiers (`rf`, `gnb`, `log_reg`, `xgb`, and `ffnn`) will be trained and storted under `pickles` folder.

> **_NOTE_**<br>
> Required flags:
> * `--training-mode`/`-tm`: Sets the program to perform only training.
> * `--training-dataset-csv`/`-tc`: Path to the CSV file that will be used for training.
>
> Optional flags:
> * `--training-dataset-version`/`-tv`:  A version number of the dataset (default=`v1`).
> * `--force-training`/`-f`: Force classifiers to be retrained under the same dataset.

Here is an example on training classifiers with `Abligity` dataset.
```bash
python run_bcrmatch.py -tm -tc datasets/abpairs_abligity.csv
```
The record (training dataset file, trained classifiers, etc.) will be stored in the `dataset-db` file with a <i>default version</i> as 1.

To specify versioning for the record, use `-tv`/`--training-dataset-version`
```bash
python run_bcrmatch.py -tm -tc datasets/abpairs_abligity.csv -tv v1
```
The above code will save the classifier as a pickle file and save it to `pickles/<dataset_name>/<dataset_version>/<classifier>_<dataset_name>.pkl`.
> **_EXAMPLE_**<br>
> The `rf_classifier` that's trained under `v1` of `Abligity` dataset will be saved to `pickles/abpairs_abligity/v1/rf_abpairs_abligity.pkl`

### Force training
If same dataset and dataset version is provided to train, the program will raise an error.
```
Exception: All models have already been train under the abpairs_abligity (v1) dataset.
```

However, if classifiers still needs to be updated with the same dataset, use the `--force-training`/`-f` flag.<br>
This will force the program to retrain the classifiers.
```bash
python run_bcrmatch.py -tm -tc datasets/abpairs_abligity.csv -tv v1 -f
```

## Prediction

### Run BCRMatch prediction
Here is an example of how to run BCRMatch prediction mode:
```bash
python run_bcrmatch.py -i ./examples/example.tsv -tn abpairs_abligity
```
> **_NOTE_**<br>
> Required flags:
> * `--input-tsv`/`-i`: TSV file containing information about CDRLs and CDRHs.
> * `--training-dataset-name`/`-tn`: This will be used to lookup dataset in the database during prediction.
>
> Optional flags:
> * `--input-cdrh`/`-ch`: FASTA file containing CDRH sequence.
> * `--input-cdrl`/`-cl`: FASTA file containing CDRL sequence.
> * `--training-dataset-version`/`-tv`:  A version number of the dataset (default=`v1`).

<br>

BCRMatch can also take in individual files (<i>3 CDRH FASTA files</i> and <i>3 CDRL FASTA files</i>) as input stead of a TSV file.
```bash
python run_bcrmatch.py -ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta -cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta -tn abpairs_abligity
```


#### What gets outputted?
It currently outputs a CSV file (<i>default: `output.csv`</i>) that contains prediction data for 5 different models (`RF`, `LR`, `GNB`, `XGB`, and `FFNN`).