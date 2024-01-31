import argparse
import textwrap
import pandas as pd
import os
import re


class BCRMatchArgumentParser:
    parser = argparse.ArgumentParser(
                    usage = '%(prog)s [-i] <input_tsv> [-tc] <training_dataset_csv>',
                    description = 'This is a command-line tool interface for BCRMatch.',
                    formatter_class=argparse.RawTextHelpFormatter)	
    
    MODELS = ['rf', 'gnb', 'log_reg', 'xgb', 'ffnn']

    _training_mode = ''
    _training_dataset = ''
    _training_dataset_name = ''
    _training_dataset_version = ''
    _dataset_db = ''
    _models_dir = ''
    _force_retrain_flag = False
    _list_datasets_flag = False

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
                            help = textwrap.dedent('''\
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
        self.parser.add_argument('--input-cdrh', '-ch', 
                            dest = 'cdrh_fasta', 
                            required = False,
                            nargs = '*', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = 'FASTA file containing 3 CDRHs.')
        self.parser.add_argument('--input-cdrl', '-cl', 
                            dest = 'cdrl_fasta', 
                            required = False,
                            nargs = '*', 
                            type = argparse.FileType('r'),
                            default = argparse.SUPPRESS,
                            help = 'FASTA file containing 3 CDRLs.')
        self.parser.add_argument('--database', '-db', 
                            dest = 'database', 
                            required = False,
                            type = str,
                            default = 'models/dataset-db',
                            help = textwrap.dedent('''\
                            Path to the database/json created or modified in the training.
                            (The 'dataset-db' in the code directory will be used as the default database.)
                            '''))
        self.parser.add_argument('--models-dir', '-md', 
                            dest = 'models_dir', 
                            required = False,
                            type = str,
                            default = 'models/models/',
                            help = textwrap.dedent('''\
                            Path to the directory that contains all the pickled models.
                            '''))
        self.parser.add_argument('--training-dataset-csv', '-tc',
                            dest = 'training_dataset_csv',
                            required = False,
                            help = 'Path to the CSV file that will be used for training.')
        self.parser.add_argument('--training-dataset-name', '-tn', 
                            dest = 'training_dataset_name', 
                            required = False, 
                            type = str,
                            default = argparse.SUPPRESS,
                            help = textwrap.dedent('''\
                            Rename the training dataset CSV to be stored in the database.
                            This will be used to lookup dataset in the database during prediction.
                            '''))
        self.parser.add_argument('--training_dataset-version', '-tv',
                            dest = 'training_dataset_version',
                            required = False,
                            type = int,
                            default = '20240125',
                            help = 'A version number of the dataset.')
        self.parser.add_argument('--training-mode', '-tm',
                            dest = 'training_mode',
                            required = False,
                            action='store_true',
                            help = 'Train the classifiers on the provided dataset.')
        self.parser.add_argument('--force-training', '-f',
                            dest = 'retrain_dataset',
                            required = False,
                            action='store_true',
                            help = 'Force training if the same dataset name and version exist.')
        self.parser.add_argument('--list-datasets', '-l',
                            dest = 'list_datasets',
                            required = False,
                            action='store_true',
                            help = 'Displays all unique dataset/version.')
        self.parser.add_argument('--output', '-o', 
                            dest = 'output', 
                            required = False,
                            nargs = '?', 
                            type = argparse.FileType('w'),
                            action='store',
                            default = argparse.SUPPRESS,
                            help = textwrap.dedent('''\
                            Path to the output file.
                            (The default output file is 'output.csv'.)
                            '''))

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


    # Getters
    def get_training_mode(self):
        return self._training_mode

    def get_training_dataset(self):
        return self._training_dataset
    
    def get_training_dataset_name(self):
        return self._training_dataset_name
    
    # def get_training_dataset_name(self, args):
    #     training_dataset_file_path = self.get_training_dataset(args)
    #     training_dataset_name = os.path.basename(training_dataset_file_path)
    #     training_dataset_name = os.path.splitext(training_dataset_name)[0]
    #     return training_dataset_name
    
    def get_training_dataset_version(self):
        return self._training_dataset_version
    
    def get_force_retrain_flag(self):
        return self._force_retrain_flag

    def get_list_datasets_flag(self):
        return self._list_datasets_flag

    def get_database(self):
        return self._dataset_db

    def get_models_dir(self):
        return self._models_dir

    # Setters 
    def set_training_mode(self, args):
        training_mode = getattr(args, 'training_mode')
        self._training_mode = training_mode

    def set_training_dataset(self, args):
        training_dataset = getattr(args, 'training_dataset_csv')
        self._training_dataset = training_dataset
    
    def set_training_dataset_name(self, args):
        try: 
            training_dataset_name = getattr(args, 'training_dataset_name')
            self._training_dataset_name = training_dataset_name
        except:
            # Set the CSV file name as the default for the training_dataset_name
            training_dataset_file = self.get_training_dataset()
            training_dataset_name = os.path.basename(training_dataset_file)
            self._training_dataset_name = os.path.splitext(training_dataset_name)[0]

    def set_training_dataset_version(self, args):
        # version needs to be in a date format (YYYYMMDD)
        training_dataset_version = getattr(args, 'training_dataset_version')

        # pattern = re.compile(r'\d{4}\d{2}\d{2}')

        # if not pattern.match(training_dataset_version):
        #     raise ValueError(f'The dataset version needs to be in a date format(YYYYMMDD).\
        #                       \nPlease correct the version({training_dataset_version}) to date format.')

        self._training_dataset_version = training_dataset_version

    def set_force_retrain_flag(self, args):
        force_flag = getattr(args, 'retrain_dataset')
        self._force_retrain_flag = force_flag

    def set_list_datasets(self, args):
        list_datasets_flag = getattr(args, 'list_datasets')
        self._list_datasets_flag = list_datasets_flag

    def set_database(self, args):
        db_path = getattr(args, 'database')
        self._dataset_db = db_path

    def set_models_dir(self, args):
        models_dir = getattr(args, 'models_dir')
        if models_dir[::-1] != '/':
            models_dir = models_dir + '/'
            
        self._models_dir = models_dir
        

    def validate(self, args):
        for arg in vars(args):
            if arg == 'training_dataset_csv':
                self.set_training_dataset(args)

            if arg == 'training_dataset_version':
                self.set_training_dataset_version(args)

            if arg == 'training_mode':
                self.set_training_mode(args)

            if arg == 'retrain_dataset':
                self.set_force_retrain_flag(args)

            if arg == 'list_datasets':
                self.set_list_datasets(args)

            if arg == 'database':
                self.set_database(args)
            
            if arg == 'models_dir':
                self.set_models_dir(args)

        # This flag needs to be set always.
        self.set_training_dataset_name(args)
