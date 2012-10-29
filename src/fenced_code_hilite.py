#!/usr/bin/env python
"""
modified from extension fenced_code .thanks it ..^_^
usage:
	markdown(content,['fenced_code_hilite'])
options: 
	pygments:if use pygments to hilite code(1 for yes,0 for no)
	markdown(content,['fenced_code_hilite(pygments=0)'])
require:pygments,codehilite
"""
import markdown, re
# Global vars
FENCED_BLOCK_RE = re.compile( \
		r'(?P<fence>^`{3,})[ ]*(?P<lang>[a-zA-Z0-9_-]*)[ ]*\n(?P<code>.*?)(?P=fence)[ ]*$', 
		re.MULTILINE|re.DOTALL
		)
CODE_WRAP = '<pre%s>%s</pre>'
LANG_TAG = ' class="brush:%s"'

class FencedCodeExtension(markdown.Extension):
	def extendMarkdown(self, md, md_globals):
		""" Add FencedBlockPreprocessor to the Markdown instance. """
		fenced_code_block=FencedBlockPreprocessor(md)
		fenced_code_block.config=self.config
		md.preprocessors.add('fenced_code_block', fenced_code_block, "_begin")
	def __init__(self,configs):
		self.config={'pygments':['1',"if use pygments to hilite code"]}
		for key, value in configs:
			self.setConfig(key, value) 

class FencedBlockPreprocessor(markdown.preprocessors.Preprocessor):
	def run(self, lines):
		""" Match and store Fenced Code Blocks in the HtmlStash. """
		text = "\n".join(lines)
		while 1:
			m = FENCED_BLOCK_RE.search(text)
			if m:
				lang = ''
				if m.group('lang'):
					lang = LANG_TAG % m.group('lang')
				if self.config['pygments'][0]=='1':
					from codehilite import CodeHilite
					code = CodeHilite()
					code.src = m.group('code')
					code.lang = m.group('lang')
					code.linenos = False
					code = code.hilite()
				else:
					code = CODE_WRAP % (lang, self._escape(m.group('code')))
				placeholder = self.markdown.htmlStash.store(code, safe=True)
				text = '%s\n%s\n%s'% (text[:m.start()], placeholder, text[m.end():])
			else:
				break
		return text.split("\n")

	def _escape(self, txt):
		""" basic html escaping """
		txt = txt.replace('&', '&amp;')
		txt = txt.replace('<', '&lt;')
		txt = txt.replace('>', '&gt;')
		txt = txt.replace('"', '&quot;')
		return txt


def makeExtension(configs={}):
	return FencedCodeExtension(configs=configs)

if __name__ == "__main__":
	import doctest
	doctest.testmod()
