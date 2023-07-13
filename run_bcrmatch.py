import argparse
import os
import csv
import tempfile
from pathlib import Path
from bcrmatch import bcrmatch_functions, classify_abs
from subprocess import Popen, PIPE


# Absolute path to the TCRMatch program
TCRMATCH_PATH = os.getenv('TCRMATCH_PATH', '/src/bcrmatch')


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='user_input.py',
        usage='%(prog)s [options]'
    )
    parser.add_argument("-i", "--inputFile", help="Text file containing list of cdrh/cdrl FASTA file names.", required=True)

    return parser.parse_args()


def compile_scores(file_name):
	score_dict = {}
	IFH1 = open(file_name, "r")
	lines1 = IFH1.readlines()
        
	for line1 in lines1:
		line1 = line1.strip("\n")
		line1 = line1.split(",")
		pair_id = line1[0]
		score = line1[1]
		if pair_id not in score_dict:
			score_dict[pair_id] = score
                        
	return(score_dict)


def run_classify(tcrout_files) :
    all_score_dict = {}
    dict_1 = compile_scores(tcrout_files[0])
    dict_2 = compile_scores(tcrout_files[1])
    dict_3 = compile_scores(tcrout_files[2])
    dict_4 = compile_scores(tcrout_files[3])
    dict_5 = compile_scores(tcrout_files[4])
    dict_6 = compile_scores(tcrout_files[5])


    for pair in dict_1.keys():
        if pair not in all_score_dict.keys():
            all_score_dict[pair] = []
            all_score_dict[pair].append(dict_1[pair])
            all_score_dict[pair].append(dict_2[pair])
            all_score_dict[pair].append(dict_3[pair])
            all_score_dict[pair].append(dict_4[pair])
            all_score_dict[pair].append(dict_5[pair])
            all_score_dict[pair].append(dict_6[pair])
        elif pair in all_score_dict.keys():
            all_score_dict[pair].append(dict_1[pair])
            all_score_dict[pair].append(dict_2[pair])
            all_score_dict[pair].append(dict_3[pair])
            all_score_dict[pair].append(dict_4[pair])
            all_score_dict[pair].append(dict_5[pair])
            all_score_dict[pair].append(dict_6[pair])

    #print(all_score_dict)

    X_train, y_train = classify_abs.preprocess_ml_dataset("test_subset_iedb_ml_dataset_filtered.csv")
    #print(X_train)
    #print(y_train)

    rf_classifier = classify_abs.RF(X_train, y_train)
    gnb_classifier = classify_abs.GNB(X_train, y_train)

    with open("output_hk.csv", "w", newline='') as csvfile:
        outfile_writer = csv.writer(csvfile, delimiter=',')
        outfile_writer.writerow(["Antibody pair","RF Prediction", "GNB Prediction"])
        for ab_pair in all_score_dict.keys():
            rowline = []
            rowline.append(ab_pair)
            #input_data = classify_abs.preprocess_input_data([0.98,1,1,1,1,0.98])
            input_data = classify_abs.preprocess_input_data(all_score_dict[ab_pair])
            #print(input_data)

            output_rf = rf_classifier.predict(input_data)
            output_gnb = gnb_classifier.predict(input_data)

            #print(output_rf)
            #print(output_gnb)

            if output_rf == 0:
                if output_gnb == 0:
                    #print("Doesn't bind to same epitope as given antibody\n")
                    rowline.append(output_rf)
                    rowline.append(output_gnb)
                    rowline.append("0")
                elif output_gnb == 1:
                    #print("Binds to same epitope as given antibody\n")
                    rowline.append(output_rf)
                    rowline.append(output_gnb)
                    rowline.append("1")
            elif output_rf == 1:
                #print("Binds to same epitope as given antibody\n")
                rowline.append(output_rf)
                rowline.append(output_gnb)
                rowline.append("1")
            outfile_writer.writerow(rowline)



def get_tcr_output_files(ifh1, input_files_path) :
    tcrout_filenames = []
    for input_file_name in ifh1 :
        # Get full path to individual example input FASTA file
        input_file_name = input_files_path + '/' + input_file_name
                
        seq_dict = bcrmatch_functions.create_tcrmatch_input_hk(input_file_name)
        
        # Create temporary file containing 'seq_dict' to be used as input for TCRMatch
        with tempfile.NamedTemporaryFile(mode = 'w', prefix='tcr_', suffix='_input', delete=False) as tmp :
            tmp.write('\n'.join(list(seq_dict.values())))

        # Run TCRMatch
        cmd = ['/src/bcrmatch/TCRMatch-0.1.1/tcrmatch', '-i', '%s' %(tmp.name), '-t', '10', '-s', '0', '-d','%s' %(tmp.name)]
        process = Popen(cmd,stdout=PIPE)
        stdoutdata, stderrdata_ignored = process.communicate()
        stdoutdata = stdoutdata.decode().strip()
        
        # Format the results into a file
        tcr_output_result = bcrmatch_functions.create_tcroutput_hk(stdoutdata, seq_dict)

        with tempfile.NamedTemporaryFile(mode = 'w', prefix='tcr_', suffix='_output', delete=False) as tmp :
            tmp.write(tcr_output_result)
            tcrout_filenames.append(tmp.name)

        # TODO: Clean up the input temporary files

    return tcrout_filenames


def main():
    args = parse_arguments()
    bcr_input_filenames = []
    pdir = str(Path(args.inputFile).parent.absolute())
    with open(args.inputFile, "r") as f :
        bcr_input_filenames = [_.strip() for _ in f.readlines()]

    print("Retrieving all files containing the TCRMatch result...")
    tcrout_files = get_tcr_output_files(bcr_input_filenames, pdir)
    
    print("Classifying...")
    # Get the final output in CSV file
    run_classify(tcrout_files)
    print("Completed!")

if __name__ == "__main__":
    main()	