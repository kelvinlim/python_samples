
# read the data

import os
import pandas as pd

# read in ema data
print(os.getcwd())
fullpath = 'MerrillEMA_edited.csv'
df = pd.read_csv(fullpath)

# drop uneeded columns
columns_to_drop = ["sex", "studyday", "datetime", "reporttype",
                   "idtag","iddaytag","assessmentvalue",
                   "mj", "lagmj", "drinking", "lagdrinking"]
df.drop(columns_to_drop, axis=1, inplace=True)
    
# create dataframe limiting to covid for redcap_repeat_instrument 
print('totals: ', df.shape)

# get number of sessions for each ID
sessions = df['ID'].value_counts(sort=False)  # create series

# get subject ids
subjects = []
for item in sessions.items():
    subjects.append(item[0])
    
# convert series to df
dfsession = sessions.to_frame()

import sys
#sys.exit()

# create an empty dataframe to append each case to
dfall = df.copy()  # make a copy
numrows, numcols = dfall.shape
# drop all the rows
dfall = dfall.drop(dfall.index[range(numrows)])
 
# loop through subjects we want to keep
for id in subjects:
    print('subject id:', id)
    # mask to select data for a subject
    mask = df['ID'] == id
    dfsub = df.loc[mask] 
    # remove all rows with nan values
    dfsub.dropna(inplace=True)

    # append  this subject data to dfall
    dfall = dfall.append(dfsub)
    
    dfsub.drop(['ID'], axis=1, inplace=True)
    filename = 'sub_' + '%04d'%id + '.csv'
    # write out data to csv
    dfsub.to_csv(os.path.join('dataorig',filename), index=False)
    

# write out all the rows to a csv file
dfall.drop(['ID'], axis=1, inplace=True)
filename = 'allcases' + '.csv'
# write out data to csv
dfall.to_csv(os.path.join('dataorig',filename), index=False)
 


