import sys
import os
import argparse
import textwrap
import pandas as pd
from pathlib import Path


class BCRMatchArgumentParser:
    parser = argparse.ArgumentParser(
                    usage = '%(prog)s <fasta_sequence> [-a] <allele_list> [-l] <length_list>',
                    description = 'This is a command-line tool interface for BCRMatch.',
                    formatter_class=argparse.RawTextHelpFormatter)	
    
    def __init__(self):
        pass

    def parse_args(self, args):
        # Optional Arguments (Flags)
        # we need a parameter to define whether we should run training or prediction
        # prediction should be the default
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
                            nargs = '*', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = 'FASTA file containing 3 CDRHs.')
        self.parser.add_argument('--input-cdrl', '-cl', dest = 'cdrl_fasta', required = False,
                            nargs = '*', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = 'FASTA file containing 3 CDRLs.')
        self.parser.add_argument('--database', '-d', dest = 'database', required = False,
                            nargs = '+', 
                            type = str,
                            default = argparse.SUPPRESS,
                            help = 'Path to the database/json created or modified in the training.')
        self.parser.add_argument('--training-dataset-csv', '-tc',
                            dest = 'training_dataset_csv',
                            required = False,
                            help = 'Path to the CSV file that will be used for training.')
        self.parser.add_argument('--training-dataset-name', '-tn', 
                            dest = 'training_dataset_name', 
                            required = False, 
                            type = str,
                            default = argparse.SUPPRESS,
                            help = 'Name of the training dataset to use for the prediction.')
        self.parser.add_argument('--training_dataset-version', '-tv',
                            dest = 'training_dataset_version',
                            required = False,
                            type = str,
                            default = 'v1',
                            help = 'A version number of the dataset.')
        self.parser.add_argument('--training-mode', '-tm',
                            dest = 'training_mode',
                            required = False,
                            action='store_true',
                            help = 'Train the classifiers on the provided dataset.')
        self.parser.add_argument('--force', '-f',
                            dest = 'retrain_dataset',
                            required = False,
                            action='store_true',
                            help = 'Train the classifiers on the provided dataset.')
        
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
    

    def get_input_tsv_content(self, args) :
        ''' DESCRIPTION:
            This will open the TSV file and return its content.

            Return Value: List of lists
            It returns list containing each row in a list format.   
        '''
        file_name = getattr(args, 'input_tsv').name
        
        return pd.read_table(file_name).to_dict('list')
    
    def get_sequences(self, args, parser) :
        ''' DESCRIPTION:
            Reads either TSV file or list of 6 FASTA files (3 CDRLs, 3 CDRHs), and turns
            them into a dictionary in the following format:
            {
                'Seq_Name': [1, 2, 3, 4, 5], 
                'CDRL1': ['NNIGSKS', 'SQDISNY', 'ASGNIHN', 'SESVDNYGISF', 'ASQDISN'], 
                'CDRL2': ['DDS', 'YTS', 'YYT', 'AAS', 'YFT'], 
                'CDRL3': ['WDSSSDHA', 'DFTLPF', 'HFWSTPR', 'SKEVPL', 'QYSTVPW'], 
                'CDRH1': ['GFTFDDY', 'GYTFTNY', 'GFSLTGY', 'GYTFTSS', 'GYDFTHY'], 
                'CDRH2': ['SWNTGT', 'YPGNGD', 'WGDGN', 'HPNSGN', 'NTYTGE'], 
                'CDRH3': ['RSYVVAAEYYFH', 'GGSYRYDGGFD', 'RDYRLD', 'RYGSPYYFD', 'PYYYGTSHWYFD']
            }
        '''
        _NUM_FASTA_FILES = 3

        if 'input_tsv' in args:
            return self.get_input_tsv_content(args)
        

        # Check if cdrh/cdrl flags are specified.
        if 'cdrh_fasta' not in args :
            raise parser.error('Please provide FASTA files containing CDRH sequences.')
        
        if 'cdrl_fasta' not in args :
            raise parser.error('Please provide FASTA files containing CDRL sequences.')
        
        # Check if 3 fasta files are provided for each cdrh and cdrl flags.
        if len(getattr(args, 'cdrh_fasta')) != _NUM_FASTA_FILES :
            raise parser.error('Please provide 3 CDRH fasta files.')

        if len(getattr(args, 'cdrl_fasta')) != _NUM_FASTA_FILES :
            raise parser.error('Please provide 3 CDRL fasta files.')

        if 'cdrh_fasta' in args and 'cdrl_fasta' in args :
            # NOTE: Is it safe to assume that the user will provide exact number of sequences for all?
            cdrh_files = getattr(args, 'cdrh_fasta')
            cdrl_files = getattr(args, 'cdrl_fasta')
            sequence_names = []
            sequence_series = []

            for i in range(_NUM_FASTA_FILES):
                _INDEX = i + 1
                cdrh_file = cdrh_files[i].name
                cdrl_file = cdrl_files[i].name

                with open(cdrh_file, 'r') as f:
                    cdrh_fcontent = [_.strip().replace('>','') for _ in f.readlines()]
                
                with open(cdrl_file, 'r') as f:
                    cdrl_fcontent = [_.strip().replace('>','') for _ in f.readlines()]

                # Retrieve sequence names (only have to perform once)
                if not sequence_names:
                    for i in range(len(cdrl_fcontent)):
                        if i%2 == 0 :
                            sequence_names.append(cdrl_fcontent[i])
                
                    sequence_series.append( pd.DataFrame({'Seq_Name': sequence_names}) )

                # Collect sequences into Series
                cdrl_col = []
                cdrh_col = []
                for i in range(len(cdrl_fcontent)):
                    if i%2:
                        cdrl_col.append(cdrl_fcontent[i])
                        cdrh_col.append(cdrh_fcontent[i])
                
                sequence_series.append( pd.DataFrame({'CDRL%s' %(_INDEX): cdrl_col}) )
                sequence_series.append( pd.DataFrame({'CDRH%s' %(_INDEX): cdrh_col}) )


            seq_df = pd.concat(sequence_series, axis=1)

            return seq_df.to_dict('list')

        return {} 



    def prepare_training_mode(self, args):
        # For training mode, user must provide the following:
        #   * training-dataset-csv
        #   * training-dataset-name
        #   * training-dataset-version
        # After that, I would need to create database for dataset.
        if not getattr(args, 'training_dataset_csv'):
            raise KeyError('Please provide path to the training dataset csv file.')
        
        # if not getattr(args, 'training_dataset_name'):
        #     raise KeyError('Please provide name for the training dataset.')
        
        if not getattr(args, 'training_dataset_version'):
            raise KeyError('Please provide dataset version.')
        

        training_dataset_file_path = getattr(args, 'training_dataset_csv')
        training_dataset_name = os.path.basename(training_dataset_file_path)
        training_dataset_name = os.path.splitext(training_dataset_name)[0]
        training_dataset_version = getattr(args, 'training_dataset_version')
        print('--------')
        print('training-dataset-csv: %s' %(training_dataset_file_path))
        print('training-dataset-name: %s' %(training_dataset_name))
        print('training-dataset-version: %s' %(training_dataset_version))

        dataset_db_header = [
            'dataset_name',
            'model',
            'dataset',
            'pickle_file',
            'dataset_version'
        ]


        # Check existence of dataset db
        database_path = Path('dataset-db')
        models = ['rf', 'gnb', 'log_reg', 'xgb', 'ffnn']

        if database_path.is_file():
            # Check if the user provided entry already exists in the database
            df = pd.read_csv('dataset-db', sep='\t')

            # Only need to check dataset name and dataset version to check for existence
            filtered_df = df[(df['dataset_name']==training_dataset_name) & ((df['dataset_version']==training_dataset_version))]

            if 0 < len(filtered_df):
                # If force flag is set, retrain
                if getattr(args, 'retrain_dataset'):
                    print('force retrain...')

                else:
                    raise Exception('All models have already been train under the %s (%s) dataset.' %(training_dataset_name, training_dataset_version))
            
            # entry doesn't exists, thus add to db
            print("Need to create more entry")
            # Create 5 dataset entry for all 5 models
            data = []
            for model in models:
                pickle_file_path = '%s/%s/%s_%s.pkl' %(training_dataset_name, training_dataset_version, model, training_dataset_name)
                data.append([training_dataset_name, model, training_dataset_file_path, pickle_file_path, training_dataset_version])
            
            additional_df = pd.DataFrame(data, columns=dataset_db_header)

            # Append the data to the existing db
            updated_df = pd.concat([df, additional_df])
            
            print('updating the database!')
            updated_df.to_csv('dataset-db', sep='\t', index=False)

        else:
            # Create 5 dataset entry for all 5 models
            data = []
            for model in models:
                pickle_file_path = '%s/%s/%s_%s.pkl' %(training_dataset_name, training_dataset_version, model, training_dataset_name)
                data.append([training_dataset_name, model, training_dataset_file_path, pickle_file_path, training_dataset_version])
            
            df = pd.DataFrame(data, columns=dataset_db_header)

            # create dataset db
            df.to_csv('dataset-db', sep='\t', index=False)

        
