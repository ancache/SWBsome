import time
import sys
import re
from string import lstrip
from lxml import etree
from os.path import isfile

mypath = '/Users/acasa/tools/Switchboard_LDC97S62/NXT_Switchboard_Annotations_LDC2009T26/xml/'

class Timer(object):
    '''Class that can be used measure timing using system clock'''
    def __init__(self, name = None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        sys.stdout.write('-> %s [elapsed: %.2f s]\n' % (self.name, time.time() - self.tstart))

def get_trans_ix(fname):
    return re.split('\.',fname)[0]

def get_sent_word_ix(terminal_id):
    ids = re.findall('\d+',terminal_id)
    ids = [int(x) for x in ids]
    return (ids[0],ids[1])

#def get_word_ix(terminal_id):

def get_msstateID(msstateID):
    id = re.findall('\d+',msstateID)
    return re.findall('\d+',msstateID)[-1]

''' Gets the sentence id. Nite id has form sentence#_word#.
'''
def get_nite_id(element):
    idx = element.attrib['{http://nite.sourceforge.net/}id']
    idx = int(re.findall('\d+',idx)[0]) # makes it easier to get surrounding sentences
    #idx = re.findall('s\d+',idx)[0]
    
    return idx

def get_text(element):
    if element.tag == 'word':
        return ' ' + element.attrib['orth']
    elif element.tag == 'punc':
        return element.text
    else:
        return ''

def create_transcript_sentences(root, someIDs, spkrID, context):

    for element in root.iter():
        if element.tag not in ["word","punc"]:
            continue
        i = get_nite_id(element) # sentence id.
        txt = get_text(element)

        if i not in context:
            context[i] = ['---' + spkrID +':  '] + [txt]
        else:
            context[i] += [txt]

    return context

"""
@ child: a node in tree containing the search hit (e.g. a "some")
"""
def get_next_child(child):
    
    this_child_id = child.attrib['{http://nite.sourceforge.net/}id']
    this_child_sentence = re.findall('\d+',this_child_id)[0]
    next_child = child.getnext()

    # next child could be: sil (silence), punc (punctuation), trace, word. not sure if anything else. Move past silence and traces.
    while next_child.tag in ['sil','trace']:
        next_child = next_child.getnext()
        if next_child is None:
            #print 'No next child?', child.attrib['msstateID'], ':  ',  this_child_id
            #we're probably at the end of the file for some reason
            return(None, 'EOF','EOF')
  
    # The next child after "some" is not always in the same sentence. E.g. disfluency after "some", or asides: "... some, I mean,..."
    
    next_child_id = next_child.attrib['{http://nite.sourceforge.net/}id']
    next_child_sentence = re.findall('\d+',next_child_id)[0]
   
    if next_child_sentence != this_child_sentence:
        #print 'Next child not in the same sentence.', next_child.attrib['msstateID'], ':  ',  this_child_id, '---', next_child_id
        # I checked the first example like this & it's a disfluency, though not marked as such, prob. because it's followed by a brief silence and an appositive "I mean"
        return(next_child_id, 'NEW_SENT', 'NEW_SENT')
    
    # Easiest case: next child is a word
    if next_child.tag == 'word':
        return(next_child_id, next_child.attrib['orth'], next_child.attrib['pos'])
    elif next_child.tag == 'punc':
        return(next_child_id, next_child.text, 'PUNC')

    #sentence_number = 's' + re.split('\d+',terminalID)[0]
    ##print re.findall('\d+',terminalID)
    #word_number = int(re.findall('\d+',terminalID)[1]) + 1
    #next_childID = sentence_number + '_' + str(word_number)
    
    ## note: xmlns must be passed through the namespaces variable; substituting it for "nite" in the xpath query gives an 'invalid syntax' error
    #next_child = tree.xpath(".//word[@nite:id='" + next_childID + "']", namespaces={'nite':'http://nite.sourceforge.net/'})
    if next_child:
        return (next_child.attrib['pos'],next_child.text)
    else:
        return (None, None)

def get_phones(fname_prefix, msstateID):
    tree = etree.parse(mypath + 'phones/' + fname_prefix + '.phones.xml')

    # phone IDs have the shape: "ms" + ID + "A|B" + "_ph\d+", where the latter is the id of the phone inside the word denoted by ID
    msstateID += fname_prefix[-1] # to make sure we don't match a longer number
    #ph = tree.xpath(".//ph[contains(@nite:id, 'ms%s')]"%msstateID, namespaces = {'nite':'http://nite.sourceforge.net/'})
    ph = tree.xpath(".//ph[contains(@nite:id,'ms%s')]"%msstateID, namespaces = {'nite':'http://nite.sourceforge.net/'})
    phones = [p.text for p in ph]

    return phones

def get_accent(fname_prefix, pwHREF):
    fname = mypath + 'accent/' + fname_prefix + '.accents.xml'
    if not isfile(fname):
        return 'NoAnnotation'
  
    tree = etree.parse(fname)
    accent_child = tree.xpath(".//*[@href='%s']"%pwHREF)
    if not accent_child:
        return "unaccented"
    elif len(accent_child) > 1:
        return "error"
    else:
        accent_node = accent_child[0].getparent()
        accent_strength = accent_node.attrib['strength']
        if 'type' in accent_node.attrib:
            accent_type = accent_node.attrib['type']
        else:
            accent_type = "NoTypeAnnotation"
        return (accent_strength, accent_type)

    return "error"

def get_focus(fname_prefix, terminalHREF):
    k_prefix = re.split('\.', fname_prefix)[0]
    fname = mypath + 'kontrast/' + k_prefix + '.kontrast.xml'
    if not isfile(fname):
        return 'NoAnnotation'
  
    tree = etree.parse(fname)
    kontrast_child = tree.xpath(".//*[@href='%s']"%terminalHREF)
    if not kontrast_child:
        return "unfocused"
    elif len(kontrast_child) > 1:
        return "error"
    else:
        #print "HELLO"
        kontrast_node = kontrast_child[0].getparent()
        return (kontrast_node.attrib['type'], kontrast_node.attrib['level'])

    return "error"


