from ..langDefaults import LangDefaults
from .freqMaps import freqMapFemale, freqMapMale, freqMapFamily, freqMapOrg, freqMapStreet, freqMapCity
from .dateFormats import dateStdFormat, dateFormatsAlpha, dateFormatsNr, dateReplMonths, DateParserInfo
from collections import defaultdict, OrderedDict
import json, os
import Levenshtein
import re
from .spacyNlp import SpacyNlp
from random import choice

'''
German handling for language-dependent entities
'''
class German(LangDefaults):
    
    def __init__(self):  
        '''
        required
        '''     
        # date related stuff
        self.dateParserInfo = DateParserInfo(dayfirst=True,yearfirst=False)
        self.dateStdFormat = dateStdFormat
        self.dateFormatsAlpha = dateFormatsAlpha
        self.dateFormatsNr = dateFormatsNr
        self.dateReplMonths = dateReplMonths
        
        # substitute lists
        # given names
        self.female = json.load(open(os.path.join(os.path.dirname(__file__), 'subLists', 'female.json'),'r'))
        self.male = json.load(open(os.path.join(os.path.dirname(__file__), 'subLists', 'male.json'),'r'))
        # family names
        self.family = json.load(open(os.path.join(os.path.dirname(__file__), 'subLists', 'family.json'),'r'))
        # street names
        self.street = json.load(open(os.path.join(os.path.dirname(__file__), 'subLists', 'street.json'),'r'))
        # city names (we distinguish by country, only self.city without any country differentiation required)

        import zipfile
        with zipfile.ZipFile('city_rec.zip', 'r') as zip_ref:
            zip_ref.extractall('')

        self.citySub = json.load(open(os.path.join(os.path.dirname(__file__), 'subLists', 'city.json'),'r'))
        self.city = self.citySub['XX']
        # city names for look up
        self.cityLookUp = {country:{k:set(v) for k,v in subList.items()} for country, subList in json.load(open(os.path.join(os.path.dirname(__file__), 'subLists', 'city_rec.json'),'r')).items()}

        # org names
        self.org = json.load(open(os.path.join(os.path.dirname(__file__), 'subLists', 'org.json'),'r'))
        
        
        '''
        optional
        '''
        # given names with nicknames
        self.femaleNick = {k:set(v) for k,v in json.load(open(os.path.join(os.path.dirname(__file__), 'subLists', 'female_nick.json'),'r')).items()}
        self.maleNick = {k:set(v) for k,v in json.load(open(os.path.join(os.path.dirname(__file__), 'subLists', 'male_nick.json'),'r')).items()}
        
        # frequency dependent first letter mappings (if not set default values are taken)
        self.freqMapFemale = freqMapFemale
        self.freqMapMale = freqMapMale
        self.freqMapFamily = freqMapFamily
        self.freqMapOrg = freqMapOrg
        self.freqMapStreet = freqMapStreet
        self.freqMapCity = freqMapCity
        
        # helpers for extensional functions
        self._spacyNlp = SpacyNlp()
        self._locDerivSuffixes = OrderedDict({'er':['','er','e','en', 'ern'],'erer':['ern'], 'eler':['eln'],'aner':['er',''],'enser':['e','a'],'usser':['us'],'ner':['en']})
        self._locDerivSuffixesIsch = ['','ien', 'en']
        self._locRegDerivIsch = re.compile('(er|r)?(isch(e[n|s|r|m]?)?)$')
        self._locRegDerivSch = re.compile('(sch(e[n|s|r|m]?)?)$')
        self._locRegDerivEr = re.compile('(er|ers|ern|erin|erinnen)$')
        self._subUmlaut = {'ä':'a','ö':'o','ü':'u', 'äu':'au'}     
        self._strAbbr = {'straße':['str','str.'],'str.':['straße', 'str'],'str':['straße', 'str.'],'platz':['pl','pl.'],'pl.':['platz','pl.'], 'pl':['platz','pl'],
                        'Straße':['Str','Str.'],'Str.':['Straße', 'Str'],'Str':['Straße', 'Str.'],'Platz':['Pl','Pl.'],'Pl.':['Platz','Pl.'], 'Pl':['Platz','Pl']} 
        self._strReg = re.compile('('+'|'.join([re.escape(k) for k in self._strAbbr])+')$')
        self._appOrg = re.compile('('+'|'.join([re.escape(k) for k in ['GmbH','AG','OG','KG','e.V.','e. V.','Unternehmen']])+')$')

        self._heightWeightReg = re.compile('[0-9]+')
        self._heightRegComma = re.compile('[0-9](,|\.)[0-9]+')

    '''
    optional: extensional functions
    '''
    
    # substitute female names     
    def subFemale(self, sgFile, token):
        return self._subGiven(sgFile, token, self.female, self.femaleNick) or self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.female)
    
    # substitute male names 
    def subMale(self, sgFile, token):
        return self._subGiven(sgFile, token, self.male, self.maleNick) or self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.male)

    # substitute family names     
    def subFamily(self, sgFile, token):
        return self._subFamily(sgFile, token) or self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.family)

    # substitute organizations     
    def subOrg(self, sgFile, token):
        return self._subOrg(sgFile, token) or self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.org)
    
    # substitute street names 
    def subStreet(self, sgFile, token):
        return self._subStreet(sgFile, token) or self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.street)
    
    # substitute city names 
    def subCity(self, sgFile, token):
        return self._subCity(sgFile, token) or self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.city)
    
    
    # for given names nicknames are resolved if possible, genitive is checked and for given names without determiner also generated
    # no plural processing
    def _subGiven(self, sgFile, token, lex, lexNick):        
        tokenSpacy = self._spacyNlp.getSpacyToken(sgFile, token.start, token.end)
        if tokenSpacy.dep in sgFile.genitive and ((token.normCase[-1] == 's') or token.normCase[-2:] in ["s'","z'","x'","ß'"] or token.normCase[-3:] in ["ce'","se'"]):
            newToken = self._getNicknames(sgFile, token.normCase[:-1], token.label, lexNick)
            if newToken:
                if tokenSpacy.left_edge.pos != sgFile.det:
                    sgFile.addSpellings(token.text[:-1], newToken, token.normCase[:1], newToken, token.label)
                    if tokenSpacy.left_edge.pos != sgFile.det:
                        newToken = self._generateGenitiveEnding(newToken)
                        sgFile.addSpellings(token.text, newToken, token.normCase, newToken, token.label)
                    return sgFile.sub[token.label][token.text]
            else:
                if tokenSpacy.left_edge.pos != sgFile.det:
                    return self._getGenitiveNames(sgFile, token.text, token.text[:-1], token.normCase, token.normCase[:1], token.label, lex)
                else:
                    return sgFile.sub[token.label].get(token.text[:-1]) or sgFile.sub[token.label].get(token.normCase[:1])
        else:
            return self._getNicknames(sgFile, token.normCase, token.label, lexNick)      
      
    # for family names genitive case is checked and for family names without determiner also generated
    # no plural processing
    def _subFamily(self, sgFile, token):
        tokenSpacy = self._spacyNlp.getSpacyToken(sgFile, token.start, token.end)
        if tokenSpacy.dep in sgFile.genitive and ((token.normCase[-1] == 's') or token.normCase[-2:] in ["s'","z'","x'","ß'"] or token.normCase[-3:] in ["ce'","se'"]):
            if tokenSpacy.left_edge.pos != sgFile.det:
                return self._getGenitiveNames(sgFile, token.text, token.text[:-1], token.normCase, token.normCase[:-1], token.label, self.family)
            else: 
                return sgFile.sub[token.label].get(token.text[:-1]) or sgFile.sub[token.label].get(token.normCase[:1])
                
    
    # for organizations check genitive singular and dativ plural are checked, genitive singular is generated for organizations without determiner
    def _subOrg(self, sgFile, token):    
        match = self._appOrg.search(token.normCase, re.IGNORECASE)
        if match:
            tok = token.normCase[:match.start()].rstrip()
            if tok in sgFile.sub[token.label]:
                return sgFile.sub[token.label].get(token.text[:match.start()].rstrip()) or sgFile.sub[token.label].get(tok) 
        tokenSpacy = self._spacyNlp.getSpacyToken(sgFile, token.start, token.end)               
        if tokenSpacy.head.tag == sgFile.apprart or any(child.pos in sgFile.artWords for child in tokenSpacy.lefts):
            if (tokenSpacy.dep in sgFile.genitive and token.normCase[-1] == 's'):
                return sgFile.sub[token.label].get(token.text[:-1]) or sgFile.sub[token.label].get(token.normCase[:1])
            elif tokenSpacy.dep == sgFile.dative and re.search('(en|ern|eln)$', token.normCase):
                newToken = sgFile.sub[token.label].get(token.text[:-1]) or sgFile.sub[token.label].get(token.normCase[:1])
                if newToken:
                    return newToken
                else:
                    newToken = self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.org) 
                    sgFile.addSpellings(token.text[:-1], newToken, token.normCase[:-1], newToken, token.label)   
                    return sgFile.sub[token.label][token.text]     
        elif tokenSpacy.dep in sgFile.genitive and (token.normCase[-1] == 's'): 
            return self._getGenitiveNames(sgFile, token.text, token.text[:-1], token.normCase, token.normCase[:1], token.label, self.org)
        elif tokenSpacy.dep == sgFile.dative and re.search('(en|ern|eln)$', token.normCase):
            newToken = sgFile.sub[token.label].get(token.text[:-1]) or sgFile.sub[token.label].get(token.normCase[:1])  
            if newToken:
                return newToken
            else:
                newToken = self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.org) 
                sgFile.addSpellings(token.text[:-1], newToken, token.normCase[:-1], newToken, token.label)   
                return sgFile.sub[token.label][token.text]

    # for street names abbreviations str. and pl. are handled
    def _subStreet(self, sgFile, token):
        match = self._strReg.search(token.normCase)
        if match:
            for partNorm in self._strAbbr[match.group()]:
                tok = token.normCase[:match.start()]+partNorm
                if tok in sgFile.sub[token.label]:
                    part = ''.join([self._getProperCaseChar(char.isupper(), char) for char in partNorm])
                    return sgFile.sub[token.label].get(token.text[:match.start()]+part) or sgFile.sub[token.label].get(tok)      
    
    # handles derivations of city, town and region names
    # entities with determiner with genitive checking, without determiner (presumption: neuter) with genitive checking and generation
    # no generation or checking of dative plural (should be rare)
    def _subCity(self, sgFile, token):
        tokenSpacy = self._spacyNlp.getSpacyToken(sgFile, token.start, token.end)   
        if tokenSpacy.head.tag == sgFile.apprart or any(child.pos in sgFile.artWords for child in tokenSpacy.lefts):
            if tokenSpacy.dep in sgFile.genitive and (token.normCase[-1] == 's'):
                if token.normCase[:-1] in sgFile.sub[token.label]:
                    return sgFile.sub[token.label].get(token.text[:-1]) or sgFile.sub[token.label].get(token.normCase[:1])
                else:         
                    lexCountry = self._getProperCountryLex(token.normCase[:-1]) or self._getProperCountryLex(token.normCase)    
                    return self.getSurrogateName(sgFile, token.text, token.normCase, token.label, lexCountry) if lexCountry else self._getDerivateCity(sgFile, token)
            else:
                lexCountry = self._getProperCountryLex(token.normCase) 
                return self.getSurrogateName(sgFile, token.text, token.normCase, token.label, lexCountry) if lexCountry else self._getDerivateCity(sgFile, token)
        elif tokenSpacy.dep in sgFile.genitive and (token.normCase[-1] == 's'):
            if token.normCase[:-1] in sgFile.sub[token.label]:
                newToken = self._generateGenitiveEnding(sgFile.sub[token.label].get(token.text[:-1]) or sgFile.sub[token.label].get(token.normCase[:-1]))
                sgFile.addSpellings(token.text, newToken, token.normCase, self.normalizeTokenCase(newToken), token.label)
                return sgFile.sub[token.label][token.text] 
            else:
                lexCountry = self._getProperCountryLex(token.normCase[:-1])
                return self._getGenitiveCity(sgFile, token.text, token.text[:-1], token.normCase, token.normCase[:1], token.label, lexCountry) if lexCountry else self._getDerivateCity(sgFile, token)
        else:
            lexCountry = self._getProperCountryLex(token.normCase)
            return self.getSurrogateName(sgFile, token.text, token.normCase, token.label, lexCountry) if lexCountry else self._getDerivateCity(sgFile, token)
    
    '''
    Functions for inflection and derivation
    '''
    # handle standard cases of genitive singular
    def _getGenitiveNames(self, sgFile, token, tokenStem, tokenNormCase, tokenStemNormCase, label, lex):        
        if tokenStemNormCase in sgFile.sub[label]:    
            newToken = self._generateGenitiveEnding(sgFile.sub[label].get(tokenStem) or sgFile.sub[label].get(tokenStemNormCase))
            sgFile.addSpellings(token, newToken, tokenNormCase, self.normalizeTokenCase(newToken), label)            
            return sgFile.sub[label][token]                   
        else:
            newToken = self.getSurrogateName(sgFile, tokenStem, tokenStemNormCase, label, lex)
            newToken = self._generateGenitiveEnding(newToken)
            sgFile.addSpellings(token, newToken, tokenNormCase, newToken, label)
            return sgFile.sub[label][token]
    
    # handle genitive singular for CITY
    def _getGenitiveCity(self, sgFile, token, tokenStem, tokenNormCase, tokenStemNormCase, label, lex):
        newToken = self.getSurrogateName(sgFile, tokenStem, tokenStemNormCase, label, lex)
        newToken = self._generateGenitiveEnding(newToken)
        sgFile.addSpellings(token, newToken, tokenNormCase, newToken, label)
        return sgFile.sub[label][token]    
    
    # handle adjectivized toponyms and signifying inhabitants
    def _getDerivateCity(self, sgFile, token):
        matchAdj = self._locRegDerivIsch.search(token.normCase) # adjectivized toponyms with -isch (incl substantivated adj)
        matchAdjSch = self._locRegDerivSch.search(token.normCase) # adjectivized toponyms with -sch (incl substantivated adj)
        matchSub = self._locRegDerivEr.search(token.normCase) # adjectivized toponyms with -er and signifying inhabitants with -er
        if matchAdj:
            if matchAdj.group(1):
                return self._derivateStem(sgFile, token, matchSub = matchAdj.group(1), matchAdj = matchAdj.group(2))
            else:
                return self._derivateStem(sgFile, token, matchAdj = matchAdj.group(2))
        elif matchAdjSch:
            return self._derivateStem(sgFile, token, matchAdj = matchAdjSch.group(1))
        elif matchSub:
            return self._derivateStem(sgFile, token, matchSub = matchSub.group())
            
    # get derivation with checking if stem already substituted and generate possible lemmas
    def _derivateStem(self, sgFile, token, matchSub = '', matchAdj = ''):
        tokenStemNormCase = token.normCase[:len(token.normCase)-len(matchSub)-len(matchAdj)]  
        if tokenStemNormCase in sgFile.sub[token.label]:
            newToken = sgFile.sub[token.label][token.text[:len(token.text)-len(matchSub)-len(matchAdj)]] or sgFile.sub[token.label][tokenStemNormCase] 
            newToken = self._generateDerivateCity(newToken, token.text[len(token.text)-len(matchSub)-len(matchAdj):len(token.text)-len(matchAdj)], token.text[len(token.text)-len(matchAdj):])
            sgFile.addSpellings(token.text, newToken, token.normCase, newToken, token.label)
            return newToken    
        lemmaOrig = self._getPossibleLemmasLevenshteinBased(token.normCase[:len(token.normCase)-len(matchSub)-len(matchAdj)], sgFile.sub[token.label].keys())
        if lemmaOrig:
            newToken = self._generateDerivateCity(sgFile.sub[token.label][lemmaOrig], token.text[len(token.text)-len(matchSub)-len(matchAdj):len(token.text)-len(matchAdj)], token.text[len(token.text)-len(matchAdj):])
            sgFile.addSpellings(token.text, newToken, token.normCase, newToken, token.label)
            return sgFile.sub[token.label][token.text]
        if token.normCase[0] in self.city:
            lemmas = self._getPossiblelemmasRuleBased(token.normCase, matchSub, matchAdj)
            if lemmas:
                newToken = self.getSurrogateName(sgFile, token.text, token.normCase, token.label, self.city)
                for lemma in lemmas:
                    sgFile.addSpellings(lemma, newToken, lemma, newToken, token.label)
                newToken = self._generateDerivateCity(newToken, token.text[len(token.text)-len(matchSub)-len(matchAdj):len(token.text)-len(matchAdj)], token.text[len(token.text)-len(matchAdj):])
                sgFile.addSpellings(token.text, newToken, token.normCase, newToken, token.label)
                return sgFile.sub[token.label][token.text]
    
    '''
    Generator functions
    '''
    # get inflectional morpheme for genitive case
    def _generateGenitiveEnding(self, token):
        return token + "'" if token[-1].lower() in ["s","z","x","ß"] else token + self._getProperCaseChar(token.isupper(), 's')
    
    # generate derivational morpheme for CITY (standard -er, -ingen, -stadt, -land, -e, also handled)
    def _generateDerivateCity(self, token, matchSub, matchAdj):
        matchSub = re.sub('^(er|r)', '', matchSub)
        if matchAdj[:3] == 'sch':
            matchAdj = 'i' + matchAdj
        
        if token[-5:] == 'ingen':
            return token[:-2] + 'er' + matchSub + matchAdj
        elif token[-5:] == 'stadt':
            return token[:-5] + 'städter' + matchSub + matchAdj
        elif token[-4:] == 'land':
            return token[:-4] + 'länder' + matchSub + matchAdj
        elif token[-1] == 'e':
            return token + 'r' + matchSub + matchAdj
        else:
            return token + 'er' + matchSub + matchAdj
    
    '''
    Helper functions
    '''    
    # get possible lemmas of token
    def _getPossiblelemmasRuleBased(self, tokenNormCase, matchSub, matchAdj):
        lemmas = []
        if matchAdj and not matchSub:
            token = tokenNormCase[:len(tokenNormCase)-len(matchAdj)]
            match = re.search('(äu|ä|ü|ö)([bcdfghjklmnpqrstvwxyzß])*$', token)
            if match:
                tokenUml = token[:match.start()] + self._subUmlaut[match.group(1)]+token[match.end(1):]
            else:
                tokenUml = ''
            for suffix in self._locDerivSuffixesIsch:
                lemmas.append(token+suffix)
                if tokenUml:
                    lemmas.append(tokenUml+suffix)
            return [lemma for lemma in lemmas if lemma in self.city[tokenNormCase[0]]]
        else:
            token = tokenNormCase[:len(tokenNormCase)-len(matchAdj)-len(matchSub)+2]
            for suffix, subs in self._locDerivSuffixes.items():
                if suffix == token[-len(suffix):]:
                    if suffix in ('er','ner'):
                        match = re.search('(äu|ä|ü|ö)([bcdfghjklmnpqrstvwxyzß])*$', token[:-2])
                        if match:                    
                            for sub in subs:
                                lemmas.append(token[:match.start()]+self._subUmlaut[match.group(1)]+token[match.end(1):-len(suffix)]+sub) 
                    for sub in subs:
                        lemmas.append(token[:-len(suffix)]+sub)                    
            return [lemma for lemma in lemmas if lemma in self.city[tokenNormCase[0]]]   
        
    # check for similar words with the same first character and levenshtein distance < 1 in already generated surrogates, if there are more matches take shortest
    def _getPossibleLemmasLevenshteinBased(self, tokenStem, surrogates):
        lowestLevDist = 2
        bestMatchLemma = ''
        for token in surrogates:
            distance = Levenshtein.distance(token[:len(tokenStem)], tokenStem)
            if distance<lowestLevDist or(distance==lowestLevDist and len(token) < len(bestMatchLemma)):
                bestMatchLemma = token
                lowestLevDist = distance
        return bestMatchLemma
                
    # substitute given name with substitute of nickname or substitute of name if it has already been substituted     
    def _getNicknames(self, sgFile, tokenNormCase, label, nicknames):
        names = [name for name in nicknames.get(tokenNormCase, []) if name in sgFile.sub[label]]
        return sgFile.sub[label][choice(names)] if names else None
    
    # get lexicon of country where token is found 
    def _getProperCountryLex(self, token):
        for key in ['AT','CH','DE','XX']:
            if token[0] in self.cityLookUp[key] and token in self.cityLookUp[key][token[0]]:
                return self.citySub[key]            
           
    # get proper case for character (f.e. derivational or inflectional suffix)
    def _getProperCaseChar(self, boolVar, char):
        return char.upper() if boolVar else char
    
    
    
__all__ = ["German"]
