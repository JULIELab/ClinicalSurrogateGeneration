import re
import random
import os
import traceback
import importlib
from sgFile import SgFile
from string import punctuation, ascii_lowercase, ascii_uppercase
from entity import Entity
from pathlib import Path

'''
Surrogate Generation
'''


class SurrogateGeneration:

    def __init__(self, parameters):
        self.parameters = parameters
        module = importlib.import_module('lang.' + parameters['settings']['lang'])
        self.lang = getattr(module, module.__all__[0])()
        self.nrFiles = 0

    # generate random characters
    def genRandomChars(self, tokenTxt):
        surrogate = ''
        for char in tokenTxt:
            if char.isdigit():
                char = str(random.randint(0, 9))
            elif char.isalpha():
                if char.islower():
                    char = random.choice(ascii_lowercase)
                else:
                    char = random.choice(ascii_uppercase)
            surrogate += char
        return surrogate

        # substitute entity with random letters and numbers

    def subChar(self, sgFile, token):
        token.setNormCase(token.text.lower())
        if token.normCase in sgFile.sub[token.label]:
            return sgFile.sub[token.label].get(token.text, sgFile.sub[token.label][token.normCase])
        else:
            surrogate = self.genRandomChars(token.text)
            sgFile.sub[token.label][token.text] = surrogate
            sgFile.sub[token.label][token.normCase] = surrogate
            return surrogate

            # substitute EMAIL and URL

    def subUri(self, sgFile, token):
        token.setNormCase(token.text.lower())
        if token.normCase in sgFile.sub[token.label]:
            return sgFile.sub[token.label].get(token.text, sgFile.sub[token.label][token.normCase])
        else:
            diff = len(token.text) - len(re.sub('^(<?ftp:|<?file:|<?mailto:|((<?https?:)?(<?www)?))', '', token.text))
            surrogate = token.text[:diff] + self.genRandomChars(token.text[diff:])
            sgFile.sub[token.label][token.text] = surrogate
            sgFile.sub[token.label][token.normCase] = surrogate
            return surrogate

            # get substitute

    def getSubstitute(self, sgFile, token):
        if token.text in punctuation:  # punctuation is returned unchanged only special char if not UFID etc...
            return token.text
        elif token.label in ['ID', 'Typist', 'Streetno']:
            return self.subChar(sgFile, token)
        elif token.label in ['Contact']:
            return self.subUri(sgFile, token)
        elif token.label in ['Date', 'Birthdate']:
            return self.lang.getCoSurrogate(sgFile, token) or self.lang.subDate(sgFile, token)
        elif token.label == 'Street':
            return self.lang.getCoSurrogate(sgFile, token) or self.lang.subStreet(sgFile, token)
        elif token.label == 'City':
            return self.lang.getCoSurrogate(sgFile, token) or self.lang.getSurrogateAbbreviation(sgFile, token.text,token.label,self.lang.city) or self.lang.subCity(sgFile, token)
        elif token.label.startswith('FemaleGivenName'):
            return self.lang.getCoSurrogate(sgFile, token) or self.lang.getSurrogateAbbreviation(sgFile, token.text,token.label,self.lang.female) or self.lang.subFemale(sgFile, token)
        elif token.label.startswith('MaleGivenName'):
            return self.lang.getCoSurrogate(sgFile, token) or self.lang.getSurrogateAbbreviation(sgFile, token.text,token.label,self.lang.male) or self.lang.subMale(sgFile, token)
        elif token.label.startswith('FamilyName'):
            return self.lang.getCoSurrogate(sgFile, token) or self.lang.getSurrogateAbbreviation(sgFile, token.text,token.label,self.lang.family) or self.lang.subFamily(sgFile, token)
        elif token.label == 'Age':
            return self.lang.subAge(sgFile, token)
        elif token.label == 'Groesse':
            return self.lang.subHeight(sgFile, token)
        elif token.label == 'Gewicht':
            return self.lang.subWeight(sgFile, token)

    def find_match(self, snippet, text):
        for i, char in enumerate(text):
            if char == snippet[0] and text[i:(i + len(snippet))]:
                return i, (i+len(snippet))
                #break
        print('error', snippet, len(snippet))
        return 0, len(snippet)

    # substitute privacy-sensitive annotations in file
    def subFile(self, sgFile, ent_annotations, attr_annos):
        newText = ''
        begin = 0
        outputAnn = ''

        list_annotations = []
        tup_st_en = {}
        tup_st_en_old = {}

        for i, token in enumerate(ent_annotations):
            token.text = token.text.replace('\n', '')
            sub = self.getSubstitute(sgFile, token)
            tup_st_en_old[token.id] = (token.start, token.end, token.text)

            if sub:
                newText += sgFile.txt[begin:token.start] + sub
                begin = token.end
                start = str(len(newText) - len(sub))
                end = str(len(newText))
                list_annotations.append(Entity(sub, token.label, start, end, token.id))
                tup_st_en[token.id] = (int(start), int(end), sub)
            else:
                start = str(token.start + (len(newText) - begin))
                end = str(token.end + (len(newText) - begin))
                list_annotations.append(Entity(token.text, token.label, start, end, token.id))
                tup_st_en[token.id] = (int(start), int(end), token.text)

        newText += sgFile.txt[begin:]
        dict_add_frag = {}

        # combine old add-framgents
        for ent in list_annotations:
            start = int(ent.start)
            end = int(ent.end)
            if '-' in ent.id:
                id = ent.id.split('-')
                if (id[0], ent.label) not in dict_add_frag:
                    dict_add_frag[(id[0], ent.label)] = [(start, end, newText[start:end])]
                else:
                    dict_add_frag[(id[0], ent.label)].append((start, end, newText[start:end]))

        for ent in list_annotations:
            start = int(ent.start)
            end = int(ent.end)

            if newText[start:end] != ent.text:
                text_to_replace = tup_st_en_old[ent.id][2]
                start_old = tup_st_en_old[ent.id][0]
                end_old = tup_st_en_old[ent.id][1]

                text_ann_new = text_to_replace
                for tup_old in tup_st_en_old:
                    tup_st_en_old[tup_old]

                    start_temp_old = tup_st_en_old[tup_old][0]
                    end_temp_old = tup_st_en_old[tup_old][1]
                    old_long_seg = sgFile.txt[int(start_old):int(end_old)]
                    old_short_seg = sgFile.txt[int(start_temp_old):int(end_temp_old)]

                    if (start_old <= start_temp_old <= end_temp_old <= end_old)\
                            and (len(old_long_seg) > len(old_short_seg)):

                        new_start = int(tup_st_en[tup_old][0])
                        new_end = int(tup_st_en[tup_old][1])
                        text_ann_new = text_ann_new.replace(
                            sgFile.txt[int(start_temp_old):int(end_temp_old)],
                            newText[new_start:new_end])

                s, e = self.find_match(text_ann_new, newText)
                ent.start = str(s)
                ent.end = str(e)
                ent.text = text_ann_new

            if '-' not in ent.id:
                outputAnn += ent.id + '\t' + ent.label + ' ' + ent.start + ' ' + ent.end + '\t' + ent.text + '\n'

        # old add fragment elements into final file
        for frag in dict_add_frag:
            ent_id = frag[0]
            ent_type_label = frag[1]
            offsets = []
            text = []
            for tup in dict_add_frag[frag]:
                offsets.append(str(tup[0]) + ' ' + str(tup[1]))
                text.append(tup[2])
            outputAnn += ent_id + '\t' + ent_type_label + ' ' + ';'.join(offsets) + '\t' + ' '.join(text) + '\n'

        # attributes into final file
        for attr in attr_annos:
            outputAnn += attr

        fileOutputAnn = os.path.join(
            self.parameters['settings']['path_output'],
            os.path.relpath(sgFile.file,
            self.parameters['settings']['path_input']))
        fileOutputTxt = Path(fileOutputAnn).with_suffix('.txt')

        os.makedirs(os.path.dirname(fileOutputAnn), exist_ok=True)

        with open(fileOutputTxt, 'wb') as fileOutputTxt:
            fileOutputTxt.write(bytes(newText, 'utf-8'))

        with open(fileOutputAnn, 'wb') as fileOutputAnn:
            fileOutputAnn.write(bytes(outputAnn.rstrip(), 'utf-8'))

    # process ann files
    def collectFiles(self, subset, threadName):
        pattern_ent = re.compile('T\d+')
        for file in subset:
            print(file)
            ent_annos = {}
            attr_annos = []

            try:
                ann_file = Path(file).with_suffix('.txt')
                with open(ann_file, 'r', encoding='utf-8', newline='\n') as fileInputTxt:
                    inputTxt = fileInputTxt.read()

                with open(file, 'r', encoding='utf-8', newline='\n') as fileInputAnn:
                    for line in fileInputAnn.readlines():
                        row = line.split('\t')
                        offset = row[1].split(' ')
                        ent_type = offset[0]
                        ent_id = row[0]
                        if pattern_ent.match(ent_id):
                            if len(offset) == 3:
                                start = int(offset[1])
                                end = int(offset[2])
                                text = row[2]
                                ent_annos[(start, end, ent_id)] = Entity(text, ent_type, start, end, ent_id)
                            else:
                                # Handling Add-Fragment-Elements
                                start = offset[1]
                                dict_pairs = {}
                                for i in range(len(offset)):
                                    if (1 < i) and (i < (len(offset) - 1)):
                                        part = offset[i].split(';')
                                        end = part[0]
                                        dict_pairs[start] = end
                                        start = part[1]
                                dict_pairs[start] = offset[len(offset) - 1]

                                cnt = 0
                                for start in dict_pairs:
                                    end = int(dict_pairs[start])
                                    start = int(start)
                                    text = inputTxt[start:end]
                                    ent_id_add_frag = ent_id + '-' + str(cnt)
                                    cnt = cnt + 1
                                    ent_annos[(start, end, ent_id_add_frag)]\
                                        = Entity(text, ent_type, start, end, ent_id_add_frag)
                        else:
                            attr_annos.append(line)

                sgFile = SgFile(file,
                                threadName,
                                inputTxt,
                                self.lang.freqMapFemale,
                                self.lang.freqMapMale,
                                self.lang.freqMapFamily,
                                self.lang.freqMapOrg,
                                self.lang.freqMapStreet,
                                self.lang.freqMapCity)

                self.subFile(sgFile, [ent_annos[anno] for anno in sorted(ent_annos)], attr_annos)
                self.nrFiles += 1

            except Exception:
                print(file + ' not processed:')
                traceback.print_exc()
