all:
	mkdwiki index.mkd -o ../html
	mkdwiki github-style -o ../html
	mkdwiki solarizeddark-style -o ../html
	mkdwiki solarizedlight-style -o ../html
clean:
	rm ../html/github-style -rf
	rm ../html/solarizeddark-style -rf
	rm ../html/solarizedlight-style -rf
	rm ../html/index.html
	rm .mkdwiki.cache~
	rm solarizeddark-style/.mkdwiki.cache~
	rm solarizedlight-style/.mkdwiki.cache~
	rm github-style/.mkdwiki.cache~
