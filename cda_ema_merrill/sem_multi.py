#! /usr/bin/env python

import semopy 
import pandas as pd
import os
import pathlib
import argparse
import datetime

class Sem:
    
    def __init__(self, noplot=False):
        self.noplot_flag = noplot  #  set plot flag
        
    def run_sem(self, prefix):  
        modelfile = os.path.join('output', prefix + '.lav')
        plotfile_png = os.path.join('pngs', prefix + '.png')
        plotfile_pdf = os.path.join('pdfs', prefix + '.pdf')
        
        fp = open(modelfile, 'r')
        desc = fp.read()
        
        # read in data
        datafile = os.path.join('data', prefix + '.csv')
        data = pd.read_csv(datafile)
        model = semopy.Model(desc)
        opt_res = model.fit(data)
        estimates = model.inspect()
        
        if not self.noplot_flag:
            g = semopy.semplot(model, plotfile_png)
            g = semopy.semplot(model, plotfile_pdf)

        # write out estimates
        estimates.to_csv('output/'+ prefix +'_semopy.csv',index=False)
        estimates.to_json(path_or_buf='output/'+prefix + '_semopy.json', orient='records')
        
def main(index=[0,None], noplot=False):
    c = Sem(noplot=noplot)

    files = os.listdir("data")    
    files = list(filter(lambda f: f.endswith('.csv'), files))
    files.sort()
    
    #for file in ['sub_1001.csv']:
    for file in files[index[0]:index[1]]:
        # run semopy to calculate the parameters
        now = datetime.datetime.now()
        print ('start:', now.strftime("%Y-%m-%d %H:%M:%S"))

        prefix = pathlib.Path(file).stem
        print(prefix)
        c.run_sem(prefix)
        now = datetime.datetime.now()
        print ('finish:', now.strftime("%Y-%m-%d %H:%M:%S"))
            
 
if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description = "Does the sem estimates for the lavaan model. \
            The semopy package is used."
    )
    parser.add_argument("--start", type = int,
                        help="beginning file list index , default 0",
                        default = 0)
    parser.add_argument("--end", type = str,
                        help="end file list index, default None",
                        default=None)
    parser.add_argument("--list", help="TODO list the files to be processed",
                        action = "store_true")
    parser.add_argument("--noplot", help="do not create the plot files, \
        default is to create the plot files",
        action = "store_true", default = False)
    args = parser.parse_args()

    # setup default values
    if args.end != None:
        args.end = int(args.end)
    main( index = [args.start, args.end], noplot=args.noplot)
        
