import spacy
    
'''
spacy tokenizer and parser
'''
class SpacyNlp:
    
    def __init__(self):
        self.nlp = spacy.load('de_core_news_sm', disable=['ner'])
    
    # process text with spacy
    def getSpacyDoc(self, sgFile):
        sgFile.doc = self.nlp(sgFile.txt)
        sgFile.det = sgFile.doc.vocab.strings.add('DET')
        sgFile.artWords = set([sgFile.doc.vocab.strings.add('ADJ'),sgFile.det])
        sgFile.apprart = sgFile.doc.vocab.strings.add('APPRART')
        sgFile.genitive = set([sgFile.doc.vocab.strings.add(label) for label in ('ag','og')]) 
        sgFile.dative = sgFile.doc.vocab.strings.add('da') 
    
       
    # get spacy token by indices and merge tokens if necessary
    def getSpacyToken(self, sgFile, start, end):
        if not sgFile.doc:
            self.getSpacyDoc(sgFile)
        span = sgFile.doc.char_span(start, end)
        if span:
            if len(span) > 1:
                with sgFile.doc.retokenize() as retokenizer:
                    retokenizer.merge(span)
            return sgFile.doc[span.start]        
        else:          
            for token in sgFile.doc:
                if start >= token.idx:
                    if end <= token.idx+len(token):
                        return token
                    else:
                        startSpan = token.i
                        for tokenEnd in sgFile.doc[token.i+1:]:
                            if end <= tokenEnd.idx+len(tokenEnd):
                                endSpan = tokenEnd.i+1
                        with sgFile.doc.retokenize() as retokenizer:
                            span = sgFile.doc[startSpan:endSpan]
                            retokenizer.merge(span)
                            return sgFile.doc[span.start]
