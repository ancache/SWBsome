from __future__ import print_function
import cPickle as pickle
from os import listdir
import re
import glob

def main():
    f = open('swbsomesEZRA.pkl','r')
    somes = pickle.load(f)
    f.close()
    
    out = open('sph_files.txt','wb')

    some_files = [(s['swbfile'],s['terminalID']) for s in somes]
    some_files = [(re.split('\.',f)[0],tid) for (f,tid) in some_files]
    some_files = [(re.sub('sw','sw0',f),tid) for (f,tid) in some_files]

    for (f,tid) in some_files:
        print(f + "\t" + tid,file=out)
    out.close()

if __name__ == "__main__":
    main()
