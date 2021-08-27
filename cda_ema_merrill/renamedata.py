#! /usr/bin/env python
# read the data

import os
import pandas as pd
import glob
import argparse
from sklearn.preprocessing import StandardScaler

class RenameData:
    
    """
    class to rename columns of dataframes to be compatble with R
    
    """
    
    def __init__(self, drop_columns='R_', index=[0,None], nostd=False):
        
        
        self.args = {
            'dataorig': 'dataorig' ,
            'datanew': 'data',
            }
        
        #self.testfile = "dataorig/sub-10014_ses-54531_task-rest_acq-eyesclosedPA_run-01_glasser19vol.ptseries.csv"
    
        #self.read_file(self.testfile)
        
        #print(self.testfile)

        self.no_std = nostd        
        self.work(drop_columns=drop_columns, index=index)
        
    
    
    def read_file(self, filepath):
        # read in the data file into a dataframe
        self.dforig = pd.read_csv(filepath)
        
        # get column names
        
        #df.rename(columns=colrenames, inplace=True)
        
 
    def rename_columns(self, df):
        
        # create a dict for renaming 
        
        renames = {}
        
        for colname in df.columns:
            if '-' in colname:  # check if invalid character is present
                renames[colname] = colname.replace('-', '.', 10)
            
        
        newdf = df.rename(columns=renames)

        return newdf
    
    
    def drop_columns(self, str='R_'):
        # remove columns beginning with the argument str
        for col in self.newdf.columns:
            	if col.startswith(str):
            		del self.newdf[col]
                    
    def drop_columns_percent(self, percent):
        # remove columns based on percent
        cols = self.newdf.columns
        # calculate number of columns to keep, inverse of drop
        proportion = (100.0 - percent)/100.0
        numcols = int(len(cols) * proportion)
        
        for item in range(numcols):
            del self.newdf[cols[item]]
        
    def standardize_df_col(self, diag=False):
        """
        standardize the columns in the dataframe
        https://machinelearningmastery.com/normalize-standardize-machine-learning-data-weka/
        
        * get the column names for the dataframe
        * convert the dataframe into into just a numeric array
        * scale the data
        * convert array back to a df
        * add back the column names
        * set to the previous df
        """
        
        # describe original data - first two columns
        if diag:
            print(self.newdf.iloc[:,0:2].describe())
        # get column names
        colnames = self.newdf.columns
        # convert dataframe to array
        data = self.newdf.values
        # standardize the data
        data = StandardScaler().fit_transform(data)
        # convert array back to df, use original colnames
        self.newdf = pd.DataFrame(data, columns = colnames)
        # describe new data - first two columns
        if diag:
            print(self.newdf.iloc[:,0:2].describe())

        
        
        
        
    def work(self, drop_columns='R_', index=[0,None]):
        # get the csv files from the data directory
    
        self.files = glob.glob(os.path.join(self.args['dataorig'], "*.csv"))
        self.files.sort()
        
        for file in self.files[index[0]:index[1]]:
            print(file)
            # read in the data
            dforig = pd.read_csv(file)
            
            # rename columns
            self.newdf = self.rename_columns(dforig)
            
            # drop columns
            if drop_columns == '':
                pass  # do nothing
            elif drop_columns.isnumeric():
                self.drop_columns_percent(int(drop_columns))
            elif type(drop_columns) == str:
                # string is provided
                self.drop_columns(str=drop_columns)

            # standardize ?
            if not self.no_std:
                self.standardize_df_col(diag=True)
                
            newfilepath = os.path.join(self.args['datanew'], 
                                       os.path.basename(file))
            self.newdf.to_csv(newfilepath, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="rename columns in csv files making them R compatible"
    )
    parser.add_argument("--start", type = int,
                        help="beginning file list index , default 0",
                        default = 0)
    parser.add_argument("--end", type = str,
                        help="end file list index, default None",
                        default=None)
    parser.add_argument("--drop", type = str,
                        help="columns to drop, 'R_' would drop \
                            columns beginning with those characters, \
                            default is no columns are dropped",
                        default='')
    parser.add_argument("--nostd", help="do not standardize the columns",
                     action = "store_true")
    parser.add_argument("--list", help="TODO - list the files to be processed",
                        action = "store_true")

    args = parser.parse_args()

    # setup default values
    if args.end != None:
        args.end = int(args.end)
 
    #c = RenameData(drop_columns='90') # to drop 90%
    #c = RenameData(drop_columns='') # keep all columns; do all files
    c = RenameData(drop_columns=args.drop, 
                    index=[args.start,args.end], nostd=args.nostd)



