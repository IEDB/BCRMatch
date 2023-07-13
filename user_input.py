import argparse
import os
from bcrmatch import bcrmatch_functions
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


def main():
	args = parse_arguments()
	ifh1 = []
	with open(args.inputFile, "r") as f:
		ifh1 = [_.strip() for _ in f.readlines()]
	
	for file_name in ifh1:
		seq_dict = bcrmatch_functions.create_tcrmatch_input("./examples/" + file_name)
		tcrinput_fname_prefix = file_name.split(".fasta")[0]
		tcrinput_fname = tcrinput_fname_prefix + "_tcrinput.txt"
		tcroutput_fname = tcrinput_fname_prefix + "_tcrout"

		# Run TCRMatch
		# cmd = ['./tcrmatch', '-i', '%s/%s' %(TCRMATCH_PATH, tcrinput_fname), '-t', '10', '-s', '0', '-d','%s/%s' %(TCRMATCH_PATH, tcrinput_fname)]
		cmd = ['/src/bcrmatch/TCRMatch-0.1.1/tcrmatch', '-i', '%s/%s' %(TCRMATCH_PATH, tcrinput_fname), '-t', '10', '-s', '0', '-d','%s/%s' %(TCRMATCH_PATH, tcrinput_fname)]
		print(cmd)
		process = Popen(cmd,stdout=PIPE)
		stdoutdata, stderrdata_ignored = process.communicate()
		stdoutdata = stdoutdata.decode()

		# Write to output file
		with open(tcroutput_fname, "w") as f:
			f.write(stdoutdata)
		
		bcrmatch_functions.create_tcroutput(tcroutput_fname, seq_dict)
		res = stdoutdata.split('\n')
		print(res)


if __name__ == "__main__":
    main()	