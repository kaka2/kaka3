#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
File: mkdwiki.py
Author: hit9
Github:@hit9
Description: A tool convert markdown files in a dir to html files
Support: 
  markdown syntax
  fenced code
  code highlighting
  template
'''

import sys
import os
import markdown
import pickle
import re
from glob import glob

'''-------------------------------------------- global vars -----------------'''

#source file encoding
encoding = 'utf-8'
#cache_filename
cache_filename = '.mkdwiki.cache~'
#tpl_filename
tpl_filename = 'tpl.html'
#title's compiled re
title_re=re.compile(r'%title (.*)')

'''------------------------------------------- global vars end ---------------'''

'''--------------------------------------------common functions-----------------'''

def fatal_error(message):
	print color('[error]', 'red')+' '+message
	sys.exit(1)

def help():
	print '''
help:
  mkdwiki <input-file/dir-path> -o <output-dir-path>

  input-path:a single dir or a file.
  output-path:a single dir.
  source file encoding support:utf-8
'''
	exit()

# --- get all files in a dir --- 
def getfilelist(d):
	filelist = list()
	for i in os.listdir(d):
		f = os.path.join(d,i)
		if os.path.isdir(f):
			filelist.extend(getfilelist(f))
		else:
			filelist.append(f)
	return filelist

# --- color output ---
def color(msg, color):
	colordict = {'red':'\033[91m', 'green':'\033[92m', 'yellow':'\033[93m', 'blue':'\033[94m'}
	return colordict.get(color, '\033[0m')+msg+'\033[0m'

'''------------------------------------------------------------ Cache functions ----------------'''

# --- get cached files dict --- 
def get_cache(cache_filepath):
	f = open(cache_filepath)
	content = f.read()
	f.close()
	try:
		file_dict = pickle.loads(content)
	except:
		fatal_error('cache pickle error. rm '+cache_filepath+' for a try')
	if type({}) != type(file_dict) :
		fatal_error('cache type error. rm '+cache_filepath+' for a try')
	return file_dict

# --- write cache --- 
def write_cache(cache_filepath, file_dict):
	f = open(cache_filepath,'w')
	f.write(pickle.dumps(file_dict))
	f.close()

# --- test file in cache list if modefied --- 
def ismodified(cache_filedict, filepath):
	for i in cache_filedict.iterkeys():
		if os.path.samefile(i, filepath) :
			if os.stat(filepath).st_mtime == cache_filedict[i] :
				return False
	return True

'''--------------------------------------------- Convert functions ----------------------'''

# --- convert a single source to html file --- 
def convert(src, out, tpl, input):

	#read source file
	inf = open(src)
	content = inf.read()
	inf.close()

	#decode
	try:
		content = content.decode(encoding)
	except:
		fatal_error('file:'+src+' encoding not utf8')

	#get title 
	t= title_re.search(content)
	if t :
		title=t.group(1).strip()
		content=content[:t.start()]+content[t.end():]
	else:
		title=os.path.basename(src).decode(encoding)

	#get relpath
	html_root = os.path.relpath(input, os.path.normpath(os.path.dirname(src)))

	#markdown convert
	content = markdown.markdown(content,['fenced_code_hilite','toc'])

	#replace 
	tpl = tpl.replace(u'%title%', title)
	tpl=tpl.replace(u'%html_root%',html_root+u'/')
	content = tpl.replace(u'%content%', content)

	#check output path
	out_dirname = os.path.dirname(out)
	if out_dirname and os.path.exists(out_dirname) == False:
		os.makedirs(out_dirname)

	#write to output
	outf = open(out, 'w')
	outf.write(content.encode(encoding))
	outf.close()
	print color('[ok] ', 'green')+src+' -> '+out

'''--------------------------------------------------- ignore files filter -----------------'''

def ignorefilter(ignore_filelist, filepath):
	#filter hidden files
	if re.match('^\..*', os.path.basename(filepath)):
		return False 
	for i in ignore_filelist :
		if os.path.samefile(i, filepath) :
			return False
	return True

def ignore_user_files(ignore_f, filepath):
	for i in ignore_f:
		try:
			if os.path.basename(filepath) in glob(i.strip('\n')):
				print color('[ignore] ','yellow')+filepath
				return False
		except:
			fatal_error('ignore file is illegal at this : \''+i.strip('\n')+'\'')
	return True; 

'''-------------------------------------------------------------- Main -----------------'''

def main():
	args = sys.argv[1:]

	if (len(args)!=3 or args[1]!='-o') :
		help()

	input = args[0]
	output = args[2]

	#------------------------------------- check inputs ---------

	if (os.path.exists(input) == False):
		fatal_error('input-path \''+input+'\' not exists.')

	if os.path.exists(output) and os.path.isfile(output) :
		fatal_error('output is not dir')

	#------------------------------------- vars init -----------

	cache_filedict = dict()
	ignore_files = list()

	#------------------------------------- filelist init -------

	if os.path.isdir(input) :
		filelist = getfilelist(input)
	else:
		filelist = [input]
		input = os.path.normpath(os.path.dirname(input))

	#------------------------------------- get cache -----------

	cache_path = os.path.join(input, cache_filename)
	if os.path.exists(cache_path) :
		cache_filedict = get_cache(cache_path)
		#add to ignore_files
		ignore_files.append(cache_path)
	#filter out exists path in cache_dict
	cache_filedict = dict((k, v) for k, v in cache_filedict.iteritems() if os.path.exists(k))

	#------------------------------------- get template content ------------------------

	tpl_path = os.path.join(input, tpl_filename)
	if os.path.exists(tpl_path) :
		#add to ignore_files
		ignore_files.append(tpl_path)
		tpl_f = open(tpl_path)
		tpl_content = tpl_f.read().decode(encoding)
	else:
		tpl_content = u'%content%'
	
	#------------------------------------- filter out user ignore files ----
	
	user_ignore_path = os.path.join(input, '.mkdwikiignore')

	if os.path.exists(user_ignore_path):
		ignore_files.append(user_ignore_path)
		f = open(user_ignore_path).readlines()
		filelist = filter(lambda x:ignore_user_files(f, x), filelist)
	
	#------------------------------------- filter out ignore files ----

	filelist = filter(lambda x:ignorefilter(ignore_files, x), filelist)
	
	#------------------------------------- cache process : filter modified files --------

	#if file is in cache , check it if modefied.filter out modefied files from input filelist
	modified_list = filter(lambda f:ismodified(cache_filedict, f), filelist)

	#------------------------------------- convert process ---------

	#make output path list
	html_re=re.compile('(.*)\.[^\.]*$')
	outlist = [ os.path.join(output,html_re.sub(r'\1.html', i)) for i in modified_list ]
	#make tpl_content list
	tpl_content_list = [tpl_content for i in modified_list]
	#make input list
	input_list = [input for i in modified_list]
	#convert filelist
	map(convert, modified_list, outlist, tpl_content_list, input_list)

	#------------------------------------- write cache --------------

	write_cache(cache_path, dict((k, os.stat(k).st_mtime) for k in filelist))

	#------------------------------------- print convert status ------

	converts = len(modified_list)
	skips = len(filelist)-converts
	print color('[status]', 'blue')+" convert: %d files. skip: %d files."%(converts, skips)

if __name__ == '__main__':
	main()
