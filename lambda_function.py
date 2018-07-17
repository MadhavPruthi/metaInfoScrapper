import re
import requests
from bs4 import BeautifulSoup

# for reading email from pdf
import io
from PyPDF2 import PdfFileReader
from urllib.request import urlopen

#for getting article metainfo from crossref
from crossref.restful import Works
#import urllib3

#for writing into csv
import csv

#for s3 bucket
from io import BytesIO
import boto3

def getEmail(eventdoi):
    doi = eventdoi
    url = 'https://dx.doi.org/' + doi
    email = ''
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, "lxml")
    
    for i in soup.find_all(href=re.compile("mailto")):
        email = i.string

    return email

    
def getTitle(eventdoi):
    works = Works()
    adoi = eventdoi
    metainfo = works.doi(adoi)
    title = metainfo['title']
    title = ''.join(title)
    return title

    
def getMetaInfo(eventdoi):
    works = Works()
    adoi = eventdoi
    metainfo = works.doi(adoi)
    authors = metainfo['author']
    return authors


def writeCSV(eventdoi):
    doi = eventdoi
    title = getTitle(eventdoi)
    authors = getMetaInfo(eventdoi)
    authornames = [d['given']+ ' ' + d['family'] for d in authors]
    firstnames = [d['given'] for d in authors]
    lastnames = [d['family'] for d in authors]
    author = ''
    cauthor = ''
    email = getEmail(eventdoi)

    i = 0
    #finding cauthor
    for auth in authornames:

        fname = firstnames[i]
        fname = fname.replace(" ", "")
        fname = fname.replace(".", "")
        fname = fname.lower()
        
        lname = lastnames[i]
        lname = lname.replace(" ", "")
        lname = lname.replace(".", "")
        lname = lname.lower()
        
        i = i + 1
        if lname in email and fname in email:
            cauthor = auth
            break
        elif lname in email:
            cauthor = auth
        elif fname in email:
            cauthor = auth
    #print(cauthor)

    #writing metadata in csv file
    for auth in authornames:
        rowList = []
        author = ''.join(auth)
        rowList.append(doi)
        rowList.append(title)
        rowList.append(author)
        rowList.append(cauthor)
        rowList.append(email)
        
        with open('metainfo.csv', 'a', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(rowList)


def lambda_handler(event, context):
    '''
        Objective: Store meta data of the article whose DOI is passed as URL parameter
    '''
    doi = event['doi']
    writeCSV(doi)
    return "Success"
