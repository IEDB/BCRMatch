import sys
import argparse
import textwrap
import pandas as pd


class BCRMatchArgumentParser:
    parser = argparse.ArgumentParser(
                    usage = '%(prog)s <fasta_sequence> [-a] <allele_list> [-l] <length_list>',
                    description = 'This is a command-line tool interface for BCRMatch.',
                    formatter_class=argparse.RawTextHelpFormatter)	
    
    def __init__(self):
        pass

    def parse_args(self, args):
        # Optional Arguments (Flags)
        self.parser.add_argument('--input-tsv', '-i', dest = 'input_tsv', required = False,
                            nargs = '?', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = textwrap.dedent('''
                                TSV file containing information about CDRLs and CDRHs.
                                ex)
                                    Seq_Name    CDRL1    CDRL2    CDRL3    CDRH1    CDRH2    CDRH3
                                    1   NNIGSKS     DDS    WDSSSDHA    GFTFDDY    SWNTGT    RSYVVAAEYYFH
                                    2   SQDISNY     YTS    DFTLPF    GYTFTNY    YPGNGD    GGSYRYDGGFD
                                    3   ASGNIHN     YYT    HFWSTPR    GFSLTGY    WGDGN    RDYRLD
                                    4   SESVDNYGISF     AAS    SKEVPL    GYTFTSS    HPNSGN    RYGSPYYFD
                                    5   ASQDISN     YFT    QYSTVPW    GYDFTHY    NTYTGE    PYYYGTSHWYFD
                            '''
                            ))
        self.parser.add_argument('--input-cdrh', '-ch', dest = 'cdrh_fasta', required = False,
                            nargs = '?', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = 'FASTA file containing 3 CDRHs.')
        self.parser.add_argument('--input-cdrl', '-cl', dest = 'cdrl_fasta', required = False,
                            nargs = '?', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = 'FASTA file containing 3 CDRLs.')
        self.parser.add_argument('--database', '-d', dest = 'database', required = False,
                            nargs = '+', 
                            type = str,
                            default = argparse.SUPPRESS,
                            help = 'Path to the database/json created or modified in the training.')
        self.parser.add_argument('--training-dataset-name', '-t', dest = 'dataset_name', required = False,
                            nargs = '+', 
                            type = str,
                            default = argparse.SUPPRESS,
                            help = 'Nmae of the training dataset to use for the prediction.')
        self.parser.add_argument('--output', '-o', dest = 'output', required = False,
                            nargs = '?', 
                            type = argparse.FileType('w'),
                            action='store',
                            default = argparse.SUPPRESS,
                            help = 'Path to the output file.')

        # Positional Arguments (User input parameters)
        self.parser.add_argument('inline_seqs', type = str,
                            nargs = '?',
                            help = 'Space separated peptide sequences.')


        return self.parser.parse_args(), self.parser
    

    def get_input_tsv_content(self, args, parser) :
        ''' DESCRIPTION:
            This will open the TSV file and return its content.

            Return Value: List of lists
            It returns list containing each row in a list format.   
        '''
        file_name = ''

        if 'input_tsv' in args :
            file_name = getattr(args, 'input_tsv').name
        
        return pd.read_table(file_name).to_dict('list')


    def get_sequences(self, args, parser) :
        ''' DESCRIPTION:
            The sequences in file will take precedence over inline sequence.
        '''
        file_name = ''
        sequences = ''
        
        if getattr(args, 'inline_seqs'):
            sequences = args.inline_seqs

        # Throw help message as only 1 file should be submitted.
        if ('fasta_file' in args) and ('peptide_file' in args) :
            parser.print_help()
            sys.exit(0)

        if 'fasta_file' in args :
            file_name = getattr(args, 'fasta_file').name

        if 'peptide_file' in args :
            file_name = getattr(args, 'fasta_file').name
        
        if file_name :
            with open(file_name, 'r') as f:
                sequences = f.readlines()

        # Simple validations
        for sequence in sequences :
            if len(sequence) < min(args.lengths):
                raise Exception('Input sequence (%s) is too short.' %(sequence))
        
        return sequences