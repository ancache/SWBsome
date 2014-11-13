
from lxml import etree
import cPickle as pickle
from os import listdir
from os.path import isfile
import re

from utils import *

hits = []
transcripts = {}

mypath = '/Users/acasa/tools/Switchboard_LDC97S62/NXT_Switchboard_Annotations_LDC2009T26/xml/'
namespace = 'http://nite.sourceforge.net/'
namespaceCB = "{%s}"%namespace

""" 
@ tree : an lxml etree
@ fname_prefix : string. for example, sw2005.A
"""
def swb_query(tree, fname_prefix):
    children = tree.xpath(".//word[(@orth='some' or @orth='Some') and @pos='DT']")
    new_hits = []
  
  # if no some's, don't do any of the following
    if not children:
        return []

    for child in children:
        D = {}
        D['swbfile'] = fname_prefix
        D['terminalID'] = child.attrib[namespaceCB+'id']
        D['start'] = child.attrib[namespaceCB+'start']
        D['end'] = child.attrib[namespaceCB+'end']

        (nextID, nextWord, nextWordPOS) = get_next_child(child)
        D['nextID'] = nextID
        D['nextWord'] = nextWord
        D['nextPOS'] = nextWordPOS

        msid = child.attrib['msstateID']
        if D['end'] == "n/a" or msid == "non-aligned":
            D['phones'] = None
        else:
            D['phones'] = get_phones(fname_prefix, get_msstateID(msid))
            #if ''.join(D['phones']) != 'sahm':
                #print 'Transcript error! Exclude ', D['swbfile'], get_msstateID(msid), D['phones']
                #return new_hits

        # accent annotations have pointer to prosodic word
        # in terminals.xml, pointer to prosodic word ID is in a child of this current child, under attribute "href"
        # list(node) gives the child of that node
        if child.attrib['msstate'] == "non-aligned":
            D['accent'] = "NoMsAlignment"
        else:
            pwHREF = list(child)[0].attrib['href']
            D['accent'] = get_accent(fname_prefix, pwHREF)

        # kontrast annotations have pointer to terminal
        # reconstruct the pointer in proper format:
        terminalHREF = fname_prefix + '.terminals.xml#id(%s)'% D['terminalID']
        #print terminalHREF
        D['focus'] = get_focus(fname_prefix, terminalHREF)

        new_hits.append(D)
  
    return new_hits

def swb_context(treeA, treeB, someIDs):
    rootA = treeA.getroot()
    rootB = treeB.getroot()

    context = {}
    context = create_transcript_sentences(rootA,someIDs,'A',context)
    context = create_transcript_sentences(rootB,someIDs,'B',context)

    return context

def ezra_context(some, trans, treeA, treeB):
    
    # if no start/end time for 'some', don't bother
    if not re.match('\d+',some['start']) or not re.match('\d+',some['end']):
        return some
    
    #### LEFT CONTEXT
    # left context has 30sec offset from hit
    lc_start_timestamp = int(float(some['start'])) - 30
    found = 0 
    while found == 0 and lc_start_timestamp >= 0:
        # find a word at 30sec offset in spkr A's transcript
        lc_start_node = treeA.xpath(".//word[starts-with(@nite:start,'%s.')]"%lc_start_timestamp, namespaces = {'nite':'http://nite.sourceforge.net/'})
        # if not found, try to find such a word in spkr B's transcript
        if not lc_start_node:
            lc_start_node = treeB.xpath(".//word[starts-with(@nite:start,'%s.')]"%lc_start_timestamp, namespaces = {'nite':'http://nite.sourceforge.net/'})
        # if still no word found, try again with a slightly higher offset
        if not lc_start_node:
            lc_start_timestamp -= 1
            continue
        else:
            found = 1
    
    if found:
        some['LC_startID'] = lc_start_node[0].attrib['{http://nite.sourceforge.net/}id']  
        some['LC_startTime'] = lc_start_node[0].attrib['{http://nite.sourceforge.net/}start'] 
        (lc_sid, lc_wid) = get_sent_word_ix(some['LC_startID'])
        (sid, wid) = get_sent_word_ix(some['terminalID'])
        
        # add ellipsis
        LC = "[...]\n" + trans[lc_sid][0]
        if lc_wid != 1:
            LC += "[...] "

        prev_spkr_id = trans[lc_sid][0]
        while lc_sid < sid:
            # some sentences are missing from transcript b/c they're made up entirely of silence
            if lc_sid not in trans:
                lc_sid += 1
                continue
            sent = trans[lc_sid]
            # consolidate sentences from same speaker
            if sent[0] == prev_spkr_id:
                LC += " ".join(sent[lc_wid:len(sent)])
            else:
                LC += "\n" + " ".join(sent[0:len(sent)])
            prev_spkr_id = sent[0]
            lc_sid += 1; lc_wid = 1
                        
        sent = trans[sid]
        if sent[0] == prev_spkr_id:
            LC += " ".join(sent[lc_wid:wid]) + " >>>"
        else:
            LC += "\n" + " ".join(sent[0:wid]) + " >>>"
            
        some['LC'] = LC

    ### RIGHT CONTEXT
    # right context ends at 15sec offset from hit
    rc_end_timestamp = int(float(some['end'])) + 15
    found = 0 
    while found == 0 and rc_end_timestamp <= int(float(some['end'])) + 20:
        # find a word at 30sec offset in spkr A's transcript
        rc_end_node = treeA.xpath(".//word[starts-with(@nite:end,'%s.')]"%rc_end_timestamp, namespaces = {'nite':'http://nite.sourceforge.net/'})
        # if not found, try to find such a word in spkr B's transcript
        if not rc_end_node:
            rc_end_node = treeB.xpath(".//word[starts-with(@nite:end,'%s.')]"%rc_end_timestamp, namespaces = {'nite':'http://nite.sourceforge.net/'})
        # if still no word found, try again with a slightly higher offset
        if not rc_end_node:
            rc_end_timestamp += 1
            continue
        else:
            found = 1
    
    if found:
        some['RC_endID'] = rc_end_node[0].attrib['{http://nite.sourceforge.net/}id']  
        some['RC_endTime'] = rc_end_node[0].attrib['{http://nite.sourceforge.net/}end'] 
        (rc_sid, rc_wid) = get_sent_word_ix(some['RC_endID'])
        (sid, wid) = get_sent_word_ix(some['terminalID'])
        sent = trans[sid]
        prev_spkr_id = sent[0]
        
        RC = " <<< " + " ".join(sent[wid+1:len(sent)])
        
        sid += 1
        while sid < rc_sid:
            # some sentences are missing from transcript b/c they're made up entirely of silence
            if sid not in trans:
                sid += 1
                continue
            sent = trans[sid]
            # consolidate sentences from same speaker
            if sent[0] == prev_spkr_id:
                RC += " ".join(sent[1:len(sent)])
            else:
                RC += "\n" + " ".join(sent[0:len(sent)])
            prev_spkr_id = sent[0]
            sid += 1
                        
        sent = trans[rc_sid]
        if sent[0] == prev_spkr_id:
            RC += " ".join(sent[1:rc_wid]) + " [...]"
        else:
            RC += "\n" + " ".join(sent[0:rc_wid]) + " [...]"
            
        some['RC'] = RC
        

    return some

def main():
    hits = []
    mypath2 = mypath + 'terminals/'
          
    files = []
    for f in listdir(mypath2):
        if isfile(mypath2 + f):
            f_prefix = re.split('\.',f)[0]
            if f_prefix not in files:
                files.append(f_prefix)
 
    for f in files:
        fnameA = f + '.A.terminals.xml'
        fnameB = f + '.B.terminals.xml'

        treeA = etree.parse(mypath2 + fnameA)
        treeB = etree.parse(mypath2 + fnameB)

        foundA = swb_query(treeA, re.split('.terminals.xml',fnameA)[0])
        foundB = swb_query(treeB, re.split('.terminals.xml',fnameB)[0])
        found = foundA + foundB
       
        if found:
            someIDs = [D['terminalID'] for D in found]
            transcripts[f] = swb_context(treeA, treeB, someIDs)
  
            # get left context
            trans = transcripts[f]
            for i in range(0,len(found)):
                found[i] = ezra_context(found[i], trans, treeA, treeB)
     
            hits = hits + found
   
 # Assign ezra IDs
    for i in range(len(hits)):
        hits[i]['ezraID'] = i

    
    
    # pickle
    with Timer('Made pickles: '):
        Fsome = open('swbsomes.pkl', 'wb')
        Ftrans = open('swbtranscripts.pkl','wb')
        pickle.dump(hits, Fsome)
        pickle.dump(transcripts, Ftrans)
        Fsome.close()
        Ftrans.close()

    print '-----> Found ', len(hits), ' hit terms.'
    


if __name__ == "__main__":
    main()
