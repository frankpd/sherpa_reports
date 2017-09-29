#!/usr/bin/env python3
#Match a list of journals to the Sherpa-Romeo API
#Frank Donnelly, Geospatial Data Librarian, Baruch CUNY
#Sept 28,2017

#With a key file obtained from Sherpa-Romeo, pass journal titles
#from a text-delimited file of articles to the SR API to generate
#an HTML report that summarizes the number of journal titles matched
#with specific archiving policies for each journal. Optionally, pass 
#additional columns from the input file to generate CSV files that list
#the specific articles that can be published in an IR.

##Copyright 2017 Frank Donnelly
##New BSD License (https://opensource.org/licenses/BSD-3-Clause)

def sherpa_get(keyfile,infile,colnum,delim,header,clean,rpt_title,extracols=[]):
    """ (str,str,int,str,str,str,str,list[int]) -> file
    Keyfile is text file with api key, infile is text file
    with journal data, colnum is # of column with journal title,
    delimiter that separates values, file has header row (y or n),
    title should be cleaned to strip HTML and notes (y or n),
    title of output report, list of additional columns (optional).
    """

    import jinja2, requests, csv, os, re
    from time import strftime, sleep
    from xml.etree import ElementTree

    #Check input values

    if isinstance(colnum,int)==True:
        pass
    else:
        print("Must specify the column where the title is stored as an integer (without quotes)")
        raise SystemExit
    
    if header.lower() in ['y','yes','n','no']:
        pass
    else:
        print("Must indicate whether there is a header row with 'y' or 'n'")
        raise SystemExit
    
    if clean.lower() in ['y','yes','n','no']:
        pass
    else:
        print("Must indicate whether to clean the titles (strip out HTML and notes in parentheses) with 'y' or 'n'")
        raise SystemExit

    #Set up the Jinja template environment

    jinja_env = jinja2.Environment(  
        trim_blocks = True,
        autoescape = False,
        loader = jinja2.FileSystemLoader(os.path.abspath('.'))
    )
    jinja_env.globals.update(zip=zip)

    template = jinja_env.get_template('sherpa_template.html')

    #Checks if key is in dict; if so, update list value, if not add it and
    #update list value
    def sumdictlist(vone,vzero,thedict):
        if vone in thedict:
            thedict[vone][1]=thedict[vone][1]+1
        else:
            thedict[vone]=[vzero,1]

    #Get the XML, grab the values for specific elements and save to list
    def getxml(req,vals):
        record=[]
        doc=ElementTree.fromstring(req.text)
        for field in vals:
            for node in doc.findall(field):
                record.append(node.text)
        return(record,doc)

    #Take the XML string and get the copyright links; if there's none pass
    #Google as a default
    def getcopy(doc,links):
        copyinfo={}
        for child in doc.findall(links):
            descript=child.find('copyrightlinktext').text
            url=child.find('copyrightlinkurl').text
            copyinfo[descript]=url                                     
        if not copyinfo:
            copyinfo['Google']='https://www.google.com/'
        return copyinfo

    #If there's division by zero just return zero
    def divide(numer,denom):
        try:
            result=numer/denom
        except ZeroDivisionError:
            result=0
        return result

    #Set up all the variables
            
    filetoday=strftime('%Y_%m_%d_%H%M')
    today=strftime('%b %d %Y %I%M %p')

    grab=['header/outcome',
        'journals/journal/jtitle',
        'journals/journal/issn',
        'publishers/publisher/name',
        'publishers/publisher/preprints/prearchiving',
        'publishers/publisher/postprints/postarchiving',
        'publishers/publisher/pdfversion/pdfarchiving',
        'publishers/publisher/romeocolour',
        'publishers/publisher/dateupdated',
        'publishers/publisher/conditions/condition'
          ]

    links='publishers/publisher/copyrightlinks/'

    matches=[]
    multiple=[]
    nomatch=[]
    failed=[]
    mult_detail=[]

    checkcount={}
    counter=0    
    inputlist=[]
    colnum=colnum-1 #Reconciles human counting (from 1) with computer counting (from 0)
    adjcols=[x - 1 for x in extracols] #Reconciles human counting (from 1) with computer counting (from 0)
    reclist=[]

    kf=open(keyfile,'r')
    thekey=kf.readline().strip()
    kf.close()

    #Read the titles for each record into the inputlist, then loop through input list,
    #passing each title to the Sherpa API. Identify whether it has already been matched;
    #if so, simply count it in checkcount. If not, then pass it to the API, save the
    #result in the appropriate list, and update checkcount.
    #A tricky aspect of this is separating journal titles retrieved from the API
    #from user-supplied titles, as the API will reformat titles and they won't
    #match the original (i.e. replaces 'and' with &). Multiple matches rely on the user
    #supplied title, as it's possible that none of the titles returned match the original name.
    #If the user supplied additional data columns that they want carried over
    #into results files, grab the appropriate columns and save them in reclist,
    #where they can be retrieved later for matches.

    print('Process launched...')

    reader=csv.reader(open(infile,'r', encoding='utf8', errors='ignore'),
                        delimiter=delim, quotechar='"')

    if header.lower() in ['y','yes']:
        next(reader)
    else:
        pass

    for line in reader:
        intitle=line[colnum].strip()
        if clean.lower() in ['y','yes']:
            intitle=re.sub("<.*?>|\(.*?\)", "", intitle)
        else:
            pass
        inputlist.append(intitle)
        if len(adjcols)>0:
            rec=[line[x].strip() for x in adjcols]
            reclist.append(rec)

    for i, title in enumerate(inputlist):
        if title in checkcount:
            checkcount[title][1]=checkcount[title][1]+1
            counter=counter+1
            if len(adjcols)>0:
                reclist[i].insert(0,title)
        else:

            p = {'jtitle':title, 'ak':thekey}
            
     
            r = requests.get('http://www.sherpa.ac.uk/romeo/api29.php',params=p)

            try:
                r.raise_for_status()
                record,doc=getxml(r,grab)
                if record[0]=='singleJournal':
                    copyinfo=getcopy(doc,links)
                    record.append(copyinfo)
                    if record[1] not in checkcount:                                           
                        matches.append(record)
                    sumdictlist(record[1],'match',checkcount)
                    if len(adjcols)>0:
                        reclist[i].insert(0,record[1])
                elif record[0]=='manyJournals':
                    if title not in checkcount:
                        record.insert(0,title)
                        multiple.append(record)
                    sumdictlist(record[0],'multiple',checkcount)
                elif record[0]=='notFound':
                    record.append(title)
                    if record[1] not in checkcount:
                        nomatch.append(record)
                    sumdictlist(record[1],'nomatch',checkcount)
                else:
                    record.append(title)
                    if record[1] not in checkcount:
                        failed.append(record)
                    sumdictlist(record[1],'fail',checkcount)
                counter=counter+1
               
            except Exception as e:
                print('There was a problem: %s' % (e))
                
        if counter % 50 ==0:
            print(counter,'records have been processed so far. Last record was:')
            print(record)
        if counter % 200 ==0:
            sleep(5)

    #For records with multiple matches, loop through the multiple list and do an issn
    #search for each. Save the details for good matches and fails for no match.

    for result in multiple:
        for item in result:
            if item is not None and item[0:4].isdigit and len(item)==9:
                p2= {'issn':item, 'ak':thekey}
                r2 = requests.get('http://www.sherpa.ac.uk/romeo/api29.php',params=p2)
                try:
                    r2.raise_for_status()
                    record,doc=getxml(r2,grab)
                    if record[0]=='singleJournal':
                        copyinfo=getcopy(doc,links)                    
                        record.append(copyinfo)
                        mult_detail.append(record)
                    else:
                        pass
                    
                except Exception as e:
                    print('There was a problem: %s' % (e))

    #When processing is finished, loop through the individual results lists and the
    #counts in check lists to create counts and percent totals  

    counts=dict.fromkeys(['matcount','nocount','multcount','failcount','pre',
                         'post','pdf'],0)
    color={}
    color_pct={}

    for key, value in checkcount.items():
        if value[0]=='match':
            counts['matcount']=counts['matcount']+value[1]
        elif value[0]=='nomatch':
            counts['nocount']=counts['nocount']+value[1]
        elif value[0]=='multiple':
            counts['multcount']=counts['multcount']+value[1]
        else:
            counts['failcount']=counts['failcount']+value[1]
            
    for record in matches:
        if record[4]=='can':
            counts['pre']=counts['pre']+checkcount[record[1]][1]
        if record[5]=='can':
            counts['post']=counts['post']+checkcount[record[1]][1]
        if record[6]=='can':
            counts['pdf']=counts['pdf']+checkcount[record[1]][1]
        if record[7] in color:
            color[record[7]]=color[record[7]]+checkcount[record[1]][1]
        else:
            color[record[7]]=checkcount[record[1]][1]
        
    for key, value in color.items():
            pct=format(value/counts['matcount'],'.0%')
            color_pct[key]=pct
            
    counts['pct_matches']=format(divide(counts['matcount'],counter),'.0%')
    counts['pct_multiple']=format(divide(counts['multcount'],counter),'.0%')
    counts['pct_nomatch']=format(divide(counts['nocount'],counter),'.0%')
    counts['pct_failed']=format(divide(counts['failcount'],counter),'.0%')

    counts['pct_pre']=format(divide(counts['pre'],counts['matcount']), '.0%')
    counts['pct_post']=format(divide(counts['post'],counts['matcount']), '.0%')
    counts['pct_pdf']=format(divide(counts['pdf'],counts['matcount']), '.0%')

    matches.sort()
    multiple.sort()
    nomatch.sort()
    failed.sort()

    #Take the names of the tags returned from the API so they can be printed
    #with each value. Open the html file and pass the variables out to the template

    names=[]
    for field in grab:
        names.append(field.split('/')[-1])


    outpath=infile.split('.')[0]+'_'+filetoday+'.html'

    outfile=open(outpath,'w', encoding="latin1", errors='ignore')
    outfile.write(template.render(today=today,counter=counter,counts=counts,matches=matches,
                                  multiple=multiple,nomatch=nomatch,failed=failed,color=color,
                                  color_pct=color_pct, names=names, checkcount=checkcount,                            
                                  infile=infile, mult_detail=mult_detail,rpt_title=rpt_title))
    
    outfile.close()

    #If the user supplied extra columns, create a dictionary where the key is the
    #journal title and the value is a list of record numbers that specify the location
    #of records that are for that journal. Then for all the matches, match the
    #title to the title in recindex, get the index number and pull the original
    #data record out of reclist and append them to lists of postprint and final
    #pdf articles which are then written as csv files.

    if len(adjcols)>0:

        recindex={}

        for i,v in enumerate(reclist):
            if v[0] in recindex:
                recindex[v[0]].append(i)
            else:
                recindex[v[0]]=[i]
                
        postprint_data=[]
        pdf_data=[]

        for result in matches:
            if result[6]=='can':
                lookup=recindex[result[1]]
                for v in lookup:
                    pdf_data.append(reclist[v])
                    
            elif result[5]=='can':
                lookup=recindex[result[1]]
                for v in lookup:
                    postprint_data.append(reclist[v])     
            else:
                pass

        if len(postprint_data)>0:
            postprint_out=infile.split('.')[0]+'_'+filetoday+'_postprint.csv'
            outfile=open(postprint_out,'w', newline='', encoding='utf8', errors='ignore')
            writer=csv.writer(outfile, delimiter=",", quotechar='"')
            writer.writerows(postprint_data)
            outfile.close()
            print('Wrote article data to', filetoday+'_postprint.csv')

        if len(pdf_data)>0:
            pdf_out=infile.split('.')[0]+'_'+filetoday+'_finalpdf.csv'
            outfile=open(pdf_out,'w', newline='', encoding='utf8', errors='ignore')
            writer=csv.writer(outfile, delimiter=",", quotechar='"')
            writer.writerows(pdf_data)
            outfile.close()
            print('Wrote article data to', filetoday+'_finalpdf.csv')

    print('\n')
    print('Finished.', counter, 'records for ', infile, ' processed on ',today,'\n')
