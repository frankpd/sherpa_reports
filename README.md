# Sherpa Romeo Report Builder
Frank Donnelly, Geospatial Data Librarian, Baruch CUNY
Sept 28, 2017

## Intro

The shepra_get function is a Python 3.x script that accepts a list of journal titles from a text-delimited file and passes it to the Sherpa-Romeo API to generate an HTML report. The report summarizes the number of records matched, with specific details on archiving policies for each journal. The report is created using a template called sherpa_template that was written using the Jinja2 templating language.

Optionally, the script can accept a list of additional columns from the input file, such as article title, author names, and year published. If optional columns are provided, the script will generate two CSV files at the end of the process that contain the journal titles and these additional attributes. One CSV file will list the articles that can be submitted to an institutional repository in their final published form (final PDF) and the other will list articles that can be submitted in their final, peer-reviewed submitted form (postprint).

The script and template are copyrighted as free and open source software under a New BSD License.

## Prerequisites

Users of the script must register with Sherpa-Romeo to obtain an API key. The key is a short string of text and numbers, which should be saved as a plain text file and placed in the same directory as the script. http://www.sherpa.ac.uk/romeo/apiregistry.php

Users must download and install any version of Python 3.x first: https://www.python.org/ and then install two third-party modules (jinja2 and requests) using pip install second. To do this, a typical MS Windows user would use the command prompt, navigate to the Scripts folder for their Python installation, and type: pip3 install 'module' where module is the name of module. Mac and Linux users can simply launch the shell and type pip3 install 'module'.

Alternatively, you can download the Anacondas distribution of Python, which includes these modules by default: https://www.continuum.io/downloads.

The script has two files that should be kept together in the same folder: sherpa_func.py which is the program itself and sherpa_template.html which is the Jinja2 template used for creating reports. For simplicty's sake you could also store your key file in the same folder. 

The function needs to be imported and run in Python in order to load it into memory. Then you can call the function and provide the necessary inputs.

## Inputs:
```
sherpa_get(keyfile,infile,colnum,delim,header,clean,rpt_title,extracols=[]):
    (str,str,int,str,str,str,str,list[int]) -> file
 ```   
* keyfile: a plain text file that contains the API key. If the file is stored in the same directory you simply provide the file name. Otherwise you must supply a path to the file.

* infile: a delimited text file that contains the list of records that you want to process. If the file is stored in the same directory you simply provide the file name. Otherwise you must supply a path to the file.

* colnum: an integer that represents the position or column number in the file that contains the jounrnal title.

* delim: the character in the text file that separates the values. Could be any character, but common ones include commas ',' tabs '\t' and pipes '|'.

* header: indicates whether the file has a header row (column names) or not, with 'y' or 'n'

* clean: indicates whether you want to scrub the journal titles with 'y' or 'n'. If yes, then anything that appears in parentheses (notes) or angle brackets (html code) will be stripped out of the title.

* rpt_title: a title that will appear at the top of the HTML report, that describes what the report is. 

* extracols: an optional field. The user can supply integers in a list format that represent additional position or column numbers that contain data that they would like to pass into the script, in order to generate CSV files that contain lists of articles that can be included in an IR as postprint or final PDF articles. 

## Examples:
```
sherpa_get('key.txt','library_articles.csv',3,',','y','y','Library Dept Publications',[1,2,4])
```

The API key is in a file called key.txt. Read in a file called library_articles.csv where the journal title is stored in the 3rd column. The file contains a header row and we want to clean the journal titles (to strip out notes and HTML). The title at the top of the HTML report should be Library Dept Publications as that's what the file represents. Create CSV files with lists of articles we can submit to an IR; pass in data from columns 1,2, and 4 (which could represent attributes like author, article title, and year published).
```
sherpa_get('key.txt','profdata/smith.txt',2,'\t','y','n','Prof Smith's Articles')
```
The API key is in a file called key.txt. Read in a file called smith.txt that's stored in a folder below the current one called profdata. The journal title is stored in the 2nd column of the file. The file contains a header row and we don't want to clean the journal titles. The title at the top of the HTML report should be Prof Smith's Articles as that's what the file represents. We don't want to generate any CSV lists, just the HTML report.

## Output:

All files will begin with the name of the input file, followed by a timestamp that indicates when it was created, and by default will be created in the same folder where the input file is stored. HTML file names will consist of just those two pieces. If a user provides additional columns to generate CSV files, the CSV files will have a suffix that indicates whether the list of articles can be submitted as finalpdfs or postprints. A CSV will only be generated if there is at least one journal title from the input file that meets the criteria; so it's possible that two, one, or zero CSV files can be created.

The HTML report contains five sections:

* File summary: a summary of the number of records that were processed and what the match result was. For records with a single match, a summary of formats that can be published (pre-print, post-print, or final PDF) is provided, as is a list of individual journals that allow final PDF and post-print archiving.

* Successful matches: a list of each journal that was matched, with a count of records from the file. Specific details about the journal's policies along with links to them are provided.

* Multiple matches: a list of journal titles that had more than one possible match. Where possible, the specific details about the journal's policies along with links are provided.

* Titles not matched: a list of journal titles and the number of records that could not be matched. If a title doesn't match, it may be because it doesn't appear in the Sherpa-Romeo database, but it could also be due to typographical errors or bad titles in the input file. This list should be scrutinized to see if the input file can be modified to increase match rates.

* Failed records: any other title that simply could not be resolved or matched.


