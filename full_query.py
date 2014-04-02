# -*- coding: utf-8 -*-
########################
# Script to extract Facebook content
# form public pages based on a keyword
# search. Requires an access token
# which is only valid for 1 month
########################
import json,requests
import sys,csv,re
import time
from time import gmtime, strftime

v=False
#v=True
# Verbose flag

outFile=None
logFile=csv.writer(open('log.csv','a'),delimiter='\t')

ACCESSTOKEN=''
# Define access token
# Needs updating every hour :-| from https://developers.facebook.com/tools/explorer/
# Click 'Get Access Token'
# OR get long lasting app access token
# Create an app at developers.facebook.com,
# get app iD and app secret and get long lasting key
# curl 'https://graph.facebook.com/oauth/access_token?client_id=<app_id>&client_secret=<app_secret>&grant_type=client_credentials'

LIMIT='5000'
# 5000 is limit for pages

QUERY='Italy'
# Query to grab pages

#################
def logQuery(url):
#################
  global logFile

  pageId=url.partition('graph.facebook.com/')[2]
  pageId=pageId.partition('/posts')[0]

  logFile.writerow([strftime("%H:%M:%S",time.localtime()),pageId,url])

#################
def matchesQuery(text):
#################
# Searches each piece of content for a
# single search term returns true/false
  returnVal=False
#  returnVal=True
  for t in text.split(' '):
    if v:print 'TESTING>>'+t+'<<',type(t)
    if t.decode('utf-8')==u'Pizza':
      returnVal=True

  return returnVal

#################
def parsePosts(rr,nPages,postIDs,category):
#################
  global outFile
  global logFile

  try:

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
  except:
    print 'MISSING data KEY',rr.keys()
    sys.exit(1)
########################
def main():
########################
  global outFile
  restartOffset=0

  if len(sys.argv)==2:
    restartId=sys.argv[1]
    outFile=csv.writer(open('out.csv','a'),delimiter='\t')
    skip=True
    commentsPageSkip=False
    print '******APPENDING TO FILE'
    print '******RESTARTING FROM PAGE',restartId
    restartCommentsPage=None
  elif len(sys.argv)==3:
    restartId=sys.argv[1]
    restartCommentsPage=sys.argv[2]
    outFile=csv.writer(open('out.csv','a'),delimiter='\t')
    skip=True
    commentsPageSkip=True
    print '******RESTARTING FROM POSTS PAGE',restartCommentsPage
  else:
    outFile=csv.writer(open('out.csv','w'),delimiter='\t')
    print '******OPENING OUTFILE'
    skip=False
    commentsPageSkip=False
    restartCommentsPage=None
    restartId=-9999
  # restartCommentsPage is FB page to resume from
  # restartId is ID of FB page to resume from
  # skip is flag to skip FB pages until restartId is found
  # commentsPageSkip is flag to skip pages of comments on a
  # FB page matching restartId until restartCommentsPage is found

  tempUrl='https://graph.facebook.com/search?q='+QUERY+'&limit='+LIMIT+'&type=page&access_token='+ACCESSTOKEN
  r=requests.get(tempUrl).json()
  logQuery(tempUrl)
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
      tempUrl='https://graph.facebook.com/'+page[u'id']+'/posts?'+'&limit='+LIMIT+'&access_token='+ACCESSTOKEN
      rr=requests.get(tempUrl).json()
      logQuery(tempUrl)
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
        tempUrl='https://graph.facebook.com/'+page[u'id']+'/posts?'+'&limit='+LIMIT+'&access_token='+ACCESSTOKEN
        rr=requests.get().json()
        logQuery(tempUrl)
        # Try to get the posts again

      postIDs=[]
      nPages=0
      nError=0
      errorSkip=False

      outFile.writerow(['PAGE',page[u'id'],page[u'name'].encode('utf-8'),page[u'category'].encode('utf-8')])

      if not errorSkip and not commentsPageSkip:
# If API has caused 3 errors, skip
# Or if restarting from a later comments page, skip
        nPages,postIDs=parsePosts(rr,nPages,postIDs,page[u'category'].encode('utf-8'))

#  while 'next' in rr[u'paging'].keys():
      while 'paging' in rr.keys():

#    print rr.keys()
#    print 'LOADING',rr[u'paging'][u'next']

        rrrRaw=requests.get(rr[u'paging'][u'next'])
        logQuery(rr[u'paging'][u'next'])

        if rr['paging']['next']==restartCommentsPage and restartCommentsPage:
          commentsPageSkip=False
          print '**********MATCHED RESTART PAGE - RESUMING PARSING COMMENTS'
        # If we want to restart from last page
        elif restartCommentsPage and restartId==page['id']:
          print '**********DIDNT MATCH COMMENTS RESTART PAGE'
#          print restartCommentsPage
#          print rr['paging']['next']
          restartOffset+=1

        try:
          rrr=rrrRaw.json()
        except:
          print 'JSON ERROR', rrrRaw.status_code

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
          logQuery(rr['paging']['next'])
        # Try to get the posts again
        # if the API doesn't respond

        if not commentsPageSkip:
          print '# COMMENTS PAGES',nPages,'# OFFSET',restartOffset,'# POSTS',len(postIDs),strftime("%H:%M:%S", time.localtime())
#        print rrr.keys()

        if (not errorSkip and not commentsPageSkip) or not skip:
        # If API has caused 3 errors
        # Or if restarting from a later page of comments
        # or if not already found restart page, skip
          nPages,postIDs=parsePosts(rrr,nPages,postIDs,page[u'category'].encode('utf-8'))
        else:
          print '************NOT PARSING POSTS',errorSkip,commentsPageSkip


        rr=rrr
      print 'TOTAL',len(postIDs)
      print '-----------'
      restartOffset=0
    else:
      print 'SKIPPING.....'
#    sys.exit(1)
  print 'FINISHED'
#####
if __name__=='__main__':
#####
  main()
