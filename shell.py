#!/usr/bin/env python

"""Sets up the faceverif_lib using a torch backend. All arguments passed to this
script are forwarded to the underlying torch shell.py.
"""

import os
import sys
import subprocess

# Choose here the torch release you want to use:
DEFAULT_TORCH_DIR = '/Users/andre/work/torch5spro'

def find_install_dir():
  """Test to see if I find my own libraries, otherwise, we are probably running
  on the SGE grid using the shell.py script as a launcher. In this case, we
  have to find an alternative. You should set always the job with the -cwd
  option and submit from the root of the faceveriflib package. As an option, you
  can set the environment variable FACEVERIFLIB_DIR using qsub -v
  FACEVERIFLIB_DIR=<bla/bla>"""

  install_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
  test_path = os.path.join(install_dir, 'lib')

  if not os.path.exists(test_path): #not on CWD, try FACEVERIFLIB_DIR
    if os.environ.has_key('FACEVERIFLIB_DIR') and os.environ['FACEVERIFLIB_DIR']:
      install_dir = os.environ['FACEVERIFLIB_DIR']
      test_path = os.path.join(install_dir, 'lib')

  if not os.path.exists(test_path): #not found, maybe is on the PWD
    if os.environ.has_key('PWD') and os.environ['PWD']:
      install_dir = os.environ['PWD']
      test_path = os.path.join(install_dir, 'lib')

  if not os.path.exists(test_path):
    raise RuntimeError, 'You are running this job using a script outside the faceveriflib root directory. This is not a problem, as long as you set FACEVERIFLIB_DIR on the environment to point to the root directory of the faceveriflib package.'

  return os.path.realpath(install_dir)

def find_torch_dir(install_dir):
  """Does the best to find the torch installation directory"""
   
  if os.environ.has_key('TORCH_DIR') and os.environ['TORCH_DIR'] and \
      os.path.exists(os.environ['TORCH_DIR']):
    torch = os.environ['TORCH_DIR']
  else:
    torch = DEFAULT_TORCH_DIR

  """
  if not os.path.exists(torch): # in the faceveriflib directory?
    torch = os.path.join(install_dir, 'torch')

  if not os.path.exists(torch): # at the same level?
    torch = os.path.join(install_dir, '..', 'torch')
  """

  if not os.path.exists(torch):
    raise RuntimeError, 'Cannot find a suitable torch5spro installation. The faceveriflib library requires torch5spro to run. You have 3 options: either set the environment variable TORCH_DIR to point to the "bin" directory inside the root of a torch installation, create a link from the faceveriflib installation directory or from one level up. The link has be called "torch".' 

  return os.path.realpath(torch)

# Locates base faceveriflib installation directory
install_dir = find_install_dir()
torch = find_torch_dir(install_dir)

print "Using torch directory located here: %s." % torch

path = 'PATH'
pypath = 'PYTHONPATH'

script_path = os.path.join(install_dir, 'script')
lib_path = os.path.join(install_dir, 'lib')

# Copies the environment
new_environ = dict(os.environ)

if new_environ.has_key(path) and new_environ[path]:
  new_environ[path] = ':'.join([script_path, new_environ[path]])
else:
  new_environ[path] = script_path

if new_environ.has_key(pypath) and new_environ[pypath]:
  new_environ[pypath] = ':'.join([lib_path, new_environ[pypath]])
else:
  new_environ[pypath] = lib_path

# execute the torch shell setup
shell = os.path.join(torch, 'bin', 'shell.py')
arguments = [shell] + sys.argv[1:]
#arguments = [shell, '-d'] + sys.argv[1:]

try:
  p = subprocess.Popen(arguments, env=new_environ)
except OSError as e:
  # occurs when the file is not executable or not found
  sys.stderr.write("Error executing '%s': %s (%d)\n" % (' '.join(arguments),
    e.strerror, e.errno))
  sys.exit(e.errno)
  
try:
  p.communicate()
except KeyboardInterrupt: # the user CTRL-C'ed
  import signal
  os.kill(p.pid, signal.SIGTERM)
  sys.exit(signal.SIGTERM)

sys.exit(p.returncode)
