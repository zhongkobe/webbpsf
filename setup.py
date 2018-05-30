#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst
# --based on setup.py from astropy--
from __future__ import print_function

import glob
import os
import sys
import imp
import ast

try:
    import numpy
except ImportError:
    print("""
WARNING: NumPy was not found! setup.py will attempt to install it if asked, but
\tyou may experience issues. Try installing NumPy first, separately.
\tSee https://github.com/numpy/numpy/issues/2434 for details.
""")

import ah_bootstrap
from setuptools import setup

#A dirty hack to get around some early import/configurations ambiguities
if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins
builtins._ASTROPY_SETUP_ = True

from astropy_helpers.setup_helpers import (
    register_commands, get_debug_option, get_package_info)
from astropy_helpers.git_helpers import get_git_devstr
from astropy_helpers.version_helpers import generate_version_py

# Get some values from the setup.cfg
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

conf = ConfigParser()
conf.read(['setup.cfg'])
metadata = dict(conf.items('metadata'))

PACKAGENAME = metadata.get('package_name', 'packagename')
DESCRIPTION = metadata.get('description', 'Astropy affiliated package')
AUTHOR = metadata.get('author', '')
AUTHOR_EMAIL = metadata.get('author_email', '')
LICENSE = metadata.get('license', 'unknown')
URL = metadata.get('url', 'http://astropy.org')

# Get the long description from the package's docstring
_, module_path, _ = imp.find_module(PACKAGENAME)
with open(os.path.join(module_path, '__init__.py')) as f:
    module_ast = ast.parse(f.read())
LONG_DESCRIPTION = ast.get_docstring(module_ast)

# Store the package name in a built-in variable so it's easy
# to get from other parts of the setup infrastructure
builtins._ASTROPY_PACKAGE_NAME_ = PACKAGENAME

# VERSION should be PEP386 compatible (http://www.python.org/dev/peps/pep-0386)
VERSION = '0.7.0'

# Indicates if this version is a release version
RELEASE = 'dev' not in VERSION

if not RELEASE:
    VERSION += get_git_devstr(False)

# Populate the dict of setup command overrides; this should be done before
# invoking any other functionality from distutils since it can potentially
# modify distutils' behavior.
cmdclassd = register_commands(PACKAGENAME, VERSION, RELEASE)

# Freeze build information in version.py
generate_version_py(PACKAGENAME, VERSION, RELEASE,
                    get_debug_option(PACKAGENAME))

# Treat everything in scripts except README.rst as a script to be installed
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if os.path.basename(fname) != 'README.rst']


# Get configuration information from all of the various subpackages.
# See the docstring for setup_helpers.update_package_files for more
# details.
package_info = get_package_info()

# Add the project-global data
package_info['package_data'].setdefault(PACKAGENAME, [])
package_info['package_data'][PACKAGENAME].append('data/*')
package_info['package_data'][PACKAGENAME].append('otelm/*')

# Include all .c files, recursively, including those generated by
# Cython, since we can not do this in MANIFEST.in with a "dynamic"
# directory name.
c_files = []
for root, dirs, files in os.walk(PACKAGENAME):
    for filename in files:
        if filename.endswith('.c'):
            c_files.append(
                os.path.join(
                    os.path.relpath(root, PACKAGENAME), filename))
package_info['package_data'][PACKAGENAME].extend(c_files)

setup(name=PACKAGENAME,
      version=VERSION,
      description=DESCRIPTION,
      scripts=scripts,
      install_requires=[
          'numpy>=1.10.0',
          'matplotlib>=1.5.0',
          'scipy>=0.16.0',
          'poppy>=0.6.1',
          'astropy>=1.2.0',
          'jwxml>=0.3.0',
          'pysiaf', 'six',
          'pytest'  # unlisted requirement for pysiaf - see https://github.com/spacetelescope/pysiaf/issues/16
                    # Remove this requirement once that issue is addressed.
      ],
      provides=[PACKAGENAME],
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      url=URL,
      long_description=LONG_DESCRIPTION,
      cmdclass=cmdclassd,
      zip_safe=False,
      use_2to3=True,
      **package_info
)
