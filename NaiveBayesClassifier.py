from __future__ import division
import math
import time
import sys

class Scrapers:

    uselessWords = ['the', 'is', 'a', "I'm", 'here', 'to', 'and', 'of', 'in',
                    'it', 'i', 'that', 'this', 'as', 'with', 'was', 'for', 'but', 'film', 'movie', 'on', 'his', 'are',
                    'you', 'her', 'they',
                    'he', 'her', 'have', 'be', 'one', 'all', 'at', 'so', 'like', 'by', 'an', 'who', 'what', 'when',
                    'where', 'why', 'from',
                    'has']

    noNeedSymbols = ['<br />','.','!','?','>','<','"',',','(',')','&',':','-','=','\\','/']

    numOfPosDocs = 0
    numOfNegDocs = 0

    def __init__(self, filename):
        self.file = open(filename, 'r')

    def is_positive_review(self, theString):
        if theString[-1] == '1':
            return True
        elif theString[-1] == '0':
            return False
        elif theString[-2] == '1':
            return True
        elif theString[-2] == '0':
            return False

    def sentence_pre_process(self, sentence):
        for symbol in self.noNeedSymbols:
            if symbol in sentence:
                sentence = sentence.replace(symbol," ")
        return sentence


class BuildSet(Scrapers):

    def __init__(self, filename):
        Scrapers.__init__(self, filename)
        self.posWords = {}
        self.negWords = {}

    def add_to_dict(self, theWord, theDict):
        theWord = theWord.lower()
        if len(theWord) != 0:
            if theWord not in self.uselessWords:
                if theWord != '1' and theWord != '0':
                    if theWord not in theDict:
                        theDict[theWord] = 1
                    elif theWord in theDict:
                        theDict[theWord]+=1

    def build_set(self):
        with self.file as f:
            for line in f:
                line = self.sentence_pre_process(line)
                if self.is_positive_review(line):
                    # self.countTrue +=1
                    self.numOfPosDocs+=1
                    # print "Positive review"
                    for word in line.split():
                        self.add_to_dict(word,self.posWords)
                else:
                    # self.countFalse+=1
                    self.numOfNegDocs+=1
                    for word in line.split():
                        self.add_to_dict(word, self.negWords)
                    # print "Negative review"




class Document:

    uselessWords = ['the', 'is', 'a', "I'm", 'here', 'to', 'and', 'of', 'in',
                    'it', 'i', 'that', 'this', 'as', 'with', 'was', 'for', 'but', 'film', 'movie', 'on', 'his', 'are',
                    'you', 'her', 'they',
                    'he', 'her', 'have', 'be', 'one', 'all', 'at', 'so', 'like', 'by', 'an', 'who', 'what', 'when',
                    'where', 'why', 'from',
                    'has']

    def __init__(self, theDoc, value, posWords, negWords, numPosDocs, numNegDocs):
        self.positWords = posWords
        self.negitWords = negWords
        self.numPosDocs = numPosDocs
        self.numNegDocs = numNegDocs
        self.totalNumWords = len(posWords) + len(negWords)
        self.doc = theDoc
        self.wordList = {}
        self.calculatedValue = None
        self.actualValue = value

    def add_to_dict(self, theWord):
        theWord = theWord.lower()
        if len(theWord) != 0:
            if theWord not in self.uselessWords:
                if theWord != '1' and theWord != '0':
                    if theWord not in self.wordList:
                        self.wordList[theWord] = 1
                    elif theWord in self.wordList:
                        self.wordList[theWord] += 1

    # def calculate_score(self, theDict, classSize):
    #     scores = []
    #     total = 1
    #
    #     for key, value in self.wordList.iteritems():
    #         if key in theDict:
    #             scores.append((theDict[key] + 1) / (classSize + self.totalNumWords))
    #             # scores.append(theDict[key]+1/(classSize + self.totalNumWords))
    #         else:
    #             scores.append(1/(classSize + self.totalNumWords))
    #     for data in scores:
    #         total = total * data
    #     return total * 0.5

    def calculate_score(self, theDict, classSize, whichSet):
        scores = []
        total = 0

        for key, value in self.wordList.iteritems():
            if key in theDict:
                scores.append((theDict[key] + 1) / (classSize + self.totalNumWords))
            else:
                scores.append(1 / (classSize + self.totalNumWords))
        for data in scores:
            total = total + math.log(data)

        if whichSet:
            return total + math.log(self.numPosDocs/(self.numPosDocs+self.numNegDocs))
        else:
            return total + math.log(self.numNegDocs/(self.numPosDocs+self.numNegDocs))

    def set_calculated_value(self):
        positive = self.calculate_score(self.positWords, len(self.positWords), True)
        negative = self.calculate_score(self.negitWords, len(self.negitWords), False)
        # made change here by going from pos>neg to pos>=neg
        if positive >= negative:
            self.calculatedValue = 1
        else:
            self.calculatedValue = 0

    def create_word_list(self):
        for word in self.doc:
            self.add_to_dict(word)


class Classifier(Scrapers):

    def __init__(self, filename, posWords, negWords, posNum, negNum, toPrint):
        Scrapers.__init__(self, filename)
        self.documentList = []
        self.results = []
        self.posiWords = posWords
        self.negiWords = negWords
        self.numberOfPosDocs = posNum
        self.numberOfNegDocs = negNum
        self.accuracy = None
        self.doPrint = toPrint

    def printOutResult(self):
        if self.doPrint:
            for i in range(len(self.documentList)):
                print str(self.documentList[i].calculatedValue)

    def main(self):
        with self.file as f:
            for line in f:
                line = self.sentence_pre_process(line)
                if self.is_positive_review(line):
                    document = Document(line.split(),1, self.posiWords, self.negiWords, self.numberOfPosDocs, self.numberOfNegDocs)
                    # calculate score of document
                    document.create_word_list()
                    document.set_calculated_value()
                    self.results.append(1)
                else:
                    document = Document(line.split(),0, self.posiWords, self.negiWords, self.numberOfPosDocs, self.numberOfNegDocs)
                    # calculate score of document
                    document.create_word_list()
                    document.set_calculated_value()
                    self.results.append(0)
                self.documentList.append(document)

        same = 0
        for i in range(len(self.documentList)):
            if self.documentList[i].calculatedValue == self.results[i]:
                same += 1
        self.accuracy = same/len(self.documentList)
        # print(self.accuracy)




trainStart = time.time()
bayes = BuildSet(sys.argv[1])
bayes.build_set()
trainEnd = time.time()
labelStart = time.time()
testing = Classifier(sys.argv[2], bayes.posWords, bayes.negWords, bayes.numOfPosDocs, bayes.numOfNegDocs, True)
testing.main()
labelEnd = time.time()
training = Classifier(sys.argv[1], bayes.posWords, bayes.negWords, bayes.numOfPosDocs, bayes.numOfNegDocs, False)
training.main()
testing.printOutResult()
print "{:g}".format(round(trainEnd-trainStart)) + " seconds (training)"
print "{:g}".format(round(labelEnd-labelStart)) + " seconds (labeling)"
print str(training.accuracy) + " (training)"
print str(testing.accuracy) + " (testing)"






