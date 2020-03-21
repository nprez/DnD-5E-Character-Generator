import random

#Settings
weightedRaces = True

def getFileLines(file):
	return [line.rstrip('\n\r') for line in open(file)]

#load list from file
def getList(file):
	return getFileLines('lists/'+file+'.txt')

#tables are stored in text files according to the following syntax:
#first line defines the dice rolled to generate a result
#every subsequent line lists outcomes
#[Optional] an outcome can list the specific roll(s) it corresponds to
#[Optional] multiple outcomes can share the same odds range
#[Optional] multiple results can share a range using /
#see tables folder for examples
class Table:
	outcomes = {}
	#load table from file
	def __init__(self, file):
		lines = getFileLines('tables/'+file+'.txt')
		#figure out what to roll
		dice = lines[0]
		diceSplit = dice.split('d')
		self.diceNum = int(diceSplit[0])
		self.diceSize = int(diceSplit[1])
		i = 1
		for outcome in lines[1:]:
			#check if there are odds listed
			if '|' in outcome:
				splitParts = outcome.split('|')
				odds = splitParts[0]
				text = splitParts[1]
				#check if the odds are a range
				if '-' in odds:
					oddsSplit = odds.split('-')
					lowOdd = int(oddsSplit[0])
					highOdd = int(oddsSplit[1])
				else:
					lowOdd = int(odds)
					highOdd = int(lowOdd)
			else:
				text = outcome
				lowOdd = i
				highOdd = i
			i += (highOdd-lowOdd)+1
			self.addOutcome(text, lowOdd, highOdd)
	#call to define table results
	def addOutcome(self, text, lowOdd, highOdd=None):
		lowRoll = lowOdd
		highRoll = highOdd
		if highOdd is None:
			highRoll = lowOdd
		if lowRoll < 1 or highRoll > (self.diceSize * self.diceNum):
			print 'invalid odds range: ' + lowOdd + '-' + highOdd
			return None
		for number in range(lowRoll, highRoll+1):
			self.outcomes[number] = text
	#generate a table result
	def roll(self):
		randomOutcome = self.outcomes[dice(self.diceNum, self.diceSize)]
		outcomes = randomOutcome.split('/')
		random.shuffle(outcomes)
		return outcomes[0]
	def printTable(self):
		print str(self.diceNum) + 'd' + str(self.diceSize)
		i = 1
		while i in range(1, self.diceSize+1):
			lowRange = i
			highRange = i
			text = self.outcomes[i]
			while i <= self.diceSize and text == self.outcomes[i]:
				highRange = i
				i = i+1
			rangeStr = str(lowRange) + '-' + str(highRange)
			if lowRange == highRange:
				rangeStr = str(lowRange)
			print rangeStr + ' ' + text

#roll number d size dice
def dice(number, size):
	total = 0
	for i in range(number):
		total += random.randint(1, size)
	return total

#roll 4d6 drop lowest
def statRoll():
	allDice = [dice(1, 6), dice(1, 6), dice(1, 6), dice(1, 6)]
	allDice.sort()
	allDice.pop(0)
	return sum(allDice)

#convert ability score to ability score modifier
def statToModifier(s):
	negative = s < 10
	if negative:
		s -= 1
	difference = abs(s-10)
	modifier = difference/2
	if negative:
		modifier *= -1
	return modifier

#stat priorities are stored by class in text files
#evenly prioritized stats are separated by a / and randomly prioritized
#decisions between stats can also be determined with ?, ignore the others
def getPrioritizedStats(className):
	unprioritizedStats = [statRoll(), statRoll(), statRoll(), statRoll(), statRoll(), statRoll()]
	unprioritizedStats.sort(reverse=True)
	statPriorities = getFileLines('stat priorities/'+className+'.txt')
	prioritizedStats = [None, None, None, None, None, None]
	for priority in statPriorities:
		decisions = priority.split('?')
		random.shuffle(decisions)
		statList = decisions[0].split('/')
		random.shuffle(statList)
		for stat in statList:
			number = statToNumber[stat]
			if prioritizedStats[number] is None:
				prioritizedStats[number] = unprioritizedStats.pop(0)
	return prioritizedStats

#map ability score to position in stat array
statToNumber = {'STR':0,'DEX':1,'CON':2,'INT':3,'WIS':4,'CHA':5}

#Get class and subclass
playerClass = Table('class').roll()
subClass = Table('subclasses/'+playerClass).roll()
#Get stats
playerStats = getPrioritizedStats(playerClass)
#Get race and subrace
if weightedRaces:
	race = Table('races weighted').roll()
else:
	race = Table('race').roll()
if race == "Other":
	race = Table('other races').roll()
if race in getList('races with subraces'):
	race = Table('subraces/'+race).roll()
#Get alignment
alignment = Table('alignment').roll()
#Get gender
gender = Table('gender').roll()
#Get background
background = Table('background').roll()

#Print
statStr = ''
for stat in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
	statNum = playerStats[statToNumber[stat]]
	statModifier = statToModifier(statNum)
	statStr += ' ' + stat + ': ' + str(statNum) + '('
	if statModifier > 0:
		statStr += '+'
	statStr += str(statModifier) + ')'
print 'Rolled stat array: '
print statStr[1:]
print 'Gender: ' + gender
print 'Race: ' + race
print 'Class: ' + playerClass + ' - ' + subClass
print 'Background: ' + background
print 'Alignment: ' + alignment