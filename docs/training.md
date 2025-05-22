## Training

This step is only necessary if you have a custom dataset upon which to train.  Otherwise, it is recommended to download the pre-trained
models from the IEDB (described above).

Users can specify the dataset that the classifiers can be trained on. If the user provides the path to the dataset, all 5 classifiers (`rf`, `gnb`, `log_reg`, `xgb`, and `ffnn`) will be trained and stored under the `modules` folder.

> Required flags:
>
> * `--training-mode`/`-tm`: Sets the program to perform only training.
> * `--training-dataset-csv`/`-tc`: Path to the CSV file that will be used for training.
>
> Optional flags:
>
> * `--training-dataset-version`/`-tv`:  A version number of the dataset (date format: YYYYMMDD).  This is useful if you will be maintaining multiple dataset versions.
> * `--force-training`/`-f`: Force classifiers to be retrained on an existing dataset name and version.

Example input training files can be found in the [examples](examples) directory.

```bash
python run_bcrmatch.py \
-tm \
-tc path/to/your_dataset.csv \
-tn your_dataset_name \
-tv YYYYMMDD
```

Example using the Ab-Ligity dataset:
```bash
python run_bcrmatch.py \
-tm \
-tc path/to/abpairs_abligity.csv \
-tn abpairs_abligity \
-tv 20240916
```

This will train all classifiers and save them to the models directory. By default, models are saved to `models/abpairs_abligity/20240916/`. You can specify a custom models directory using the `--models-dir` option.

The above code will save the classifier as a pickle file to `models/<dataset_name>/<dataset_version>/<classifier>_<dataset_name>.pkl`.

> **_EXAMPLE_**<br>
> The `rf_classifier` that's trained under `20240916` of `Ab-Ligity` dataset will be saved to `models/abpairs_abligity/20240916/rf_abpairs_abligity.pkl`

### Forced training

If the same dataset name and version is provided to train, the program will raise an error.

```
Exception: All models have already been train under the abpairs_abligity (20240916) dataset.
```

However, if classifiers still needs to be updated with the same dataset, use the `--force-training`/`-f` flag.
This will force the program to retrain the classifiers.

```
python run_bcrmatch.py -tm -tc path/to/abpairs_abligity.csv -tv 20240916 -f
```

### Custom directories / files

If models are stored in a separate/custom directories or `dataset-db` is saved somewhere else as a different name, then specify paths with `--models-dir`/`-md` and `--database`/`-db` flags, respectively.

```bash
python run_bcrmatch.py -tm \
-tc path/to/abpairs_abligity.csv \
-tv 20240916 \
-md custom/path/to/models/directory \
-db custom/path/to/dataset-db-file
```
