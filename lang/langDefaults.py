from string import ascii_uppercase
import re, math
from random import choice
from collections import defaultdict
from datetime import datetime, timedelta
import dateutil.parser

'''
default handling of language-dependent entities 
'''
class LangDefaults():
    
    def __init__(self):
        self.freqMapFemale = [(ascii_uppercase, ascii_uppercase)]
        self.freqMapMale = [(ascii_uppercase, ascii_uppercase)]
        self.freqMapFamily = [(ascii_uppercase, ascii_uppercase)]
        self.freqMapOrg = [(ascii_uppercase, ascii_uppercase)]
        self.freqMapStreet = [(ascii_uppercase, ascii_uppercase)]
        self.freqMapCity = [(ascii_uppercase, ascii_uppercase)]
        
        self._heightWeightReg = re.compile('[0-9]+')
        self._heightRegComma = re.compile('[0-9](,|\.)[0-9]+')

    # substitute female names 
    def subFemale(self, sgFile, token):
        return self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.female) 

    # substitute male names 
    def subMale(self, sgFile, token):
        return self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.male) 

    # substitute family names     
    def subFamily(self, sgFile, token):
        return self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.family) 

    # substitute organizations     
    def subOrg(self, sgFile, token):
        return self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.org) 

    # substitute street names     
    def subStreet(self, sgFile, token):
        return self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.street) 

    # substitute city names     
    def subCity(self, sgFile, token):
        return self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.city) 

    # substitute dates
    def subDate(self, sgFile, token):
        try:
            tokenPars = dateutil.parser.parse(re.sub('\.(?=\w)','. ',token.text), parserinfo=self.dateParserInfo)
            newTokenPars = tokenPars + timedelta(days=sgFile.dateShift)
        except:
            return self.getRandomDate(sgFile, token)
        else:
            newToken = re.findall('\W+|\w+', token.text)
            parts = re.findall('\w+', token.text)
            if re.search('[a-zA-Z]+', token.text):
                month = datetime.strftime(tokenPars, '%B')
                for form in self.dateFormatsAlpha:
                    try:
                        partsPars = datetime.strftime(tokenPars, form)
                        idxMonth = [i for i, form in enumerate(self.dateReplMonths[month]) if parts==re.findall('\w+', re.sub(month, form, partsPars))]
                        if idxMonth:
                            newMonth = datetime.strftime(newTokenPars, '%B')
                            if len(self.dateReplMonths[newMonth])>idxMonth[0]:
                                newPartsPars = re.findall('\w+', re.sub(newMonth, self.dateReplMonths[newMonth][idxMonth[0]], datetime.strftime(newTokenPars, form)))
                            else:
                                newPartsPars = re.findall('\w+', re.sub(newMonth, self.dateReplMonths[newMonth][0], datetime.strftime(newTokenPars, form)))
                            c = 0
                            for i, part in enumerate(newToken):
                                if part.isalnum():
                                    newToken[i] = newPartsPars[c]
                                    c+=1                                
                            newToken = ''.join(newToken)
                            sgFile.addSpellings(token.text, newToken, token.normCase, self.normalizeTokenCase(newToken), token.label)
                            return sgFile.sub[token.label][token.text]
                    except:
                        continue
                return self.getRandomDate(sgFile, token)
            else:
                for form in self.dateFormatsNr:
                    try:
                        partsPars = re.findall('\w+', datetime.strftime(tokenPars, form))
                        if partsPars == parts:
                            newPartsPars = re.findall('\w+', datetime.strftime(newTokenPars, form))
                            c = 0
                            for i, part in enumerate(newToken):
                                if part.isdigit():
                                    newToken[i] = newPartsPars[c]
                                    c+=1
                            newToken = ''.join(newToken)
                            sgFile.sub[token.label][token.text] = newToken
                            return newToken
                    except:
                        continue
                return self.getRandomDate(sgFile, token)  
                       
    # substitute ages
    def subAge(self, sgFile, token):
        match = self._heightWeightReg.search(token.text)
        if match:
            age = int(match.group())
            if age > 89:
                return str(89)
                #return str(age+1) if sgFile.dateShift > 180 else str(age-1) if sgFile.dateShift < -180 else str(age)
   
    # substitute height 
    def subHeight(self, sgFile, token):
        match = self._heightRegComma.search(token.text) # height in meters with comma
        if match:
            try:
                height = float(match.group())
                if 40 > height > 1.90:
                    return '{}{}{}'.format(
                        token.text[:match.start()],
                        1.90,
                        token.text[match.end():])  
            except:
                height = float(re.sub(',', '.', match.group()))
                if 40 > height > 1.90:
                    return '{}{}{}'.format(
                        token.text[:match.start()],
                        '1,90',
                        token.text[match.end():])    
                #try:
                    #return '{}{}{}'.format(
                        #token.text[:match.start()],
                        #round(math.sqrt(math.pow(float(match.group()),2) * sgFile.weightHeightShift),2),
                        #token.text[match.end():])  
                #except:
                    #return '{}{}{}'.format(
                        #token.text[:match.start()],
                        #re.sub('.',',',str(round(math.sqrt(math.pow(float(re.sub(',','.', match.group())),2) * sgFile.weightHeightShift),2))),
                        #token.text[match.end():])             

        else:
            match = self._heightWeightReg.search(token.text) # height in centimeters or 2m
            if match:
                height = int(match.group())
                if len(match.group())== 1 and height > 1.9: # 2m
                    return '{}{}{}'.format(
                        token.text[:match.start()],
                        1.9,
                        token.text[match.end():])               
                elif height > 190:
                    return '{}{}{}'.format(
                        token.text[:match.start()],
                        190,
                        token.text[match.end():])      
                    
                #return '{}{}{}'.format(
                    #token.text[:match.start()],
                    #round(math.sqrt(math.pow(int(match.group()),2) * sgFile.weightHeightShift)),
                    #token.text[match.end():])             

    # substitute weight     
    def subWeight(self, sgFile, token): 
        match = self._heightWeightReg.search(token.text)
        if match:
            weight = int(match.group())
            if 1000 > weight > 150: # to prevent replacement of g (for babies)
                return '{}{}{}'.format(
                    token.text[:match.start()],
                    150,
                    token.text[match.end():])                 
            #return '{}{}{}'.format(
                #token.text[:match.start()],
                #round(int(match.group()) * sgFile.weightHeightShift),
                #token.text[match.end():]) 
    
    # get surrogate name 
    def getSurrogateName(self, sgFile, token, tokenNormCase, label, lex):
        newToken = choice(lex[sgFile.getMapForChar(label, token[0].upper(), lex)])
        sgFile.addSpellings(token, newToken, tokenNormCase, self.normalizeTokenCase(newToken), label)
        return sgFile.sub[label][token] 

    # get surrogate for abbreviations
    def getSurrogateAbbreviation(self, sgFile, token, label, lex):
        if (len(token) == 1):
            newToken = sgFile.getMapForChar(label, token[0].upper(), lex)
            sgFile.sub[label][token] = newToken.lower() if token.islower() else newToken
            return sgFile.sub[label][token]
        elif token[-1] == '.' and len(token)<=4:
            newToken = sgFile.getMapForChar(label, token[0].upper(), lex) + '.'  
            sgFile.sub[label][token] = newToken.lower() if token.islower() else newToken
            return sgFile.sub[label][token]
    
    # get same substitute for same entity in file
    def getCoSurrogate(self, sgFile, token):
        token.setNormCase(self.normalizeTokenCase(token.text))
        return sgFile.sub[token.label].get(token.text) or sgFile.sub[token.label].get(token.normCase)
    
    # generate random date
    def getRandomDate(self, sgFile, token): 
        surrogate = datetime.today()+timedelta(days=sgFile.dateShift)
        surrogate = surrogate.strftime(self.dateStdFormat)
        sgFile.sub[token.label][token.text] = surrogate
        return surrogate

    # get case normalized token (standard title case) 
    def normalizeTokenCase(self, token):
        return ''.join(t[0].upper()+t[1:].lower() for t in re.findall('\W+|\w+',token))
    
    # read in substitute lists that are provided in a file with one entry per line 
    def readSubstituteLists(self, lexicon):
        names = defaultdict(list)
        for line in open(lexicon):
            names[line[0].upper()].append(line.rstrip())
        return names
