#!/usr/bin/env python
#
#   Setup script for sK1 2.x
#
# 	Copyright (C) 2013-2016 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Usage: 
--------------------------------------------------------------------------
 to build package:       python setup-sk1.py build
 to install package:     python setup-sk1.py install
 to remove installation: python setup-sk1.py uninstall
--------------------------------------------------------------------------
 to create source distribution:   python setup-sk1.py sdist
--------------------------------------------------------------------------
 to create binary RPM distribution:  python setup-sk1.py bdist_rpm
--------------------------------------------------------------------------
 to create binary DEB distribution:  python setup-sk1.py bdist_deb
--------------------------------------------------------------------------.
 Help on available distribution formats: --help-formats
"""

from distutils.core import setup
import datetime
import os
import shutil
import sys

import buildutils
import dependencies
from native_mods import make_modules

sys.path.insert(1, os.path.abspath('./src'))

from sk1 import appconst

############################################################
# Flags
############################################################
UPDATE_MODULES = False
DEB_PACKAGE = False
RPM_PACKAGE = False
CLEAR_BUILD = False

############################################################
# Package description
############################################################
NAME = appconst.APPNAME
VERSION = appconst.VERSION + appconst.REVISION
DESCRIPTION = 'Vector graphics editor for prepress'
AUTHOR = 'Igor E. Novikov'
AUTHOR_EMAIL = 'sk1.project.org@gmail.com'
MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL
LICENSE = 'GPL v3'
URL = 'http://sk1project.net'
DOWNLOAD_URL = URL
CLASSIFIERS = [
    'Development Status :: 5 - Stable',
    'Environment :: Desktop',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: LGPL v2',
    'License :: OSI Approved :: GPL v3',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python',
    'Programming Language :: C',
    "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
]
LONG_DESCRIPTION = '''
sK1 is an open source vector graphics editor similar to CorelDRAW, 
Adobe Illustrator, or Freehand. First of all sK1 is oriented for prepress 
industry, therefore works with CMYK colorspace and produces CMYK-based PDF 
and postscript output.
sK1 Project (http://sk1project.net),
Copyright (C) 2004-%s sK1 Project Team
''' % str(datetime.date.today().year)

LONG_DEB_DESCRIPTION = ''' .
 sK1 is an open source vector graphics editor similar to CorelDRAW, 
 Adobe Illustrator, or Freehand. First of all sK1 is oriented for prepress 
 industry, therefore works with CMYK colorspace and produces CMYK-based PDF 
 and postscript output.
 . 
 sK1 Project (http://sk1project.net),
 Copyright (C) 2004-%s sK1 Project Team
 .
''' % str(datetime.date.today().year)

############################################################
# Build data
############################################################
install_path = '/usr/lib/%s-wx-%s' % (NAME, VERSION)
os.environ["APP_INSTALL_PATH"] = "%s" % (install_path,)
src_path = 'src'
include_path = '/usr/include'
modules = []
scripts = ['src/script/sk1', ]
deb_scripts = []
data_files = [
    ('/usr/share/applications', ['src/sk1.desktop', ]),
    ('/usr/share/pixmaps', ['src/sk1.png', 'src/sk1.xpm', ]),
    ('/usr/share/icons/hicolor/scalable/apps', ['src/sk1.svg', ]),
    (install_path, ['GPLv3.txt', 'LICENSE', ]),
]

EXCLUDES = ['sword', ]

############################################################
deb_depends = ''
rpm_depends = ''
############################################################

dirs = buildutils.get_dirs_tree('src/sk1/share')
share_dirs = []
for item in dirs:
    share_dirs.append(os.path.join(item[8:], '*.*'))

package_data = {
    'sk1': share_dirs,
}

############################################################
# Main build procedure
############################################################

if len(sys.argv) == 1:
    print 'Please specify build options!'
    print __doc__
    sys.exit(0)

if len(sys.argv) > 1:

    if sys.argv[1] == 'bdist_rpm':
        CLEAR_BUILD = True
        RPM_PACKAGE = True
        sys.argv[1] = 'sdist'
        rpm_depends = dependencies.get_sk1_rpm_depend()

    if sys.argv[1] == 'build_update':
        UPDATE_MODULES = True
        CLEAR_BUILD = True
        sys.argv[1] = 'build'

    if sys.argv[1] == 'bdist_deb':
        DEB_PACKAGE = True
        CLEAR_BUILD = True
        sys.argv[1] = 'build'
        deb_depends = dependencies.get_sk1_deb_depend()

    if sys.argv[1] == 'uninstall':
        if os.path.isdir(install_path):
            # removing sk1 folder
            print 'REMOVE: ' + install_path
            os.system('rm -rf ' + install_path)
            # removing scripts
            for item in scripts:
                filename = os.path.basename(item)
                print 'REMOVE: /usr/bin/' + filename
                os.system('rm -rf /usr/bin/' + filename)
            # removing data files
            for item in data_files:
                location = item[0]
                file_list = item[1]
                for file_item in file_list:
                    filename = os.path.basename(file_item)
                    filepath = os.path.join(location, filename)
                    if not os.path.isfile(filepath):
                        continue
                    print 'REMOVE: ' + filepath
                    os.system('rm -rf ' + filepath)
            print 'Desktop database update: ',
            os.system('update-desktop-database')
            print 'DONE!'
        else:
            print 'sK1 installation is not found!'
        sys.exit(0)

# Preparing start script
src_script = 'src/script/sk1.tmpl'
dst_script = 'src/script/sk1'
fileptr = open(src_script, 'rb')
fileptr2 = open(dst_script, 'wb')
while True:
    line = fileptr.readline()
    if line == '':
        break
    if '$APP_INSTALL_PATH' in line:
        line = line.replace('$APP_INSTALL_PATH', install_path)
    fileptr2.write(line)
fileptr.close()
fileptr2.close()

# Preparing MANIFEST.in and setup.cfg
############################################################
shutil.copy2('MANIFEST.in_sk1', 'MANIFEST.in')

fileptr = open('setup.cfg_sk1', 'rb')
fileptr2 = open('setup.cfg', 'wb')
content = fileptr.read()
if rpm_depends:
    content += '\nrequires = ' + rpm_depends
fileptr2.write(content)
fileptr.close()
fileptr2.close()

############################################################
# Native extensions
############################################################

modules += make_modules(src_path, include_path)

############################################################
# Setup routine
############################################################

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    license=LICENSE,
    url=URL,
    download_url=DOWNLOAD_URL,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    packages=buildutils.get_source_structure(excludes=EXCLUDES),
    package_dir=buildutils.get_package_dirs(excludes=EXCLUDES),
    package_data=package_data,
    data_files=data_files,
    scripts=scripts,
    ext_modules=modules)

############################################################
# .py source compiling
############################################################
if not UPDATE_MODULES:
    buildutils.compile_sources()

############################################################
# This section for developing purpose only
# Command 'python setup.py build_update' allows
# automating build and copying of native extensions
# into package directory
############################################################
if UPDATE_MODULES:
    buildutils.copy_modules(modules)

############################################################
# Implementation of bdist_deb command
############################################################
if DEB_PACKAGE:
    buildutils.DebBuilder(
        name=NAME,
        version=VERSION,
        maintainer='%s <%s>' % (AUTHOR, AUTHOR_EMAIL),
        depends=deb_depends,
        homepage=URL,
        description=DESCRIPTION,
        long_description=LONG_DEB_DESCRIPTION,
        section='graphics',
        package_dirs=buildutils.get_package_dirs(excludes=EXCLUDES),
        package_data=package_data,
        scripts=scripts,
        data_files=data_files,
        deb_scripts=deb_scripts,
        dst=install_path)

############################################################
# Implementation of bdist_rpm command
############################################################
if RPM_PACKAGE:
    buildutils.RpmBuilder(
        name=NAME,
        version=VERSION,
        release='0',
        arch='',
        maintainer='%s <%s>' % (AUTHOR, AUTHOR_EMAIL),
        summary=DESCRIPTION,
        description=LONG_DESCRIPTION,
        license=LICENSE,
        url=URL,
        depends=rpm_depends.split(' '),
        build_script='setup-sk1.py',
        install_path=install_path,
        data_files=data_files, )

if CLEAR_BUILD:
    buildutils.clear_build()

for item in ['MANIFEST', 'MANIFEST.in', 'src/script/sk1', 'setup.cfg']:
    if os.path.lexists(item):
        os.remove(item)
