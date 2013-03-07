# -*- coding: utf-8 *-*
#filename: likelihood.py
from __future__ import division
from numpy import histogram, sum, argmax  # array, savetxt
#from scipy.stats import scoreatpercentile
from math import *
from numpy.lib.recfunctions import stack_arrays
#import random
from matplotlib import pyplot


def likelihood(t, n, s, r):

    '''Calculate likelihood ratio'''
    m_h = t[1].field(3).tolist()  # mag value of high-res catalog
    nm_l = len(t[0].field(0))     # Number of centroids in low-res catalog
    lrm_l = t[0].field(4).tolist()  # LR value by Smith et al
    idm_l = t[0].field(0).tolist()  # ID of HATLAS sources

    print 'Calculating likelihood ratio'
    print '  compiling list of matches:'
    cnd = []  # candidate list of counterparts for sources in low-res catalog
    for i in range(0, nm_l):
        src = t[0][i]  # iterate srcs in low-res cat [1] for x [2] for y
        tmp = findcnd(src[1], src[2], r, t[1])  # list of objs in r_max
        cnd.append(tmp)  # write to list
    mtch = stack_arrays(cnd, autoconvert=True, usemask=False)
#   compile cnd[] to one big list since cnd[] is list of lists
#   mtch = unique(stack_arrays(cnd, autoconvert=True, usemask=False))
    m_mtch = [elm[3] for elm in mtch]  # magnitude of mch

    bn = 31     # bin number
    # bn = findbin(m)       # get bin number by F-D method
    print '  bin#: %s' % bn

    print '  histograms for %s objects throughout %s\n' % (len(mtch), len(m_h))
    print '  drawing histogram:'
    (histtotal, bedge) = histogram(m_mtch, bins=bn, range=(10, 22.4))
    # total(m)
    print '  bin edges: '
    print bedge
    print '\n  total(m)'
    print histtotal

    print '\n  n(m)'
    histn_l = histogram(m_h, bins=bedge)  # histogram n(m)
    histn = [0] * (len(histtotal))  # normalized list for n(m)
    histbg = [0] * (len(histtotal))  # normalized list for background dist
    for i in range(0, len(histn_l[0])):
        histn[i] = histn_l[0][i] / 100 / 3600 ** 2
         # area of h_cat 35.982182771 168.631304818
        histbg[i] = histn[i] * nm_l * pi * r ** 2
    print histn

    print '\n  real(m)'
    histreal = [0] * (len(histtotal))
    for i in range(0, len(histreal)):
        histreal[i] = histtotal[i] - histbg[i]  # real(m), non-norm
        if histreal[i] < 0:
            histreal[i] = 0
    print histreal

    print '\n  Q_0'
    Q = (len(mtch) - sum(histbg)) / nm_l
    #Q= 0.58
    print Q

    print '\n  q(m)'
    histq = [0] * (len(histtotal))
    sumreal = sum(histreal)
    for i in range(0, len(histq)):
        histq[i] = histreal[i] / sumreal * Q
    print histq

    print '\n q(m)/n(m)'
    histqn = [0] * (len(histtotal))
    for i in range(0, len(histqn)):
        if histn[i] == 0:
            histqn[i] = 1
        else:
            histqn[i] = histq[i] / histn[i]
    for i in range(bn, 0, -1):
        if bedge[i] < 14.2:
            histqn[i - 1] = histqn[i]
    print histqn

    #plot the histograms
    pyplot.step(bedge[:-1], [a + 1e-20 for a in histq], color='blue')
    pyplot.ylim(ymin=1e-6)
    pyplot.yscale('log')
    pyplot.ylabel('q(m)')
    pyplot.savefig('q.eps')
    pyplot.clf()
    pyplot.step(bedge[:-1], [a + 1e-20 for a in histqn], color='blue')
    pyplot.ylim(ymin=1)
    pyplot.yscale('log')
    pyplot.ylabel('q(m)/n(m)')
    pyplot.savefig('qn.eps')
    pyplot.clf()
    pyplot.step(bedge[:-1], [a + 1e-20 for a in histtotal], color='blue')
    pyplot.step(bedge[:-1], [a + 1e-20 for a in histbg], color='black')
    pyplot.step(bedge[:-1], [a + 1e-20 for a in histreal], color='red')
    pyplot.ylim(ymin=1e-1)
    pyplot.yscale('log')
    pyplot.ylabel('counts')
    pyplot.legend(('total(m)', 'bg(m)', 'real(m)'),
           'upper left', shadow=True)
    pyplot.savefig('counts.eps')
    pyplot.clf()
    #calculate LR
    print '\n  LR(m,r)'
    lrobj = [[0], ]  # list of lists, as the same structure of cnd[]
    qnobj = [[0], ]
    for i in range(0, nm_l):
        if i != 0:
            lrobj.append([0])  # initialize
            qnobj.append([0])
        if len(cnd[i]) > 0:  # those objs have candidate counterpart
            for j in range(0, len(cnd[i])):
                kk = 0
                for k in range(0, bn):  # find which bin the m falls in
                    if cnd[i][j][3] < bedge[k]:
                        kk = k
                       # print kk,
                        break

                tmplr = histqn[kk - 1] * f(rs(t[0][i][1], t[0][i][2], cnd[i][j][1], cnd[i][j][2]), s)
                tmpqn = histqn[kk - 1]
                if j != 0:
                    lrobj[i].append(tmplr)
                    qnobj[i].append(tmpqn)
                else:
                    lrobj[i][0] = tmplr
                    qnobj[i][0] = tmpqn
    print ''
    for i in range(0, 5):
        print lrobj[i]
    print '...'

    print '\nCalculating reliability:'
    rlobj = [[0], ]
    for i in range(0, len(lrobj)):
        lsum = sum(lrobj[i]) + 1 - Q
        if i != 0:
            rlobj.append([0])

        for j in range(0, len(lrobj[i])):
            if j != 0:
                rlobj[i].append(lrobj[i][j] / lsum)
            else:
                rlobj[i][0] = lrobj[i][0] / lsum
# print rlobj
    #prl = [val for subl in rlobj for val in subl]

    #for p in prl:
        #print "{0:.0f}%".format(float(p) * 100),
    #return 1
    print ''
    for i in range(0, 5):
        print rlobj[i]
    print '...'

    print '\nGenerate adopted LR list:'
    adobj = [0] * nm_l
    for i in range(0, len(adobj)):
        if max(rlobj[i]) > 0.8:
            adlr = lrobj[i][argmax(rlobj[i])]
            adqn = qnobj[i][argmax(rlobj[i])]
        else:
            adlr = -99.0
            adqn = -99.0
        adobj[i] = [idm_l[i], lrm_l[i], adlr, adqn]
    print '  write to file: rst.txt'
   # savetxt('rst.txt', array(adobj))
    #pyplot.step(range(0, len(adobj)), [a[2] / a[1] for a in adobj], color='blue')
    #split ones with -99.0
    with99 = []
    without = []
    with1 = []
    for i in range(0, len(adobj)):
        if adobj[i][2] / adobj[i][1] == 1.:
            with1.append([i, adobj[i][2] / adobj[i][1]])
        elif adobj[i][1] < -90.0 or adobj[i][2] < -90.0:
            with99.append([i, adobj[i][2] / adobj[i][1]])
        else:
            without.append([i, adobj[i][2] / adobj[i][1], adobj[i][3], adobj[i][2] / adobj[i][3]])
    for i in range(0, len(with99)):
        if with99[i][1] > 5:
            with99[i][1] = 5
        if with99[i][1] < -5:
            with99[i][1] = -5
    for i in range(0, len(without)):
        if without[i][1] > 5:
            without[i][1] = 5
        if without[i][1] < -5:
            without[i][1] = -5
        if without[i][3] > .1:
            without[i][3] = .1
        if without[i][3] < -.1:
            without[i][3] = -.1
    pyplot.scatter([a[0] for a in with99], [a[1] for a in with99], s=1, lw=0, color='red')
    pyplot.scatter([a[0] for a in without], [a[1] for a in without], s=1, lw=0, color='blue')
    pyplot.scatter([a[0] for a in with1], [a[1] for a in with1], s=1, lw=0, color='yellow')
  #  pyplot.scatter([a[0] for a in without], [a[2] / 3000 for a in without], s=1, lw=0, color='green')
  #  pyplot.scatter([a[0] for a in without], [a[1] / a[3] / 50 for a in without], s=1, lw=0, color='black')
    pyplot.ylabel('myLR/SmithLR')
    pyplot.xticks([], [])
    pyplot.xlabel('HAtlas source: brighter --> fainter')
    pyplot.legend(('perc of dismatch: ' + str(len(with99)/len(adobj))[:4],
    'perc of both-have-value: ' + str(len(without)/len(adobj))[:4],
    'perc of both-99.00: ' + str(len(with1)/len(adobj))[:4]),
           'lower left', shadow=True)
    pyplot.savefig('LRcompare.eps')
    pyplot.clf()
    pyplot.scatter([a[0] for a in without], [a[2] for a in without], s=1, lw=0, color='blue')
    pyplot.ylabel('q(m)/n(m)')
    pyplot.xticks([], [])
    pyplot.xlabel('HAtlas source: brighter --> fainter')
    pyplot.savefig('qn.eps')
    pyplot.clf()
    pyplot.scatter([a[0] for a in without], [a[3] for a in without], s=1, lw=0, color='blue')
    pyplot.ylabel('f(r)')
    pyplot.xticks([], [])
    pyplot.xlabel('HAtlas source: brighter --> fainter')
    pyplot.savefig('f(r).eps')


def f(rsquare, s):
    '''positional distribution'''

    return 1. / 2. / pi / s ** 2 * exp(-rsquare / 2. / s ** 2)


def findcnd(x, y, r, c):
    '''retrieve candidates list from high-res catalog'''

    #return c[rs(c.field(1), c.field(2), x, y) <= r ** 2]
    # offset < r_max
    return c[((c.field(1) - x) * 3600 *
    cos(radians(y))) ** 2 +
    ((c.field(2) - y) * 3600) ** 2 < r ** 2]  # offset < r_max


def rs(x, y, a, b):
    '''get objects offset, r squared, in arcsec'''

    # input in degree
    f = cos(radians(b))
    return ((x - a) * 3600 * f) ** 2 + ((y - b) * 3600) ** 2
    # output in arcsec


def findbin(x):
    '''Calculates the Freedman-Diaconis bin size by Freedman–Diaconis rule'''

# First Calculate the interquartile range
    x.sort()
#    ma = max(x)
#    mi = min(x)
#    x.remove(ma)
#    x.remove(mi)

    upperQuartile = scoreatpercentile(x, .75)
    lowerQuartile = scoreatpercentile(x, .25)
    IQR = upperQuartile - lowerQuartile

    # Find the F-D bin size
    h = 2. * IQR / len(x) ** (1. / 3.)
    bn = int(ceil((max(x) - min(x)) / h))
# print '  bin#: %s' % bn
# Bin edge list
# bl = [i*h+min(x) for i in range(0, bn+1) ]
# bl.insert(0,mi)
# bl.append(ma+h)

    return bn
