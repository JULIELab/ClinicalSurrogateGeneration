'''
map first letters according to frequency (OPTIONAL)
format: [
        ([list of chars with lowest frequency],
         [desired mapping for that chars (mapping will be shuffled for each file)]
        ),
        [list of chars with higher frequency],
        ...
        ),
        ...
        ]

if a character is not in defined mappings a random ascii character is taken
'''

freqMapFemale =    [
                    (['Q','X','Y','Z','Ä','Ö','Ü'],
                     ['Q','X','Y','Z','Ä','Ö','Ü']),
                    (['A','E','F','H','J','L','M','N','P','S','T','B','C','D','G','I','K','O','R','V','W','U'],
                     ['A','E','F','H','J','L','M','N','P','S','T','B','C','D','G','I','K','O','R','V','W','U']) 
                    ]
freqMapMale =      [   
                    (['Q','X','Y','Z','Ä','Ö','Ü'],
                     ['Q','X','Y','Z','Ä','Ö','Ü']),
                    (['A','E','F','H','J','L','M','N','P','S','T','B','C','D','G','I','K','O','R','V','W','U'],
                     ['A','E','F','H','J','L','M','N','P','S','T','B','C','D','G','I','K','O','R','V','W','U']) 
                    ]
freqMapFamily =    [
                    (['Q','X','Y','Ä','Ö','Ü'],
                     ['Q','X','Y','Ä','Ö','Ü']),
                    (['A','E','F','H','J','L','M','N','P','S','T','B','C','D','G','I','K','O','R','V','W','U','Z'],
                     ['A','E','F','H','J','L','M','N','P','S','T','B','C','D','G','I','K','O','R','V','W','U','Z']) 
                    ]
freqMapOrg =       [
                    (['0','1','2','3','4','5','6','7','8','9'],
                     ['T','U','V','Z','Q','X','Y','Ä','Ö','Ü']),
                    (['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Ä', 'Ü', 'Ö'],
                     ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Ä', 'Ü', 'Ö']),
                    (['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'A', 'R', 'S', 'T', 'U', 'V', 'W', 'E', 'F', 'Z', 'G', 'K', 'M'],
                     ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'A', 'R', 'S', 'T', 'U', 'V', 'W', 'E', 'F', 'Z', 'G', 'K', 'M'])
                    ]
freqMapStreet =    [
                    (['0','1','2','3','4','5','6','7','8','9'],
                     ['T','U','V','Z','Q','X','Y','Ä','Ö','Ü']),
                    (['Q','X','Y','Ä','Ö','Ü','O','P','T','U','V','Z'],
                     ['Q','X','Y','Ä','Ö','Ü','O','P','T','U','V','Z']),
                    (['A','B','F','G','H','K','L','M','R','S','W','C','D','E','I','J','N','O','P','T','U','V','Z'],
                     ['A','B','F','G','H','K','L','M','R','S','W','C','D','E','I','J','N','O','P','T','U','V','Z'])
                    ]
freqMapCity =      [
                    (['Q','X','Y','Ä','Ö','Ü'],
                     ['Q','X','Y','Ä','Ö','Ü']),
                    (['A','E','F','H','J','L','M','N','P','S','T','B','C','D','G','I','K','O','R','V','W','U','Z'],
                     ['A','E','F','H','J','L','M','N','P','S','T','B','C','D','G','I','K','O','R','V','W','U','Z']) 
                    ]