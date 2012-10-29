'''
File: setup.py
Author: hit9
Description: setup for mkdwiki
'''
import os,sys
#---------------------------------- color output ---

def color(msg, color):
	colordict = {'red':'\033[91m', 'green':'\033[92m', 'yellow':'\033[93m', 'blue':'\033[94m'}
	return colordict.get(color, '\033[0m')+msg+'\033[0m'

def fatal_error(message):
	print color('[failed]', 'red')+' '+message
	sys.exit(1)
#-----------------------plat check-------------------------
if os.name  != 'posix' :
	fatal_error('require linux plat')

#-----------------------python version check----------------

print 'check python version...'
if sys.version_info[0]!=2:
	fatal_error('require python 2.x')

#-----------------------markdown module check----------------

print 'check markdown module...'
try:
	import markdown
except ImportError:
	fatal_error('failed to import markdown module')

if markdown.version_info[1]<2 :
	fatal_error('require:markdown version at least 2.0.')

#---------------------pygments module check-----------------
print 'check pygments module...'
try:
	import pygments
except ImportError:
	fatal_error('failed to import pygments module')

#--------------------markdown extension install------------

markdown_module_path=os.path.dirname(markdown.__file__)
setup_ext_path=markdown_module_path+'/extensions/'

#--------------------comiple extension to pyc -----------------

import py_compile
py_compile.compile("src/fenced_code_hilite.py")

#--------------------install via system------------------------

#if linux plat
installed_path = '/usr/bin/mkdwiki'
os.system('cp src/fenced_code_hilite.py '+setup_ext_path+'fenced_code_hilite.py')
os.system('cp src/fenced_code_hilite.pyc '+setup_ext_path+'fenced_code_hilite.pyc')
os.system('cp src/mkdwiki.py '+installed_path)
os.system('chmod u+x '+installed_path)
os.system('chmod 777 -R '+installed_path)
print color('[installed]', 'green')+' installed path: '+installed_path
