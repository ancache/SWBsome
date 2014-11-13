import cPickle as pickle
import nltk

def bigram(somes):
    nxt_word = [hit['nextWord'] for hit in somes]
    nxt_POS = [hit['nextPOS'] for hit in somes]

    fdist_word = nltk.FreqDist(nxt_word)
    # print(fdist_word)
    fdist_word.plot(50) # plots first 50
    
    fdist_POS = nltk.FreqDist(nxt_POS)
    # print(fdist_word)
    fdist_POS.plot(50) # plots first 50    

def annotation_report(somes):
    accents = [hit['accent'] for hit in somes]
    focus = [hit['focus'] for hit in somes]

    fdist_accents = nltk.FreqDist(accents)
    print(fdist_accents)
    #fdist_accents.tabulate()

    fdist_focus = nltk.FreqDist(focus)
    print(fdist_focus)
    #fdist_focus.tabulate()


def main():
    f = open('swbsomes.pkl','r')
    somes = pickle.load(f)
    #f = open('swbtranscripts.pkl','r')
    #trans = pickle
    f.close()

    bigram(somes)
    annotation_report(somes)

    

if __name__ == "__main__":
    main()
