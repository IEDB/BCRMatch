# BCRMatch

### Prerequisites
> **_NOTE:_** <br>
> TCRMatch is required to run BCRMatch. Currently, it's using TCRMatch standalone (https://gitlab.lji.org/iedb/tools/standalone-tools/TCRMatch).

Once TCRMatch is downloaded from the repository, navigate inside the standalone and run the `Makefile`:
```
make
```

Set the path to TCRMatch in the environment variable `TCRMATCH_PATH`.
```
export TCRMATCH_PATH=<PATH_TO_TCRMATCH_PATH>
```

Finally, make sure all the requirements are installed.
```
pip install -r requirements.txt
```

### Docker
It is possible to run this inside a Docker container.
1. Make sure TCRMatch is in the current working directory.
2. Build image form `Dockerfile`:
    ```
    docker build -t bcrmatch_img .
    ```
3. Run the container with a volume mounted to the current directory:
   ```
   docker run -d -v $(pwd):/src/bcrmatch --name bcrmatch_container bcrmatch_img
   ```
4. Navigate inside the container:
   ```
   docker exec -it bcrmatch_img /bin/bash
   ```


### Running BCRMatch
Here is an example of how to run BCRMatch:
```
python run_bcrmatch.py -i ./examples/text.txt
```

#### What's in text.txt?
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