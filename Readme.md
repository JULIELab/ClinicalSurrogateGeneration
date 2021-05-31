# Clinical Surrogate Generation System

The Clinical Surrogate Generation System replaces privacy-sensitive information by synthetically generated surrogates
(e.g., a person originally named 'Tina Smith' is renamed to 'Christa Meyer').
For further information see our [paper (Pseudonymization of PHI Items in German Clinical Reports, MIE 2021)](https://pubmed.ncbi.nlm.nih.gov/34042748/).
This system is derivated from Elisabeth Eders Surrogate Generation System from
[https://github.com/ee-2/SurrogateGeneration](https://github.com/ee-2/SurrogateGeneration) and
["De-Identification of Emails: Pseudonymizing Privacy-Sensitive Data in a German Email Corpus (Eder et al., RANLP 2019)"](https://www.aclweb.org/anthology/R19-1030/).

## Installation
* create a virtual environment
* Python 3
* spaCy (Version 2.3.4) and German language modul
* Python packages:
  * python-dateutil
  * python-Levenshtein
* for further details, see into [requirements.txt](requirements.txt)

## Usage

To use the Clinical Surrogate Generation System first edit the parameters in [param.conf](param.conf).
Then run the system with: ``` python3 main.py ```
The System was tested on Python 3.5 and 3.6 and spaCy 2.
For processing DATEs [python-dateutil](https://pypi.org/project/python-dateutil/) has to be installed.

### Entities
The following privacy-sensitive categories are currently provided:
- FEMALE (female given names)
- MALE (male given names)
- FAMILY (family names)
- ORG (organization names)
- USER (user names)
- DATE (dates)
- STREET (street names)
- STREETNO (street number)
- CITY (names of cities, towns, villages or regions)
- ZIP (Zip codes)
- PASS (passwords)
- UFID (IDs, IPs, IBANs ...)
- EMAIL (email addresses)
- URL (URLs)
- PHONE (phone and fax numbers)
- MEDICAL UNIT (common clinical institutions)
- SIZE (Groesse)
- WEIGHT (Gewicht)
* For further details, e.g., a Brat configuration, look into [annotation.conf](annotation.conf).


### Input Format
The Surrogate Generation System accepts any type of text with [BRAT](https://brat.nlplab.org/) annotations of the described entities. For each file to process the actual text without modifications ('.txt') and the annotations of the privacy-sensitive entities ('.ann') have to be provided separately. An example for the annotation format (the numbers denote the character offsets of the entities in the txt file): 
```
T1	FEMALE 6 11	Irene
T2	CITY 126 132	London
...
```
For more information see the [brat standoff format](https://brat.nlplab.org/standoff.html).
More annotations will be published under [https://github.com/julielab/jsyncc](https://github.com/julielab/jsyncc).

### Language Modules
To adapt the Surrogate Generation System to a specific language a language module has to be provided which handles the language-dependent categories (FEMALE, MALE, FAMILY, ORG, STREET, CITY, DATE).

#### German Language Module ([lang/de](lang/de))
We implemented a German language module (further described in [paper](https://www.aclweb.org/anthology/R19-1030)).

Requirements:
- [spacy v2.1.*](https://spacy.io/) with a German model linked via the shortcut 'de' ([How to install](https://spacy.io/usage), [Shortcut link](https://spacy.io/usage/models#usage-link))
- [Levenshtein](https://github.com/ztane/python-Levenshtein/)

##### Sources for Substitute Lists
- [female.json](lang/de/subLists/female.json), [male.json](lang/de/subLists/male.json), [female_nick.json](lang/de/subLists/female_nick.json), [male_nick.json](lang/de/subLists/male_nick.json)
   - Jörg Michael: <ftp://ftp.heise.de/pub/ct/listings/0717-182.zip> ([GNU Lesser General Public License (LGPL)](https://www.gnu.org/licenses/lgpl-3.0))
- [family.json](lang/de/subLists/family.json)
   - Deutscher Familienatlas (DFA): <http://www.namenforschung.net/fileadmin/user_upload/dfa/Inhaltsverzeichnisse_etc/Index_Band_I-V_Gesamt_Stand_September_2016.pdf>
- [org.json](lang/de/subLists/org.json)
   - [OpenStreetMap contributors](http://www.openstreetmap.org/): <https://www.datendieter.de/item/Liste_von_deutschen_Firmennamen_.txt> ([Open Data Commons Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/))
- [street.json](lang/de/subLists/street.json)
   - [OpenStreetMap contributors](http://www.openstreetmap.org/): <https://www.datendieter.de/item/Liste_von_deutschen_Strassennamen_.csv> ([Open Data Commons Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl/))
- [city_rec.json](lang/de/subLists/city_rec.json), [city.json](lang/de/subLists/city.json)
   - GeoNames: <http://download.geonames.org/export/dump/> ([Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/))
   - Statistik Austria — data.statistik.gv.at: <https://www.statistik.at/strasse/suchmaske.jsp> ([Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/))
   - OpenGeoDB: <http://www.fa-technik.adfc.de/code/opengeodb/PLZ.tab>
   - Amtliche Vermessung Schweiz / swisstopo: <https://www.cadastre.ch/de/services/service/registry/plz.html>


#### Requirements of a Language Module
To build a language module follow the structure of the German language module in the [lang/de](lang/de) package. All the requirements have to be properties of the specific language object (see class 'German').

##### Substitute Lists
Appropriate substitutes for the categories FEMALE, MALE, FAMILY, STREET, CITY and ORG are required. They have to be provided as dictionaries where the key is the first letter and the values are lists with names starting with this first letter and named after their category (see [lang/de/__init__.py](lang/de/__init__.py)).

##### Date Formats
You also have to provide your own date formats as done in the file [lang/de/dateFormats.py](lang/de/dateFormats.py).

##### (Distributional Letter-to-Letter Mappings)
Optionally you can define first letter mappings depending on their frequency (see [lang/de/freqMaps.py](lang/de/freqMaps.py)). Otherwise the mappings will be inherted from the file [lang/langDefaults.py](lang/langDefaults.py), which are frequency independent.

##### (Extensional Functions)
Functions for a different treatment of a specific language-dependent category will also be the default ones (replacing each entity by the unchanged entry of the substitute list) if you do not overwrite them in your own language module as shown in the German class in [lang/de/__init__.py](lang/de/__init__.py).


## Citation

If you use or extend the Clincial Surrogate Generation System please cite:

```
@inproceedings {Lohr21,
	author = {Lohr, Christina and Eder, Elisabeth and Hahn, Udo},
	title = {Pseudonymization of PHI Items in German Clinical Reports},
	booktitle = {Studies in Health Technology and Informatics -- Volume 281: Public Health and Informatics},
	year = {2021},
	month = {05},
	day = {27},
	publisher = {IOS Press Ebooks},
	pages = {273--277},
    url = {https://ebooks.iospress.nl/doi/10.3233/SHTI210163},
    doi = {10.3233/SHTI210163},
}
```
