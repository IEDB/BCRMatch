# BCRMatch

> **_NOTE:_** <br>
> TCRMatch is required to run BCRMatch. Currently, Docker is using [Harbor TCRMatch](https://harbor.lji.org/harbor/projects/5/repositories/iedb-public%2Ftcrmatch/tags/0.1.1) as the base image.

### Docker
It is possible to run this inside a Docker container.
1. Build image form `Dockerfile`:
    ```
    docker build -t bcrmatch .
    ```
2. Run the container with a volume mounted to the current directory:
   ```
   docker run -it -v $(pwd):/src/bcrmatch bcrmatch /bin/bash
   ```


### Running BCRMatch
Here is an example of how to run BCRMatch:
```
python run_bcrmatch.py -i ./examples/example.tsv -tc datasets/abpairs_abligity.csv
```
```
python run_bcrmatch.py -ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta -cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta
```
```
python run_bcrmatch.py -i ./examples/example.tsv -tc datasets/abpairs_abligity.csv -tm
```

#### Running inside the container

All of the command line arguments can be stored in the ```BCRMATCH_ARGS``` environment variable.
This makes passing parameters that include special characters more consistent across platforms. For
example:

```
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
> * `--training_mode`/`-tm`: Sets the program to perform only training.
> * `--training-dataset-csv`/`-tc`: Path to the CSV file that will be used for training.
>
> Optional flags:
> * `--training_dataset-version`/`-tv`:  A version number of the dataset (default=`v1`).
> * `--force-training`/`-f`: Force classifiers to be retrained under the same dataset.

Here is an example on training classifiers with `Abligity` dataset.
```
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
```
python run_bcrmatch.py -tm -tc datasets/abpairs_abligity.csv -tv v1 -f
```

## Prediction


#### What gets outputted?
It currently outputs 2 pickled classifiers (`gnb_classifier.pkl`, `rf_classifier.pkl`) and a final output file in CSV.