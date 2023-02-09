#!/usr/bin/env python
import sys, getopt
from bcrmatch import bcrmatch_functions
import os
from subprocess import Popen, PIPE

def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:",["ifile="])
   except getopt.GetoptError:
      print ('test.py -i <inputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('test.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   print ('Input file is ', inputfile)
   print ('Output file is ', outputfile)

if __name__ == "__main__":
	main(sys.argv[1:])
	IFH1 = open(sys.argv[2], "r")
	file_list = []
	for file_id in IFH1.readlines():
		file_name = file_id.strip("\n")

		seq_dict = bcrmatch_functions.create_tcrmatch_input(file_name)
		print(seq_dict)
		tcrinput_file = file_name.split(".fasta")
		tcrinput = tcrinput_file[0]+"_tcrinput.txt"
		tcrout = tcrinput_file[0]+"_tcrout"
		print(tcrinput)
		OFH = open(tcrout, "w")


	#cmd = ./tcrmatch -i /home/mjarjapu/non_em/TCRMatch-1.0.2/tcrmatch_sarscov2/scv2_cdrl1_aligned_seq_tcrinput.txt -t 10 -s 0 -d  /home/mjarjapu/non_em/TCRMatch-1.0.2/tcrmatch_sarscov2/scv2_cdrl1_aligned_seq_tcrinput.txt  > /home/mjarjapu/non_em/TCRMatch-1.0.2/test_subprocess

		cmd = ['./tcrmatch', '-i', '/home/mjarjapu/non_em/TCRMatch-1.0.2/%s'% tcrinput, '-t', '10', '-s', '0', '-d','/home/mjarjapu/non_em/TCRMatch-1.0.2/%s'% tcrinput]

		process = Popen(cmd,stdout=PIPE)
		stdoutdata, stderrdata_ignored = process.communicate()
		stdoutdata = stdoutdata.decode()
		OFH.write(stdoutdata)
		OFH.close()
		bcrmatch_functions.create_tcroutput(tcrout, seq_dict)
		res = stdoutdata.split('\n')

		print(res)
