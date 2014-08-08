import sys
from itertools import permutations
from gzip import GzipFile
from StringIO import StringIO
from urllib2 import	urlopen

url = "http://scrabblehelper.googlecode.com/svn-history/r20/trunk/ScrabbleHelper/src/dictionaries/sowpods.txt"
url = "http://www.mieliestronk.com/corncob_lowercase.txt"
download = urlopen(url)
download = open("dict-short.txt") # from http://www.mieliestronk.com/corncob_lowercase.txt

#download = StringIO(download.read())
#download = GzipFile(fileobj=download)
dict = set()

for word in download:
	word = str(word.encode("ascii","ignore")).lower().strip()
	dict.add(word)

# dictlist = open("/usr/share/dict/words").readlines()

# for i in range(len(dictlist)):
# 	if dictlist[i] == dictlist[i].lower():
# 		dict.add(dictlist[i].strip())

print "loaded %i words" % len(dict)
cardvalues = { 'a':10, 'b':2, 'c': 8, 'd':6, 'e':10, 'f':2, 'g':4, 'h': 8, 'i': 10,'j':6, 'k': 8, 'l':8, 'm':8, 'n':8, 'o':8, 'p':8, 'q':4, 'r':8, 's':8, 't':8, 'u':8, 'v':6, 'w':8, 'x':2, 'y':4, 'z':2, '?':15 }
for ch in "QWERTYUIOPASDFGHJKLZXCVBNM":
	cardvalues[ch]=15

popularletters = 'etaoinshrdlcumwfgypbvkjxqz'.upper()

progressbar_width = 40

messages=[]
def print_msg(msg):
	sys.stdout.write(" -->  "+msg)
	messages.append(" -->  "+msg)
	sys.stdout.flush()
def unprint_msg():
	l = len(messages.pop())
	
	sys.stdout.write("\b"*l+" "*l+"\b"*l)
	sys.stdout.flush()	


def get_perms(value, cutstart=0, cutend=3, length=7, exactlength=False):

	if '?' in value:
		print_msg("permuting wildcard of %s" % value)
		allvalues = []
		for ch in popularletters[cutstart:cutend]:
			allvalues.extend(get_perms(value.replace('?',ch,1)))
		unprint_msg()	
		return allvalues

	else:	
		print_msg("permuting %s" % value)
		value=value.strip()
		values = []
		if not exactlength:
			lengths = list(range(min(len(value),length)))+[len(value)]
		else:
			if type(length) == list:
				lengths = length
			else:
				lengths = [length]
		
		for i in lengths:
			if len(value) >= i:
				newvalues = permutations(value,i)
				
				values.extend(newvalues)
		for i in range(len(values)):
			values[i] = "".join(values[i]).strip()
		unprint_msg()
		
		return list(set(values))


def get_score(word):
	total = 0
	for ch in word:
		total += cardvalues[ch]
	return total

def print_progressbar(percentage):

	#sys.stdout.write("[%s%s]" % ("-" * (percentage), "_" * (progressbar_width - percentage)))
	#sys.stdout.flush()
	#sys.stdout.write("\b" * (progressbar_width+1)) # return to start of line, after '['

	sys.stdout.write( "\b\b\b\b%s" % (" "*(4-len(str(percentage))) + str(percentage)))
	sys.stdout.flush()

def strsub(str1, str2):
	#remove str2 from str1
	s = str1
	for ch in str2:
		s = s.replace(ch,"",1)
		
	return s

def get_words(cards, combinationlist):
	words = []

	perms = get_perms(cards, length=combinationlist[0], exactlength=True)


	if len(combinationlist) == 1:
		for p in perms:
			if p.lower() in dict:
				words.append(p)
		return words
		
	else:
		for p in perms:
			if p.lower() in dict:
				cardsleft = strsub(cards, p)
				#print "found %s, permuting %s" %(p,cardsleft)
				remainaingcards = get_words(cardsleft, [combinationlist[1:]])
				for p2 in remainaingcards:
					words.append((p,)+(p2,))
			

	return (words)



def get_word(cards, cutstart=0, cutend=5):
	turn = ""
	score = 0
	perms = get_perms(cards, cutstart, cutend)
	permcount = len(perms)
	#print permcount
	prev = 0
	for i in range(permcount):
		next = int(100*float(i)/permcount)
		if next != prev:
			print_progressbar(next)
		prev = next
		word = perms[i]
		wordscore = get_score(word)
		if word.lower() in dict and len(word) >= 3 and (turn == "" or wordscore > score):
			turn = word
			score = wordscore
	sys.stdout.write("\b" * (progressbar_width+1))
	return turn, score

def get_moves(cards):

	# 10
	# 7-3
	# 6-4
	# 4-3-3
	# 5-4
	# 4-4
	# 7
	# 6
	# 3-3
	# 5
	# 4
	# 3
	combinations = [[10],[7,3],[6,4],[5,5],[4,3,3],[9],[3,3,3],[8],[4,4],[7],[4,3],[6],[3,3],[5],[4],[3]]
	
	hands = []
	for c in combinations:
		print_msg(str(c))
		turn = get_words(cards,c)
		#print c, len(turn)
		hands.extend(turn)
		unprint_msg()
	
	return hands

def get_insertions(word, cards):
	perms = get_perms(cards)
	for i in range(len(word)):
		for p in perms:
			pass
last_turn = "	"
while True:
	print
	originalcards = raw_input("Cards: ")
	if originalcards == "":
		print """
ESC  - quit
UP   - cards remainaing from prev hand
DOWN - end round"""
		continue
	if originalcards == "\x1b": #escape:
		exit()
	if originalcards == '\x1b\x5b\x42': #down
		print get_score(raw_input("Cards: (counting) "))
		continue
	if originalcards == "\x1b\x5b\x41": #up
		print "Cards: %s" % last_turn
		originalcards = last_turn
	cards = originalcards
	# i = -1
	# minscore = 25
	# while len(cards) > 8:
	# 	b = False
	# 	for i in range(len(cards)):
	# 		if cardvalues[cards[i]] < minscore:
	# 			minscore = cardvalues[cards[i]]
	# 	for i in range(len(cards)):
	# 		if b: break
	# 		for ch in popularletters[-1::-1]:
	# 			if b:break
	# 			#print cards[i]
	# 			if cardvalues[cards[i]] == minscore and cards[i] == ch:
	# 				cards = cards.replace(cards[i],"",1)
	# 				b=True
	# if len(originalcards) > len(cards):
	# 	print "now working with %s" % cards
	# else:
	# 	print cards
	try:
		#turn, score = get_word(cards)
		turn = get_moves(cards)
		
		if len(turn) > 0:
			minscore = 150
			minscorewordlist = []
			minscoreworddict = {}
			for t in turn:
				newscore = get_score(strsub(cards,"".join(t)))
				if minscore >= newscore or newscore == 0:
					minscore = newscore
					minscorewordlist.insert(0,t)
					minscoreworddict[t] = newscore
			
			for i in range(min(1000,len(minscorewordlist))):
				if type(minscorewordlist[-i-1]) == str:
					print "play %s (with %i points left)" % ((minscorewordlist[-i-1]), minscoreworddict[minscorewordlist[-i-1]])
				else:
					print "play %s (with %i points left)" % (", ".join((minscorewordlist[-i-1])), minscoreworddict[minscorewordlist[-i-1]])
			
		else:
			exchange = raw_input("What is the exposed card? ")
			selection = "hidden"
			if exchange in list(popularletters.lower()[:15]):
				#print "%s is good" % exchange
				selection = "exposed"
			b = False
			for ch in popularletters.lower()[-1::-1]:
				if b: break
				if ch in cards:
					print "Exchange %s for the %s card" % (ch, selection)
					b = True	
		
		
	except KeyError:
		string= '"'
		for ch in cards:
			string+="\\x"+hex(ord(ch))[2:]
		string+= '"'
		print "Unrecognized control squence: %s" % string
		continue

	# if '?' in cards:	
	# 	i = 3
	# 	while turn == "":
	# 		turn, score = get_word(cards, i, i+1)
	# 		i+=1

	# if turn == "":
	# 	turn, score = get_word(originalcards)
	# if turn == :
	# 	print "Please provide the words on the table, each on a new line, followed by an empty line:"
	# 	hands = []
	# 	hand = raw_input("  ~ ")
	# 	while hand != "":
	# 		hands.append(hand)
	# 		hand = raw_input("  ~ ")

	# 	for h in hands:
	# 		get_insertions(h, cards)

	# last_turn = originalcards
	# for ch in turn:
	# 	last_turn = last_turn.replace(ch,"",1)

	
	

			




