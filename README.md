# BCRMatch

BCRMatch is a tool that accepts sequences of CDR loops of antibodies (with and without known epitopes), and uses the pre-trained machine learning models developed in this study to predict which antibodies recognize the same epitope.

## Installation

There are 3 methods of installation, listed in order of our recommendation.

### 1. Prebuilt docker image (highly recommended)

Pull the image from our public registry and tag it locally as `bcrmatch`:

```bash
docker pull harbor.lji.org/iedb-public/bcrmatch:latest
docker tag harbor.lji.org/iedb-public/bcrmatch:latest bcrmatch
```
Now you can run commands using the ```bcrmatch``` container image as described below.

### 2. Docker build (recommended)

To build an image from `Dockerfile`:
```bash
docker build -t bcrmatch .
```

Now you can run commands using the ```bcrmatch``` container image as described below.

> **_NOTE_**:<br>
On ARM-based systems (e.g., Mac M1/M2/M3), you may also need to pass the ```--platform=linux/amd64``` command line
switch to every Docker command.<br><br>Although it seems to build properly on some ARM machines, the tensorflow libraries may
cause issues and the image may be unusable.

Accessing inside the container to run the program:
```bash
docker run -it -v $(pwd):/src/bcrmatch bcrmatch /bin/bash
```

### 3. Local installation

1. Install python requirements

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

Run the script ```dataset-download.sh``` to download the most _up-to-date_ pre-trained datasets from the IEDB servers:

```bash
sh dataset-download.sh
```

## Usage

Example commands for using BCRMatch are shown as if running locally or when attached to the container.  Example commands for running BCRMatch
from outside of the container are in the section "`Running outside of the container`" below.


### Prediction

To perform a prediction, CDRLs and CDRHs are required along with a dataset name.<br>

> **_NOTE_**<br>
> If you don't have existing models available, please download the models using the following script.
> ```bash
> sh download-latest-models.sh
> ``` 
> This will create `models` folder that contains all the pickled models and `dataset-db` file.


Following is an example of running a simple prediction:
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
> * `--training-dataset-version`/`-tv`:  A version number of the dataset (default=`20240125`).
<br>

BCRMatch can also take in individual files (<i>3 CDRH FASTA files</i> and <i>3 CDRL FASTA files</i>) as input stead of a TSV file.
```bash
python run_bcrmatch.py \
-ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta 
-cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta 
-tn abpairs_abligity
```

Output is saved to ```output.csv``` by default, but can be redirected by passing the ```-o``` option.

**List available datsets**

```
$ python run_bcrmatch.py --list-datasets
Starting program...
    dataset_name  dataset_version
abpairs_abligity         20240125
    abpairs_iedb         20240125
```


### Input format

Input can be provided in either TSV format with 1 row per antibody or 6 paired fasta files.

#### TSV input format
A TSV file containing sequences of 3 CDRLs and 3 CDRHs is accepted.

| Seq_Name | CDRL1 | CDRL2 | CDRL3 | CDRH1 | CDRH2 | CDRH3
| -------- | ------- | ------- | -------- | ------- | ------- | ------- |
| 1 | NNIGSKS | DDS | WDSSSDHA | GFTFDDY | SWNTGT | RSYVVAAEYYFH 
| 2	| SQDISNY | YTS | DFTLPF | GYTFTNY | YPGNGD | GGSYRYDGGFD 
| 3	| ASGNIHN | YYT | HFWSTPR | GFSLTGY | WGDGN | RDYRLD 

> **_NOTE_**: See `examples/example.tsv` as well.

To use the TSV file as input, `--input-tsv`/`-i` must be used.
```bash
python run_bcrmatch.py -i ./examples/example.tsv -tn abpairs_abligity
```

#### Paired FASTA input format
A set of 3 heavy chain CDR and 3 light chain CDR FASTA files can be accepted as input with the ```-ch``` and ```-cl``` options, respectively. <br>

Each FASTA file must be of the same length.  See the
FASTA files in the `examples` directory.

To submit paired FASTA files as input, use `--input-cdrh`/`-ch` for CDRH FASTA files and `--input-cdrl`/`-cl` for CDRL FASTA files.

```bash
python run_bcrmatch.py \
-ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta \
-cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta \
-tn abpairs_abligity
```

### Output format

The output file will be generated as a CSV file. It will contain all the prediction scores from each classifiers, and percentile ranks for each prediction scores.

| Antibody pair | RF Prediction | RF Percentile Rank | LR Prediction | LR Percentile Rank | GNB Prediction | GNB Percentile Rank | XGB Prediction | XGB Percentile Rank | FFNN Prediction | FFNN Percentile Rank
| -------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- |
1_1 | 0.9213664158986034 | 99.96176330012132 | 0.9999999999994706 | 99.9544100886062 | 0.9530043907614975 | 99.99889701827273 | 0.53367907 | 99.93896834442442 | 0.19919458 | 99.86470090812162
1_2 | 0.0031097953602010797 | 90.79083789845214 | 2.2318461017302968e-06 | 29.20180889003272 | 6.792526580672553e-05 | 13.578072723261885 | 0.00011318268 | 80.95481451523953 | 6.599952e-05 | 28.835618956579285
1_3 | 0.00020557564409447987 | 6.341777271223206 | 9.907540468928734e-07 | 18.316114563035406 | 4.057680904118906e-06 | 0.6669362844222214 | 2.131753e-05 | 20.665833302694953 | 1.373775e-05 | 2.950843781021361

One row per antibody and a set of two columns per predictor:

 * The ```Prediction``` column indicates the score for the given predictor (higher is better).
 * The ```Percentile Rank``` column indicates the rank of the score within a set of ~300,000 random scores (Range: 0-100; lower is better).


### Training

This step is only necessary if you have a custom dataset upon which to train.  Otherwise, it is recommended to download the pre-trained
models from the IEDB (described above).

Users can specify the dataset that the classifiers can be trained on. If the user provides the path to the dataset, all 5 classifiers (`rf`, `gnb`, `log_reg`, `xgb`, and `ffnn`) will be trained and stored under the `modules` folder.

> Required flags:
> * `--training_mode`/`-tm`: Sets the program to perform only training.
> * `--training-dataset-csv`/`-tc`: Path to the CSV file that will be used for training.
>
> Optional flags:
> * `--training_dataset-version`/`-tv`:  A version number of the dataset (date format: YYYYMMDD).  This is useful if you will be maintaining multiple dataset versions.
> * `--force-training`/`-f`: Force classifiers to be retrained on an existing dataset name and version.

Example input training files can be found in the [examples](examples) directory.

Here is an example on training classifiers with `Abligity` dataset.
```bash
python run_bcrmatch.py \
-tm \
-tc datasets/abpairs_abligity.csv \
-tv 20240125
```

The above code will save the classifier as a pickle file to `models/<dataset_name>/<dataset_version>/<classifier>_<dataset_name>.pkl`.
> **_EXAMPLE_**<br>
> The `rf_classifier` that's trained under `20240125` of `Abligity` dataset will be saved to `models/abpairs_abligity/20240125/rf_abpairs_abligity.pkl`

#### Forced training
If the same dataset name and version is provided to train, the program will raise an error.
```
Exception: All models have already been train under the abpairs_abligity (20240125) dataset.
```

However, if classifiers still needs to be updated with the same dataset, use the `--force-training`/`-f` flag.
This will force the program to retrain the classifiers.
```
python run_bcrmatch.py -tm -tc datasets/abpairs_abligity.csv -tv 20240125 -f
```

#### Custom directories / files
If models are stored in a separate/custom directories or `dataset-db` is saved somewhere else as a different name, then specify paths with `--models-dir`/`-md` and `--database`/`-db` flags, respectively.
```bash
python run_bcrmatch.py -tm \
-tc datasets/abpairs_abligity.csv \
-tv 20240103 \
-md custom/path/to/models/directory \
-db custom/path/to/dataset-db-file
```


### Running outside the container

All of the command line arguments can be stored in the ```BCRMATCH_ARGS``` environment variable.
This makes passing parameters that include special characters more consistent across platforms. For
example:

```
docker run \
-it \
-e BCRMATCH_ARGS="-ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta -cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta -tn abpairs_abligity" \
bcrmatch
```

## Development notes

Gitlab CI will build container images for all tags and push them to harbor.  They will need to be manually tagged with
```latest```.