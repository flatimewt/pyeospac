#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import Extension
import os.path
import re
from datetime import datetime
import numpy

def setup_eospac(cfg):

    EOSPAC_INCLUDE = os.path.join(cfg['path'], "include", cfg['arch'], cfg['compiler'])
    EOSPAC_LIB = os.path.join(cfg['path'], "lib", cfg['arch'], cfg['compiler'])

    for test_path in [cfg['path'], EOSPAC_INCLUDE, EOSPAC_LIB]:
        if not os.path.exists(test_path):
            raise OSError("Path does not exist: '{0}'. Please edit setup.cfg !".format(test_path))



    #===============================================================================#
    #               Creating constants.py from C headers eos_Interface.h
    #===============================================================================#

    with open(os.path.join(EOSPAC_INCLUDE, "eos_Interface.h"), 'r') as f:
        header = f.readlines()

    sections = {'tables':
                    { 'expr': r'/\* table types: \*/',
                      'begin': 0, 
                      'previous': None},
                'options': 
                    { 'expr': r'/\* Table setup and interpolation option constants \*/',
                      'previous': 'tables'},
                'info':
                    { 'expr': r'/\* Data information constants \*/',
                      'previous': 'options'},
                'errors':
                    { 'expr': r'/\* Error code constants \*/',
                      'previous': 'info',
                      'end': -1}
                }

    for idx, line in enumerate(header):
        for section_name, section_dict in sections.iteritems():
            if re.match(section_dict['expr'], line):
                section_dict['begin'] = idx+1
                if section_dict['previous']:
                    sections[section_dict['previous']]['end'] = idx-1

    with open('eospac/eospac/constants.py', 'w') as f:
        f.write("""#!/usr/bin/python      
# -*- coding: utf-8 -*-

# Warning! This file is automatically generated from the eos_Interface.h
# header by the setup.py script. All manual changes will be overwritten
# at the next install.
# Created on: {0}\n\n""".format(datetime.now()))
        for section_name, section_dict in sections.iteritems():
            f.write('{0}  = dict(\n'.format(section_name))
            out_txt = []
            for line in header[section_dict['begin']:section_dict['end']]:
                if re.match('^static const EOS_INTEGER EOS.*', line):
                    txt = re.sub('^static const EOS_INTEGER EOS_', ' '*4, line)
                    txt = re.sub('/\*', '#', txt)
                    txt = re.sub('\*/', '', txt)
                    txt = re.sub(';', ',', txt)
                    if section_name == 'options':
                        # convert options section keys to lowercase
                        comma_idx = txt.find(',')
                        txt = txt[:comma_idx].lower() + txt[comma_idx:]
                    out_txt.append(txt)
            f.write(''.join(out_txt))
            f.write(')\n\n')

    return  [Extension("eospac.eospac.libpyeospac",
                 sources=["eospac/eospac/libpyeospac.pyx"],
                 include_dirs=[numpy.get_include(), EOSPAC_INCLUDE],
                 library_dirs=[EOSPAC_LIB],
                 libraries=['eospac6']),
            Extension("eospac.eospac.libsesio",
                 sources=["eospac/eospac/libsesio.pyx"],
                 include_dirs=[numpy.get_include(), EOSPAC_INCLUDE],
                 library_dirs=[EOSPAC_LIB],
                 libraries=['eospac6'])]




