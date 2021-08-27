#! /usr/bin/env python3

# 20210817 - kolim - use the ts_gfci
import os
import semopy
import pandas as pd
from sklearn.preprocessing import StandardScaler
import argparse

class CausalWrap:
    
    """
    class that wraps the causal-cmd in a python wrapper
    
    """
    
    def __init__(self):
        
        # set the default arguments for causal-cmd
        self.causal_args = {
            'dataset': '',
            'algorithm': 'gfci',
            'data-type': 'continuous',
            'delimiter': 'comma',
            'score': 'sem-bic',
            'prefix': '',
            'test': 'fisher-z-test',
            'thread': '1',
            'skip-latest': True,
            'out': 'output'
            }
        
        self.args = {
            'rawdata': 'data' ,
            'causal-cmd': 'causal-cmd ',
             #'causal-cmd': 'causal-cmd_1-3 '

            }
        
        self.edges = []
        self.model = ''

        #self.set_arg({'dataset': 'sub_1001.csv'})
        #self.create_cmd()
        
        
    def set_arg(self, argval):
        """
        set the arguments 

        Parameters
        ----------
        argval : a dictionary of arg value pairs.
            .

        Returns
        -------
        None.

        """
        
        for key in argval.keys():
            # change existing arg or add an arg
            self.causal_args[key] = argval[key]

            # set the prefix based on the dataset name
            if key == 'dataset':
                prefix = self.causal_args[key].split('.csv')[0]
                self.causal_args['prefix'] = prefix
                
                
    def create_cmd(self):
        """
        create the causal-cmd using the arguments

        Returns
        -------
        0 - if OK
        1 if  problem

        """
        
        self.cmd = self.args['causal-cmd']
        
        # check to make sure that critical arguments
        # are set
        
        if (self.causal_args['dataset'] == '') or (self.causal_args['prefix'] == ''):
                # missing args
                return 1
            
        for key in self.causal_args.keys():
            
            if key == 'skip-latest':
                if self.causal_args[key] == True:
                    argstr = '--skip-latest '
            elif key == 'dataset':
                # add directory info
                argstr = '--%s %s '%(key, 
                                    os.path.join(self.args['rawdata'],
                                                 self.causal_args['dataset']))
            else:
                argstr = "--%s %s "%(key, self.causal_args[key])
                
            self.cmd += argstr
            
        
        return 0
    
    def parse_edges(self, file='output/sub_1066.txt'):
        """
        parse the  edges from the output file
        
        get edges and parse into a list of dict
        Graph Edges:
        1. drinks --> drinking dd nl
        
        {'a': 'drinks', 'etype': '-->', 'b': 'drinking', 'extra': ['dd','nl']}

        Parameters
        ----------
        file : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        self.edges = []

        # open the file
        f = open(file, 'r')
        self.lines = f.readlines()
        
        in_edge = False  # boolean for in_edge section
        
        for line in self.lines:
            if line.startswith('Graph Attributes'):
                in_edge = False  
            # print("info: ", line)
            if in_edge:  # parse the line
                segs = line.split()
                if len(segs) > 0:
                    #print(segs)
                    edge = {}
            
                    if len(segs) >= 4:
                        edge['a'] = segs[1]
                        edge['etype'] = segs[2]
                        edge['b'] =  segs[3]
                       
                    if len(segs) > 4:
                        edge['extra'] = [segs[4], segs[5]]
                    else:
                        edge['extra'] = []
                    
                    
                    self.edges.append(edge)
                
            if line.startswith('Graph Edges:'):
                in_edge = True
        
    def generate_model(self):
        # generate a model for sem in lavaan format text

        #TODO modify to accomodate different edge strings
        # eg. gfci has o-o
        # gfes has --- -->
        
        self.model = ''  # string to hold the model
        
        for edge in self.edges:
    
            # create the different edges needed
            
            if edge['etype'] == '-->':
                ops = ['~']
            elif edge['etype'] == 'o->':
                ops = ['~', '~~']
            elif edge['etype'] == 'o-o':
                ops = ['~~']
            elif edge['etype'] == '<->':  # <->
                ops = ['~~']
            else: 
                ops =[]
                
            for op in ops:
                str = '%s %s %s\n'%(edge['b'], op, edge['a'])
                self.model += str  # append to model string
                # print(edge, str)
        return self.model
    
    def run_sem(self):
        # run the sem to get the edge parameters
        sub = self.causal_args['prefix']
        #modelfile = os.path.join(self.causal_args['out'], "%s.lav"%(sub)
        # TODO write out the model file
        
        # read in the data
        datafile = os.path.join(self.args['rawdata'],
                                self.causal_args['dataset'])
        
        data = pd.read_csv(datafile)
        
        plotfile = os.path.join(self.causal_args['out'], "%s_plot.pdf"%(sub))
        edgefile = os.path.join(self.causal_args['out'], "%s_edge.json"%(sub))
        
        # fit model
        mod = semopy.Model(self.model, mimic_lavaan=False, baseline=False,
                           cov_diag=False)
        res = mod.fit(data)
        #print(res)
        
        # edges
        ins = mod.inspect()
        print(ins)
        
        # output into a json
        ins.to_json(path_or_buf=edgefile, orient='records')
        
        # plot
        g = semopy.semplot(mod, plotfile)

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

  

 
def main():
    # get the csv files from the data directory
    c = CausalWrap()
    c.set_arg({'knowledge': 'prior.txt'})

    for file in os.listdir('data'):
        if file.endswith(".csv"):
            c.set_arg({'dataset': file})
            c.create_cmd()
            print(c.cmd)
            os.system(c.cmd)
            
            # read in the output file and get the edges                
        
def main2(index=[0,None]):
    # get the csv files from the data directory
    c = CausalWrap()
    c.set_arg({'knowledge': 'prior.txt'})
    c.set_arg({'score': 'sem-bic'})
    
    # standardize data - didn't work
    #c.set_arg({'standardize': ' Yes'})
    
    
    # for gfci
    c.set_arg({'algorithm': 'gfci'})
    
    # for fges
    c.set_arg({'algorithm': 'fges'})
    c.causal_args.pop('test')
    
    # get sorted list of files in directory
    files = os.listdir("data")    
    files = list(filter(lambda f: f.endswith('.csv'), files))
    files.sort()
    
    #for file in ['sub_1001.csv']:
    for file in files[index[0]: index[1]]:

        c.set_arg({'dataset': file})
        c.create_cmd()
        print(c.cmd)
        os.system(c.cmd)
        
        # read in the output file and get the edges
        outputfile = os.path.join(c.causal_args['out'], 
                                  c.causal_args['prefix'] + '.txt')
        c.parse_edges(file=outputfile)
        #print(c.edges)
        # create model from edges
        c.generate_model()
        
        # output the model file
        modelfile = os.path.join(c.causal_args['out'], 
                                  c.causal_args['prefix'] + '.lav')
        #print(c.model)
        fp = open(modelfile, 'w')
        fp.write(c.model)
        
        # run semopy to calculate the parameters
        #c.run_sem()
            
 
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
    parser.add_argument("--list", help="TODO - list the files to be processed",
                        action = "store_true")
    
    args = parser.parse_args()
    
    # setup default values
    if args.end != None:
        args.end = int(args.end)
        
    main2(index=[args.start, args.end])