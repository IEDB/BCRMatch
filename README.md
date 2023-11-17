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
python run_bcrmatch.py -i ./examples/example.tsv
```
```
python run_bcrmatch.py -ch examples/cdrh1_seqs.fasta examples/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta -cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta
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

#### What gets outputted?
It currently outputs 2 pickled classifiers (`gnb_classifier.pkl`, `rf_classifier.pkl`) and a final output file in CSV.