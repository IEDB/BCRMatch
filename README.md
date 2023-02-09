# BCRMatch

Instructions:

1. Download the fasta files and text.txt files into a directory. The fasta files contain sequences of each of the 6 CDR loops of the antibodies.
2. Download the .csv file which is used as a sample training dataset for the ML models.
3. Line 44 in 'user_input.py' has to be modified to include 2 paths: Path 1 to directory containing TCRMatch source code. Path 2 to directory containing 6 fasta files and the text.txt file


4. Run the script as follows:

sh bcrmatch_pipeline.sh

5. This generates intermediate files and a final output file, 'output.csv', with each row corresponding to an antibody pair. Column 1 is the antibody pair, Column 2 is the prediction made by the Random Forest model, Column 3 is the prediction made by the GNB model. Column 4 states whether the antibody pair binds to the same epitope (1) or does not bind to the same epitope (0)

## Getting started










## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
