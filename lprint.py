# -*- coding: utf-8 *-*
#filename:lprint.py


def lprint(l, cl=4, ind=0):
    '''gives nice look for long list printing'''

    l = [str(i).rjust(2 + ind) + ': ' + l[i].ljust(20) for i in xrange(0,
    len(l))]
    li = ("".join(l[i:i + cl]) for i in xrange(0, len(l), cl))

    return '\n'.join(li) + '\n'
