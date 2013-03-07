# -*- coding: utf-8 *-*
#filename:loadcfg.py

#import
from ConfigParser import SafeConfigParser
from os import path


#load config file
def loadcfg():
    '''Load settings from par.cfg'''

    conf_list = {'path': {
        'catalog_low': 'low.txt',
        'catalog_high': 'high.txt',
        },
        'switch': {
        'catatype': 'fits'
        }
    }

#config filename
    dn = path.dirname(path.realpath(__file__))
    fn = path.join(dn, 'par.cfg')
    print 'Working directory: %s \n' % dn
    parser = SafeConfigParser()
    parser.read(fn)

#not exist then write
    if not parser.sections():
        print 'file not found: par.cfg'
        print 'use default, writing to par.cfg:'
        parser.add_section('path')
        parser.set('path', 'catalog_low', 'low.txt')
        parser.set('path', 'catalog_high', 'high.txt')
        parser.add_section('switch')
        parser.set('switch', 'catatype', 'fits')
        with open(fn, 'wb') as cfg:
            parser.write(cfg)
#read
    for sec_name in parser.sections():
        print 'Loading settings:', sec_name
        for par in conf_list[sec_name]:
            if parser.has_option(sec_name, par):
                conf_list[sec_name][par] = parser.get(sec_name, par)
                print '  %s = %s' % (par, conf_list[sec_name][par])
            else:
                print '  %s missing, use default: %s' \
                % (par, conf_list[sec_name][par])
        print ''
    return conf_list
