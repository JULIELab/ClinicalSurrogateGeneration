import dateutil.parser

# customized parser info for datetutil
class DateParserInfo(dateutil.parser.parserinfo):
    
    # for parsing German month names
    MONTHS = [('Jänner', 'Jän', 'Januar','Jan'),
              ('Februar', 'Feb', 'Feber'),
              ('März', 'Mrz'),
              ('April', 'Apr'),
              ('Mai'), 
              ('Juni', 'Jun'),
              ('Juli', 'Jul'), 
              ('August', 'Aug'), 
              ('September', 'Sep', 'Sept'), 
              ('Oktober', 'Okt'), 
              ('November', 'Nov'), 
              ('Dezember', 'Dez')]
    
# standard format of dates
dateStdFormat = '%d. %m. %y'

# formats with month as number
dateFormatsNr = ['%d.%m.%Y','%d.%m.%y', '%-d.%-m.%Y', '%-d.%-m.%y', 
                 '%-d.%m.%Y', '%-d.%m.%y', '%d.%-m.%Y', '%d.%-m.%y',
                 '%Y.%m.%d', '%y.%m.%d', '%Y.%-m.%-d', '%y.%-m.%-d', 
                 '%y%-m.%d','%Y.%m.%-d', '%y.%m.%-d', '%Y.%-m.%d', 
                 '%d.%m', '%-d.%-m', '%m.%Y', '%-m.%Y', '%m.%y', '%-m.%y', 
                 '%Y.%m', '%Y.%-m', '%y.%m', '%y.%-m', 
                 '%-d', '%d', '%Y', '%y', 
                 '%-d.%m''%d.%-m',
                 '%d.%m.%Y','%d.%m.%y', '%#d.%#m.%Y', '%#d.%#m.%y',
                 '%#d.%m.%Y', '%#d.%m.%y', '%d.%#m.%Y', '%d.%#m.%y',
                 '%Y.%m.%d', '%y.%m.%d', '%Y.%#m.%#d', '%y.%#m.%#d',
                 '%y%#m.%d','%Y.%m.%#d', '%y.%m.%#d', '%Y.%#m.%d',
                 '%d.%m', '%#d.%#m', '%m.%Y', '%#m.%Y', '%m.%y', '%#m.%y',
                 '%Y.%m', '%Y.%#m', '%y.%m', '%y.%#m',
                 '%#d', '%d', '%Y', '%y',
                 '%#d.%m''%d.%#m'
                 ]
# formats with month in letter format
dateFormatsAlpha = ['%-d.%B.%Y', '%-d.%B.%y', '%Y.%B.%-d', '%y.%B.%-d', 
                   '%d.%B.%Y', '%d.%B.%y','%Y.%B.%d', '%y.%B.%d', 
                   '%-d.%B', '%B.%-d', '%d.%B','%B.%d',
                   '%B.%Y', '%B.%y', '%Y.%B', '%y.%B', '%B',
                   '%#d.%B.%Y', '%#d.%B.%y', '%Y.%B.%#d', '%y.%B.%#d',
                   '%d.%B.%Y', '%d.%B.%y','%Y.%B.%d', '%y.%B.%d',
                   '%#d.%B', '%B.%#d', '%d.%B','%B.%d',
                   '%B.%Y', '%B.%y', '%Y.%B', '%y.%B', '%B'
                   ]

# replacement mapping for parsed months
dateReplMonths = {'January': ['Januar','Jan','Jänner', 'Jän'],
                  'February': ['Februar', 'Feb', 'Feber'],
                  'March':['März', 'Mrz'],
                  'April':['April', 'Apr'],
                  'May':['Mai'],
                  'June':['Juni', 'Jun'],
                  'July':['Juli', 'Jul'],
                  'August':['August', 'Aug'], 
                  'September':['September', 'Sep', 'Sept'],
                  'October':['Oktober', 'Okt'], 
                  'November':['November', 'Nov'], 
                  'December':['Dezember', 'Dez']}