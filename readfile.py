# -*- coding: utf-8 *-*
#filename: readfile.py

#import
from astropy.io import ascii
from astropy.io import fits
from os import path
#from lprint import lprint
#from math import log10


#load ascii catalog
def readascii(catalog_low, catalog_high):
    '''Read catalog from ascii file'''

    arg = (catalog_low, catalog_high)
    print 'Read txt catalogs:'
    print '  %s \n  %s' % arg

    fn = [0] * 2
    db = [0] * 2

    dn = path.dirname(path.realpath(__file__))

    fn[0] = path.join(dn, catalog_low)
    fn[1] = path.join(dn, catalog_high)
    for i in [0, 1]:
        db[i] = ascii.read(fn[i])

    return 1


#load fits catalog
def readfits(catalog_low, catalog_high, filt):
    '''Read catalog from binary file'''

    arg = (catalog_low, catalog_high)
    print 'Read fits catalogs:'
    print '  %s \n  %s \n' % arg

    fn = [0] * 2  # file path
    db = [0] * 2  # fits handle
    tb = [0] * 2  # full catalog table
    cl = [0] * 2  # column header
    ct = [0] * 2  # filtered catalog table
    nm = [0] * 2  # number of objects
    mask = [0] * 2  # mask applied
    ntb = [0] * 2  # masked table
#    fvega = 3631  # ab-mag

    dn = path.dirname(path.realpath(__file__))

    for i in [0, 1]:
        fn[i] = path.join(dn, arg[i])
        db[i] = fits.open(fn[i])
        tb[i] = db[i][1].data
        cl[i] = db[i][1].columns
        print 'Objects#: %s in %s ' % (len(tb[i].field(0)), arg[i])
        #print '  column headers:'
        #print lprint(cl[i].names, ind=2)
        db[i].close()
        print '    region:'
        if i == 0:
            print '    ra  [%s, %s]' \
            % (min(tb[i].field(2)), max(tb[i].field(2)))
            print '    dec [%s, %s]\n' \
            % (min(tb[i].field(3)), max(tb[i].field(3)))
        else:
            print '    ra  [%s, %s]' \
            % (min(tb[i].field(1)), max(tb[i].field(1)))
            print '    dec [%s, %s]\n' \
            % (min(tb[i].field(2)), max(tb[i].field(2)))
    #mask on low.fits
   # mask[0] = tb[0].field('LR') > -99.0
    #mask[0] = tb[0].field('RA_J2000') > 135.0
    #mask[0] &= tb[0].field('RA_J2000') < 136.0
    #mask[0] &= tb[0].field('DEC_J2000') > 0.0
    #mask[0] &= tb[0].field('DEC_J2000') < 1.0
    mask[0] = tb[0].field('RA_J2000') > 134.5
    mask[0] &= tb[0].field('RA_J2000') < 138.5
    mask[0] &= tb[0].field('DEC_J2000') > -1.5
    mask[0] &= tb[0].field('DEC_J2000') < 2.5
    mask[0] &= tb[0].field('F250_BEST') > 0.032
    ntb[0] = tb[0][mask[0]]
   #for j in range(0, len(ntb[0].field(0))):
       #ntb[0].field(10)[j] = (log10(fvega) - log10(ntb[0].field(10)[j])) * 2.5
# use F250_BEST, convert to ab-mag

    #mask on high.fits
    mask[1] = tb[1].field('r') > 10.
    mask[1] &= tb[1].field('r') < 22.4
    ntb[1] = tb[1][mask[1]]  # mask applied
 #   ntb[1] = tb[1]
    print 'Filtering and generating txt catalog:'

    for i in [0, 1]:
        ascii.write(ntb[i], fn[i] + '.txt', include_names=filt[i])
        ct[i] = ascii.read(fn[i] + '.txt')
        nm[i] = len(ct[i])
        print '  %s -> %s.txt: objects# %s' % (arg[i], arg[i], nm[i])
        print '    filter: %s' % filt[i]
        print '    region:'
        print '    ra  [%s, %s]' % (min(ct[i].field(1)), max(ct[i].field(1)))
        print '    dec [%s, %s]\n' % (min(ct[i].field(2)), max(ct[i].field(2)))

    return (ct, nm)
