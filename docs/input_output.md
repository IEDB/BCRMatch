## Input format

Input can be provided in either TSV format with 1 row per antibody or 6 paired fasta files.

### TSV input format

A TSV file containing sequences of 3 CDRLs and 3 CDRHs is accepted.

| Seq_Name | CDRL1   | CDRL2 | CDRL3    | CDRH1   | CDRH2  | CDRH3        |
| -------- | ------- | ----- | -------- | ------- | ------ | ------------ |
| 1        | NNIGSKS | DDS   | WDSSSDHA | GFTFDDY | SWNTGT | RSYVVAAEYYFH |
| 2        | SQDISNY | YTS   | DFTLPF   | GYTFTNY | YPGNGD | GGSYRYDGGFD  |
| 3        | ASGNIHN | YYT   | HFWSTPR  | GFSLTGY | WGDGN  | RDYRLD       |

> **_NOTE_**: See `examples/set-a/example.tsv` as well.

To use the TSV file as input, `--input-tsv`/`-i` must be used.

```bash
python run_bcrmatch.py -i ./examples/set-a/example.tsv -tn abpairs_abligity
```

#### Paired FASTA input format

A set of 3 heavy chain CDR and 3 light chain CDR FASTA files can be accepted as input with the ``-ch`` and ``-cl`` options, respectively. `<br>`

Each FASTA file must be of the same length.  See the
FASTA files in the `examples` directory.

To submit paired FASTA files as input, use `--input-cdrh`/`-ch` for CDRH FASTA files and `--input-cdrl`/`-cl` for CDRL FASTA files.

```bash
python run_bcrmatch.py \
-ch examples/cdrh1_seqs.fasta examples/set-a/cdrh2_seqs.fasta examples/cdrh3_seqs.fasta \
-cl examples/cdrl1_seqs.fasta examples/cdrl2_seqs.fasta examples/cdrl3_seqs.fasta \
-tn abpairs_abligity
```

### Output format

The output file will be generated as a CSV file. It will contain all the prediction scores from each classifiers, and percentile ranks for each prediction scores.

| Antibody pair | RF Prediction          | RF Percentile Rank | LR Prediction          | LR Percentile Rank | GNB Prediction        | GNB Percentile Rank | XGB Prediction | XGB Percentile Rank | FFNN Prediction | FFNN Percentile Rank |
| ------------- | ---------------------- | ------------------ | ---------------------- | ------------------ | --------------------- | ------------------- | -------------- | ------------------- | --------------- | -------------------- |
| 1_1           | 0.9213664158986034     | 99.96176330012132  | 0.9999999999994706     | 99.9544100886062   | 0.9530043907614975    | 99.99889701827273   | 0.53367907     | 99.93896834442442   | 0.19919458      | 99.86470090812162    |
| 1_2           | 0.0031097953602010797  | 90.79083789845214  | 2.2318461017302968e-06 | 29.20180889003272  | 6.792526580672553e-05 | 13.578072723261885  | 0.00011318268  | 80.95481451523953   | 6.599952e-05    | 28.835618956579285   |
| 1_3           | 0.00020557564409447987 | 6.341777271223206  | 9.907540468928734e-07  | 18.316114563035406 | 4.057680904118906e-06 | 0.6669362844222214  | 2.131753e-05   | 20.665833302694953  | 1.373775e-05    | 2.950843781021361    |

One row per antibody and a set of two columns per predictor:

* The ``Prediction`` column indicates the score for the given predictor (higher is better).
* The ``Percentile Rank`` column indicates the rank of the score within a set of ~300,000 random scores (Range: 0-100; lower is better).