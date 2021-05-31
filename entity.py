'''
Entity properties
'''
class Entity:
    
    def __init__(self, text, label, start, end, id):
        self.text = text
        self.label = label
        self.start = start
        self.end = end
        self.id = id
    
    # set case normalized token 
    def setNormCase(self, tokenNormCase):
        self.normCase = tokenNormCase