from __future__ import print_function
import cPickle as pickle
from os import listdir
import re
import glob

######
# Creates tab-separated txt files for processing sph files:
#     hits_start_end.txt for replacing hits with noise
#     sph_files.txt for converting wavs to mp3s, 1 per hit
######

def main():
    f = open('swbsomesEZRA.pkl','r')
    somes = pickle.load(f)
    f.close()
    
    out1 = open('hits_start_end.txt','wb')
    startend = {}; offset = 0.5
    # offset = how much around the hit should we replace with noise
    # should be dynamically updated below when hits are too close together
    out2 = open('sph_files.txt','wb')
    
    for s in somes:
        fname = s['swbfile']
        fname = re.split('\.',fname)[0]
        fname = re.sub('sw','sw0',fname)
        s['swbfile'] = fname
        
        soff = float(s['start']) - offset
        eoff = float(s['end']) + offset
      
        se = (soff,eoff)
        if fname in startend:
            startend[fname] += [se]
        else:
            startend[fname] = [se]

    for f in startend:
        times = sorted(startend[f])
   
        i = 1; limit = len(times)
        while i < limit:
            if times[i][0] - times[i-1][1] < 0.05:
                #print("Entered while loop for f = " + f)
                #print(times)
                if i >= 2:
                    times2 = times[:i-1] + [(times[i-1][0],times[i][1])] + times[i+1:]
                else:
                    times2 = [(times[i-1][0],times[i][1])] + times[i+1:]
                times = times2
                #print(times)
                limit = len(times)
                i = 1
                
            else:
                i += 1

        times = [str(soff) + '\t' + str(eoff) for (soff,eoff) in times]
        print(f + '\t' + '\t'.join(times), file=out1)

    out1.close()

    some_files = [(s['swbfile'],s['terminalID']) for s in somes]
    for (f,tid) in some_files:
        print(f + "\t" + tid,file=out2)
    out2.close()

if __name__ == "__main__":
    main()
