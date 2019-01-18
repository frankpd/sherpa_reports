#!/usr/bin/env python3
#Create emails to encourage IR submission
#Frank Donnelly, Geospatial Data Librarian, Baruch CUNY
#Jan 18, 2019

#Using data output fromt Sherpa-Romeo and Digital Measures,
#create a series of generic emails for professors who have published journal 
#articles where postprints of the article are eligible for submission to
#the IR. For input this script requires a CSV file that contains titles of
#the article and journal and the author's first and last names and email address
#in separate fields. A list of emails is generated in two separate files: one for 
#authors who have one publication, and one for authors who have several. The
#messages should be scrutinized for errors and customized individually
#based on caveats for submission set by publishers.


def ir_email(infile,colnum_j,colnum_a,colnum_e,colnum_fn,colnum_ln):
    """ (str,int,int,int,int,int) -> file
    Infile is a csv file with journal and article data, followed
    by integers that indicates which columns contain
    the journal name, article title, author email address, 
    author first name, and author last name in that file.
    """

    import jinja2, csv, os
    from time import strftime
    
    #Set up the Jinja template environment
    
    jinja_env = jinja2.Environment(  
        trim_blocks = True,
        autoescape = False,
        loader = jinja2.FileSystemLoader(os.path.abspath('.'))
    )
    jinja_env.globals.update(zip=zip)
    
    print('Process launched...')
    
    #Reconcile human counting with computer counting
    index_j=colnum_j-1
    index_a=colnum_a-1
    index_e=colnum_e-1
    index_fn=colnum_fn-1
    index_ln=colnum_ln-1
    
    acount=0
    pcount=0
    
    reader=csv.reader(open(infile,'r', encoding='utf8', errors='ignore'),
                      delimiter=',', quotechar='"')
    
    #Create dictionaries for authors and postprint articles using email address
    #as the key for both. Also cleans some of the data.
    authors={}
    postprints={}
    for line in reader:
        key = line[index_e].lower()
        if key in authors:
            pass
        else:
            authors[key]=[line[index_fn],line[index_ln]]
            acount=acount+1
        art=line[index_a].strip('",.')
        journ=line[index_j].strip('",.')
        if key in postprints:
            postprints[key].append([art,journ])
        else:
            postprints[key]=[[art,journ]]
        pcount=pcount+1
    
            
    filetoday=strftime('%Y_%m_%d_%H%M')    
    singlepath='emailsingle'+'_'+infile.split('_')[0]+'_'+filetoday+'.txt'
    multipath='emailmulti'+'_'+infile.split('_')[0]+'_'+filetoday+'.txt'
    singlefile=open(singlepath,'w', encoding="latin1", errors='ignore')
    multifile=open(multipath,'w', encoding="latin1", errors='ignore')
    
    #If an author has only one article, write that information out to the email
    #template that was written to address this. Otherwise, write to the other
    #email template. For that template publications are passed out as a nested
    #list with article and journal as the 1st and 2nd elements.
    for key in sorted(postprints):
        email=key
        firstname=authors[key][0]
        lastname=authors[key][1]
        if len(postprints[key])==1:
            article=postprints[key][0][0]
            journal=postprints[key][0][1]
            template = jinja_env.get_template('ir_email_template1.txt')
            singlefile.write(template.render(email=email, firstname=firstname, 
                                            lastname=lastname, article=article, 
                                            journal=journal))
        else:
            publications=postprints[key]
            template = jinja_env.get_template('ir_email_template2.txt')
            multifile.write(template.render(email=email, firstname=firstname, 
                                            lastname=lastname, publications=publications))
    
    singlefile.close()
    multifile.close()
    
    print(('Process complete. Records for {0} authors and {1} publications were processed').format(acount,pcount))