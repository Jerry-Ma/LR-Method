#!/usr/bin/python
# -*- coding: utf-8 *-*
#
#Realization of likelihood ratio method for object identifacation.

#imports
from __future__ import division
from loadcfg import loadcfg
from readfile import readfits
from likelihood import likelihood

#main
#load cfg
cf = loadcfg()

#load and get abstract of catalog
filt = (['HATLAS_IAU_ID', 'RA_J2000', 'DEC_J2000', 'F250_BEST', 'LR'],
['objID', 'ra', 'dec', 'r'])
(ct, nm) = readfits('low.fits', 'high.fits', filt)

#calculate likelihood ratio
sigma = 2.4  # in arcsec
r_max = 10

lr = likelihood(ct, nm, sigma, r_max)
