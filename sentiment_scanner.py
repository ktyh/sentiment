# -*- coding: utf8 -*-
"""
This performs a sentiment scan on tha available repository
Insted of raw metrics on availability of positive/negative
rich words in general, finds clusters of some threshold
where spacing within individual words is given as
a heuristic
"""
from path import path
import string
import sys

class ConfHolder(object):
    """
    All conf in one place
    Create object and pass it to functions
    """
    def __init__(self, 
            threshold, 
            hthresh,
            fpath,
            cpath):
        self.threshold = threshold
        self.hthresh = hthresh
        self.fpath = fpath
        self.cpath = cpath
        self.lexicon = {}
        self.load_lexicon()

    def print_conf(self):
        """
        Necessary for experiments
        """
        print '+'*30
        print self.threshold
        print self.hthresh
        print self.fpath
        print '+'*30

    def load_lexicon(self):
        """
        Loads and preprocesses the lexicon
        """
        lines = [l.strip() for l in open(self.fpath).readlines()]


        for line in lines:
            try:
                elx, ely = line.split(';')
                elx = elx.strip()
                ely = float(ely.strip().replace(',', '.'))
                self.lexicon[elx] = ely
            except:
                #will omit only lines where somehowe there
                #are more than one separators
                pass





def check_bag(bag, cnf):
    """
    bag - list of ints
    cnf - object containing cnf minimal bag size and gap
    returns valid bags or None

    Checks whether given bag contains 
    enough elements of desired sort.
    """

    if len(bag) < 1:
        return None


    #algorithm works as follows
    #checking each subsequent elements whether
    #they are apart within HTHRESH interval
    #if true, current outbag gets another element
    #else it is checked whether its size is over threshold
    #if true, it is added to the bag of valid bags

    bag.reverse() 
    outbags = []


    outbag = [bag[0]]


    for i, ele in enumerate(bag):
        if i < len(bag) - 2:
            if ele - bag[i + 1] < cnf.hthresh:
                outbag.append(bag[i + 1])
            else:
                if len(outbag) >= cnf.threshold:
                    outbags.append(outbag)
                outbag = [ele]

    if len(outbag) >= cnf.threshold:
        outbags.append(outbag)

    if len(outbags) >= 1:
        return outbags
    return None

def describe_bag(inbag, content, cnf):
    """
    Takes a bag of bags and original content
    provides a description
    """
    for lbag in inbag:
        print ' '.join([content[ele] for ele in lbag])
        print sum([cnf.lexicon[content[ele]] for ele in lbag]) / len(lbag)

def cruch_corpus(cnf):
    """
    Loads corpus, file by file checks
    cnf cstorres cnf data
    whethere there are some negative or positive clusters.
    """
    gl_pos_cnt = 0
    gl_neg_cnt = 0

    #goes with local dir and local fiel path
    ldir = path(cnf.cpath)
    for lfp in ldir.files('*.html'):
        with open(lfp) as lfile:
            #get only words with no punctuation
            #for multiple runs with different thresholds, should cache it
            content = [''.join(ch.lower() for ch in wrd if ch not in \
                    set(string.punctuation)) \
                    for wrd in lfile.read().split(' ')]
            #lists of possitive and negative word occurences
            pbag = []
            nbag = []
            for j, elm in enumerate(content):
                if elm in cnf.lexicon:
                    if cnf.lexicon[elm] > 5.5:
                        pbag.append(j)
                    elif cnf.lexicon[elm] < 4.5:
                        nbag.append(j)
            #checking bag contents
            ch_pbag = check_bag(pbag, cnf)
            ch_nbag = check_bag(nbag, cnf)
            if ch_pbag is not None or ch_nbag is not None:
                print lfp.name
                if ch_pbag is not None:
                    print "Pos:"
                    gl_pos_cnt += len(ch_pbag)
                    describe_bag(ch_pbag, content, cnf)
                if ch_nbag is not None:
                    print "Neg:"
                    gl_neg_cnt += len(ch_nbag)
                    describe_bag(ch_nbag, content, cnf)

    print "{2}\nGLP: {0}, GLN: {1}".format(gl_pos_cnt, gl_neg_cnt, '+'*30)

if __name__ == "__main__":
    #yeah, I should know what I am doing, else argpars
    if len(sys.argv) == 1: 
        CONF = ConfHolder(3, 5, 
                './txt_inputs/sentiment-lexicon-morpho-boosted-sorted.txt', 
                '../data/rp_clean')
        CONF.print_conf()
        cruch_corpus(CONF)
    else:
        CONF = ConfHolder(sys.argv[1], sys.argv[2], 
                './txt_inputs/sentiment-lexicon-morpho-boosted-sorted.txt', 
                '../data/rp_clean')
        CONF.print_conf()
        cruch_corpus(CONF)
