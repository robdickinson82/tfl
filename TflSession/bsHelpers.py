from bs4 import BeautifulSoup

def getSoupFromHtml(htmlDoc):
	soup = BeautifulSoup(htmlDoc, 'html.parser')
	return soup