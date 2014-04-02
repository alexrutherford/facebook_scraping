# -*- coding: utf-8 -*-
import json,requests
import sys,csv,re
import time
from time import gmtime, strftime

v=False
#v=True

outFile=None

ACCESSTOKEN=''
# Define access token
# Needs updating every hour :-| from https://developers.facebook.com/tools/explorer/
# Click 'Get Access Token'

LIMIT='5000'
# Some large number
# 5000 is limit for pages

QUERY='Italy'
# Query to grab pages

#################
def matchesQuery(text):
#################
  returnVal=False
#  returnVal=True
  for t in text.split(' '):
    if v:print 'TESTING>>'+t+'<<',type(t)
    if t.decode('utf-8')==u'pizza':
      returnVal=True

  return returnVal

#################
def parsePosts(rr,nPages,postIDs,category):
#################
  global outFile
  
  for d,dd in enumerate(rr[u'data']):
    if dd[u'id'] in postIDs:
      print 'DUPLICATE'
    else:
      postIDs.append(dd[u'id'])
#        print dd.keys()
      
#        outLine=[u'POST',dd[u'id'],dd[u'created_time']]
#        outFile.writerow([o.encode('utf-8') for o in outLine])

      try:
        if v:print '\tMESSAGE',dd[u'message'].encode('utf-8')
      except:
        z=0

      if u'message' in dd.keys():
        message=dd['message'].encode('utf-8')
        outLine=['POST',dd[u'id'],dd[u'created_time']]
        outLine.append(message.replace('\n',' | '))
        outLine.append(category)
        if matchesQuery(outLine[-2]):outFile.writerow([o for o in outLine])
      else:
        if v:print '!!! NO MESSAGE',dd.keys()
     
      if u'comments' in dd.keys(): 
        for c in dd['comments']['data']:
          if v:print '\t\tCOMMENT',c['message']
          message=c['message'].encode('utf-8')
          outLine=['COMMENT',c[u'id'],c[u'created_time']]
          outLine.append(re.sub('\n',' | ',message))
          outLine.append(category)
          if matchesQuery(outLine[-2]):outFile.writerow([o for o in outLine])
      else:
        if v:print '!!! NO COMMENTS',dd.keys()
#        sys.exit(1)
      if v:print '+++++++++++++++++++'
    if v:print ''
    nPages+=1
#    sys.exit(1)
  return nPages,postIDs

########################
def main():
########################
  global outFile

  if len(sys.argv)>1:
    restartId=sys.argv[1]
    outFile=csv.writer(open('out.csv','a'),delimiter='\t')
    skip=True
  else:
    outFile=csv.writer(open('out.csv','w'),delimiter='\t')
    print 'OPENING OUTFILE'
    skip=False
    restartId=-9999
  # Restart from certain ID if cut off

  r=requests.get('https://graph.facebook.com/search?q='+QUERY+'&limit='+LIMIT+'&type=page&access_token='+ACCESSTOKEN).json()
# Get all pages matching QUERY

  if not 'data' in r.keys():
    print 'EXPIRED????',r
    sys.exit(1)
################################################
  for page in r[u'data']:
# Each page has 'category','name','id'
    try:
      print 'PAGE',page[u'name'],page[u'category'],page[u'id']
    except:
      print ''

    if page[u'id']==restartId:
      skip=False
      print 'RESTARTING....'
    
    if not skip:
      rr=requests.get('https://graph.facebook.com/'+page[u'id']+'/posts?'+'&limit='+LIMIT+'&access_token='+ACCESSTOKEN).json()
# Try to get the posts
      while u'error' in rr.keys():

        if rr[u'error'][u'code'] in [1,2]:
        # API error
          print 'API ERROR: SLEEPING....'
          time.sleep(10)    
          print 'RETRYING'
          nError+=1
          if nError==3:
            print nError,'ERRORS - SKIPPING'
            break
        else:
        # TOKEN ERROR
          print '********ERROR',rr[u'error']
          sys.exit(1)
        rr=requests.get('https://graph.facebook.com/'+page[u'id']+'/posts?'+'&limit='+LIMIT+'&access_token='+ACCESSTOKEN).json()
        # Try to get the posts again

      postIDs=[]
      nPages=0
      nError=0
      errorSkip=False

      outFile.writerow(['PAGE',page[u'id'],page[u'name'].encode('utf-8'),page[u'category'].encode('utf-8')])
      
      nPages,postIDs=parsePosts(rr,nPages,postIDs,page[u'category'].encode('utf-8'))

#  while 'next' in rr[u'paging'].keys():
      while 'paging' in rr.keys():

#    print rr.keys()
#    print 'LOADING',rr[u'paging'][u'next']
       
        rrr=requests.get(rr[u'paging'][u'next']).json()
        
        while u'error' in rrr.keys():

          if rrr[u'error'][u'code'] in [1,2]:
        # API error
            print 'API ERROR: SLEEPING....'
            time.sleep(10)    
            print 'RETRYING'
            nError+=1
            if nError==3:
              print nError,'ERRORS - SKIPPING'
              errorSkip=True
              break
          else:
        # TOKEN ERROR
            print '********ERROR',rrr['error']
            sys.exit(1)
          
          rrr=requests.get(rr[u'paging'][u'next']).json()
        # Try to get the posts again
        # if the API doesn't respond
 
        print '# PAGES',nPages,'# POSTS',len(postIDs),from time import gmtime, strftime("%Y-%m-%d %H:%M:%S", localtime())
#        print rrr.keys()
        if not errorSkip:
        # If API has caused 3 errors, skip
          nPages,postIDs=parsePosts(rrr,nPages,postIDs,page[u'category'].encode('utf-8'))
        rr=rrr
      print 'TOTAL',len(postIDs)
      print '-----------' 
    else:
      print 'SKIPPING.....'
#    sys.exit(1)
#####
if __name__=='__main__':
#####
  main()
