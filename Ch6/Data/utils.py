import pandas as pd
import numpy as np

def get_data(filename):
    df = pd.read_csv(filename,delim_whitespace=True,names=['word','label'])
    beg_indices = list(df[df['word'] == 'BOS'].index)+[df.shape[0]]
    sents,labels,intents = [],[],[]
    for i in range(len(beg_indices[:-1])):
        sents.append(df[beg_indices[i]+1:beg_indices[i+1]-1]['word'].values)
        labels.append(df[beg_indices[i]+1:beg_indices[i+1]-1]['label'].values)
        intents.append(df.loc[beg_indices[i+1]-1]['label'])    
    return np.array(sents),np.array(labels),np.array(intents)

def get_data2(filename):
    with open(filename) as f:
        contents = f.read()
    sents,labels,intents = [],[],[]
    for line in contents.strip().split('\n'):
        words,labs = [i.split(' ') for i in line.split('\t')]
        sents.append(words[1:-1])
        labels.append(labs[1:-1])
        intents.append(labs[-1])
    return np.array(sents),np.array(labels),np.array(intents)

read_method = {'data2/atis-2.dev.w-intent.iob':get_data,
               'data2/atis.train.w-intent.iob':get_data2,
               'data2/atis.test.w-intent.iob':get_data,
              'data2/atis-2.train.w-intent.iob':get_data2}

def fetch_data(fname):
    func = read_method[fname]
    return func(fname)
