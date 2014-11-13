import cPickle as pickle
import nltk

from utils import *

def bigram(somes):
    pass

def annotation_report(somes):
    pass

def prune_dataset(somes):
    print '---> Initial dataset: %s tokens.'%len(somes)

    # exclude those without enough context or no MS alignment
    somes2 = [s for s in somes if 'LC' in s and 'RC' in s]
    print '---> Exclude tokens with not enough context or no MS alignment. %s tokens left.'%len(somes2)

    # choose nonunique bigrams
    next_word = [hit['nextWord'] for hit in somes2]
    fdist = nltk.FreqDist(next_word)
    somes2 = [hit for hit in somes2 if fdist[hit['nextWord']] > 1]
    print '---> Choose nonunique bigrams. %s tokens left.'%len(somes2)

    # exclude disfluencies
    exclude = ['some','uh','um']
    somes2 = [hit for hit in somes2 if hit['nextWord'] not in exclude]
    print '---> Exclude disfluencies. %s tokens left.'%len(somes2)
    
    # exclude those with bad audio or alignment
    # (TODO)

    return somes2
                      

def main():
    f = open('swbsomes.pkl','r')
    somes = pickle.load(f)
    f = open('swbtranscripts.pkl','r')
    trans = pickle.load(f)
    f.close()

    somes2 = prune_dataset(somes)

    Fsome = open('swbsomesEZRA.pkl','wb')
    pickle.dump(somes2,Fsome)
    Fsome.close()

    mp3url = 'http://www.fakeurl.org/'

    for some in somes2:
        fname = re.split('\.',some['swbfile'])[0]
        fname = re.sub('sw','sw0',fname) + some['terminalID'] + '.param'
        f = open(fname, 'wb')
        f.write('MP3\t' + mp3url + str(some['ezraID']) + '.mp3\n')
        f.write('SEEK\t' + str(int(float(some['start']))) + '\n')

        some['LC'] = re.sub('\\n','\\\\n',some['LC'])
        some['RC'] = re.sub('\\n','\\\\n',some['RC'])
        f.write('LEFTCONTEXT\t' + some['LC'] + '\n')
        f.write('RIGHTCONTEXT\t' + some['RC'] + '\n')
        f.write('WINDOWOFFSET\t' + str(int(float(some['start']) - float(some['LC_startTime']))) + '\n')
        f.write('WINDOWDURATION\t' + str(int(float(some['RC_endTime']) - float(some['LC_startTime']))))
        f.close()

if __name__ == "__main__":
    main()
