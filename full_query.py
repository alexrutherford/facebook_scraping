# -*- coding: utf-8 -*-
########################
# Script to extract Facebook content
# form public pages based on a keyword
# search. Requires an access token
# which is only valid for 1 month
# Optional first arg is ID of FB page to restart from
# Optional second arg is URL to query when restarting
# from middway through a page's comments
########################
import json,requests
import sys,csv,re
import time
from time import gmtime, strftime

v=False
#v=True
# Flag for verbose printing

outFile=None
# File to deposit filtered content
logFile=csv.writer(open('log.csv','a'),delimiter='\t')
# Log file for requests

trashFile=csv.writer(open('trash.txt','w'),delimiter='\t')
# File for writing weird bits of content I don't understand yet

ACCESSTOKEN='CAACEdEose0cBAKODv5yx7LZCYU0YsXeDBTaxEFC0XOxOyzBHvcLNiwDcxauy56ZAPyk8GTcRJZBfVYsXIpudUYXcCpDryy7DMhloeLPNAfus5oaWiqt9rDv6EqygizxTJAJEZCwbh0gIZAK50l8neqZCRe8YbkMweSHZAgUSev3rXlP7eiqJXyykxgvsh5dQbYZD'
# Define access token
# Needs updating every hour :-| from https://developers.facebook.com/tools/explorer/
# Click 'Get Access Token'
# OR get long lasting app access token
# Create an app at developers.facebook.com,
# get app iD and app secret and get long lasting key
# curl 'https://graph.facebook.com/oauth/access_token?client_id=<app_id>&client_secret=<app_secret>&grant_type=client_credentials'

ACCESSTOKEN='681571835211669|qiglQube0eaE9XFD0ycM5s21ZeQ'
# This is long lasting app key

LIMIT='5000'
# 5000 is limit for pages

QUERY='سوريا'
QUERY='دمشق'
QUERY='حمص'
#QUERY='ادلب'
#QUERY='دير الزور'
QUERY='شلل الاطفال'
#QUERY='بوليو'
# Query to grab pages

terms=[u'شلل',u'بوليو',u'لقاح',u'تطعيم',u'پوليو']
#terms=[u'سوريا',u'سوري',u'سورية',u'انا',u'اسد',u'الاسد',u'الأسد',u'لا']
#terms.append(u'علي')
#terms.append(u'لن')
terms.extend([u'polio',u'vaccination',u'injection',u'opv',u'o.p.v.',u'ipv',u'i.p.v.'])

regexString='|'.join(terms)
matchRe=re.compile(regexString)
# Construct regex from terms

nMatches=0
nTrash=0

#################
def logQuery(url):
#################
# Makes an entry in log file of URL, ID of page queries and time
  global logFile

  pageId=url.partition('graph.facebook.com/')[2]
  pageId=pageId.partition('/posts')[0]

  logFile.writerow([strftime("%H:%M:%S",time.localtime()),pageId,url])

#################
def matchesQuery(text,outFile):
#################
# Searches each piece of content for a
# single search term returns true/false
# Can't use compiled regex with unicode flag
  returnVal=False
  res=re.search(regexString,text,re.UNICODE|re.IGNORECASE)
  if res:
    returnVal=True
#    print 'TEXT',text
#    print 'GROUPS',res.group()
    outFile.writerow(['MATCH',res.group().encode('utf-8')])
    # Log each match
#    sys.exit(1)
  return returnVal
#################
def parsePosts(rr,nPages,nPosts,category):
#################
# Cycles through all posts form a given FB page
# if matching keywords, writes to file
  global outFile
  global logFile
  global nMatches
  global trashFile
  global nTrash

  for d,dd in enumerate(rr[u'data']):
      nPosts+=1

      try:
        if v:print '\tMESSAGE',dd[u'message'].encode('utf-8')
      except:
        z=0

      if u'message' in dd.keys():
    # Can we use 'story' entries?
        message=dd['message'].encode('utf-8')
        outLine=['POST',dd[u'id'],dd[u'created_time']]
        outLine.append(message.replace('\n',' | '))
        outLine.append(category)
        if v:print 'MATCHES?'
        if matchesQuery(dd['message'],outFile):
          outFile.writerow([o for o in outLine])
          nMatches+=1
      else:
        if v:print '!!! NO MESSAGE',dd.keys()

      if v: print 'COMMENTS?'

      if u'comments' in dd.keys():
        if dd[u'type'] in [u'photo',u'swf',u'link',u'status',u'video']:
#          print 'HAS COMMENTS',dd[u'type'],dd[u'link'],dd.keys()
          if u'link' in dd.keys():trashFile.writerow([dd[u'type'],dd[u'link'].encode('utf-8')])
          else:trashFile.writerow([dd[u'type']])
#          sys.exit(1)
          # Keep track of photo,links,statuses etc which DO have comments (many don't)
        for c in dd['comments']['data']:
          if v:print '\t\tCOMMENT',c['message']
          message=c['message'].encode('utf-8')
          outLine=['COMMENT',c[u'id'],c[u'created_time']]
          outLine.append(re.sub('\n',' | ',message))
          outLine.append(category)
          if matchesQuery(outLine[-2],outFile):
            outFile.writerow([o for o in outLine])
            nMatches+=1
      ## If not comments, catch other possible types
      ## These all seem to consistently not have any comments
      ## Tried querying many different types across many different pages
      ## Seems not due to privacy settings as comments possible in browser
      ## Also swf,question
      #################################
      elif dd[u'type']==u'video':
        outLine=['VIDEO',dd[u'id'],dd[u'created_time']]
        contentString=''
#        if v:print 'VIDEO'
#        print  dd
#        print dd[u'id']
#        time.sleep(100000)
#        sys.exit(1)
        '''
        try:
          xxx=requests.get('https://graph.facebook.com/'+dd[u'id']+'/comments?access_token='+ACCESSTOKEN)
        except:
          print 'FAILED'
        if len(xxx.json()[u'data'])>0:
          print 'VIDEO',xxx.json()
          sys.exit(1)
       '''
        for k in [u'description',u'message',u'caption']:
          if k in dd.keys():
            contentString+='|'+dd[k].replace('\n','|')
        contentString=contentString.encode('utf-8')
        if matchesQuery(contentString,outFile):
          outLine.append(contentString)
          outFile.writerow(outLine)
          nMatches+=1
      #################################
      elif dd[u'type']==u'status':
        # message
        # likes
        outLine=['STATUS',dd[u'id'],dd[u'created_time']]
        contentString=''
#        if v:print 'STATUS'
#        print dd
#        print dd[u'id']
#        sys.exit(1)
        '''
        try:
          xxx=requests.get('https://graph.facebook.com/'+dd[u'id']+'/comments?access_token='+ACCESSTOKEN)
        except:
          print 'FAILED'
        if len(xxx.json()[u'data'])>0:
          print 'STATUS',xxx.json()
          sys.exit(1)
        '''
        for k in [u'message']:
          if k in dd.keys():
            contentString+='|'+dd[k].replace('\n','|')
        contentString=contentString.encode('utf-8')
        if matchesQuery(contentString,outFile):
          outLine.append(contentString)
          outFile.writerow(outLine)
          nMatches+=1
      #################################
      elif dd[u'type']==u'photo':
        # picture,message
        # likes
        outLine=['PHOTO',dd[u'id'],dd[u'created_time']]
        contentString=''
#        if v:print 'PHOTO',dd[u'link']
#        print dd
#        sys.exit(1)
        '''
        try:
          xxx=requests.get('https://graph.facebook.com/'+dd[u'id']+'/comments?access_token='+ACCESSTOKEN)
        except:
          print 'FAILED'
        if len(xxx.json()[u'data'])>0:
          print 'PHOTO',xxx.json()
          sys.exit(1)
        '''
        for k in [u'picture',u'message']:
          if k in dd.keys():
            contentString+='|'+dd[k].replace('\n','|')
        contentString=contentString.encode('utf-8')
        if matchesQuery(contentString,outFile):
          outLine.append(contentString)
          outFile.writerow(outLine)
          nMatches+=1
      #################################
      elif dd[u'type']==u'link':
        # description,message
        # likes
        outLine=['LINK',dd[u'id'],dd[u'created_time']]
        contentString=''
#        if v:print 'LINK',dd[u'link']
        '''
        try:
          xxx=requests.get('https://graph.facebook.com/'+dd[u'id']+'/comments?access_token='+ACCESSTOKEN)
        except:
          print 'FAILED'
        if len(xxx.json()[u'data'])>0:
          print 'LINK',xxx.json()
          sys.exit(1)
        '''
        for k in [u'description',u'message']:
          if k in dd.keys():
            contentString+='|'+dd[k].replace('\n','|')
        contentString=contentString.encode('utf-8')
        if matchesQuery(contentString,outFile):
          outLine.append(contentString)
          outFile.writerow(outLine)
          nMatches+=1
      #################################
      else:
        if v:print '!!! NO COMMENTS',dd.keys()
        #print dd
#        nTrash+=1
#        print 'ADDING TO TRASH FILE',nTrash
#        print dd.keys(),
#        print 'TYPE',dd['type']
#        print dd[u'id']
#        if u'link' in dd.keys():print dd[u'link']
#        if 'message' in dd.keys():print 'MESSAGE',dd['message'].replace('\n','|').encode('utf-8'),dd['type']
#        json.dump(dd,trashFile,indent=2)
#        sys.exit(1)

      if v:print '+++++++++++++++++++'
  if v:print ''
  nPages+=1

  return nPages,nPosts
  '''
  except:
    print 'MISSING data KEY',rr.keys()
    print rr[u'error_code'],rr[u'error_msg']
    outFile.writerow(['MISSING DATA'])
#    sys.exit(1)
  '''
########################
def main():
########################
  global outFile
  restartOffset=0
  nPostsTotal=0
  # Counts total number of unfiltered posts considered
  nMatchesTotal=0
  global nMatches

  startTime=time.localtime()
###################################
# Parse args
  if len(sys.argv)==2:
    restartId=sys.argv[1]
#    outFile=csv.writer(open('out_'+QUERY.encode('utf-8')+'.csv','a'),delimiter='\t')
    outFile=csv.writer(open('out_'+QUERY+'.csv','a'),delimiter='\t')
    skip=True
    commentsPageSkip=False
    print '******APPENDING TO FILE','out_'+QUERY+'.csv'
    print '******RESTARTING FROM PAGE',restartId
    restartCommentsPage=None
  elif len(sys.argv)==3:
    restartId=sys.argv[1]
    restartCommentsPage=sys.argv[2]
    outFile=csv.writer(open('out_'+QUERY+'.csv','a'),delimiter='\t')
#    outFile=csv.writer(open('out_'+QUERY.encode('utf-8')+'.csv','a'),delimiter='\t')
    skip=True
    commentsPageSkip=True
    print '******APPENDING TO FILE','out_'+QUERY+'.csv'
    print '******RESTARTING FROM POSTS PAGE',restartCommentsPage
  else:
    outFile=csv.writer(open('out_'+QUERY+'.csv','w'),delimiter='\t')
    print '******OPENING OUTFILE','out_'+QUERY+'.csv'
    skip=False
    commentsPageSkip=False
    restartCommentsPage=None
    restartId=-9999
  # restartCommentsPage is FB page to resume from
  # restartId is ID of FB page to resume from
  # skip is flag to skip FB pages until restartId is found
  # commentsPageSkip is flag to skip pages of comments on a
  # FB page matching restartId until restartCommentsPage is found
###################################
  tempUrl='https://graph.facebook.com/search?q='+QUERY+'&limit='+LIMIT+'&type=page&access_token='+ACCESSTOKEN
  r=requests.get(tempUrl).json()
  logQuery(tempUrl)
# Get all pages matching QUERY

#  LIMIT=5000
  # Make limit higher once we start to look at comments not pages???

  if not 'data' in r.keys():
    print 'EXPIRED????',r
    sys.exit(1)
################################################
  for p,page in enumerate(r[u'data']):
# Each page has 'category','name','id'
    errorSkip=False

    try:
      print 'PAGE #',p,'('+str(len(r[u'data']))+')',page[u'name'],page[u'category'],page[u'id'],strftime("%H:%M:%S", time.localtime())
    except:
      print '!!!!!!!PAGE ERROR'

    if page[u'id']==restartId:
      skip=False
      print 'RESTARTING....'

    if not skip:
      tempUrl='https://graph.facebook.com/'+page[u'id']+'/posts?'+'&limit='+LIMIT+'&access_token='+ACCESSTOKEN
      rr=requests.get(tempUrl).json()
      logQuery(tempUrl)
      # Try to get the posts

      while u'error' in rr.keys() or u'error_msg' in rr.keys():
        if (u'error' in rr.keys() and u'code' in rr[u'error'].keys() and rr[u'error'][u'code'] in [1,2]) or u'error_msg' in rr.keys():
        # API error
          print 'API ERROR: SLEEPING....'
          print rr
          time.sleep(60)
          print 'RETRYING'
          nError+=1
          if nError==10:
            print nError,'ERRORS - SKIPPING'
            break
        else:
        # TOKEN ERROR
          print '********ERROR',rr[u'error']
          sys.exit(1)
        tempUrl='https://graph.facebook.com/'+page[u'id']+'/posts?'+'&limit='+LIMIT+'&access_token='+ACCESSTOKEN
        rr=requests.get(tempUrl)
        print 'rr',rr
        rr=rr.json()
        logQuery(tempUrl)
        # Try to get the posts again

      nPages=0
      nError=0
      nPosts=0
      nMatches=0

      outFile.writerow(['PAGE',page[u'id'],page[u'name'].encode('utf-8'),page[u'category'].encode('utf-8')])

      if not errorSkip and not commentsPageSkip:
      # If API has caused 3 errors, skip
      # Or if restarting from a later comments page, skip
        errorSkip=False
        nPages,nPosts=parsePosts(rr,nPages,nPosts,page[u'category'].encode('utf-8'))

      while 'paging' in rr.keys() and not errorSkip and not commentsPageSkip:

        if v:print 'LOADING',rr[u'paging'][u'next']

        rrrRaw=requests.get(rr[u'paging'][u'next'])
        logQuery(rr[u'paging'][u'next'])

        if rr['paging']['next']==restartCommentsPage and restartCommentsPage:
          commentsPageSkip=False
          print '**********MATCHED RESTART PAGE - RESUMING PARSING COMMENTS'
        # If we want to restart from last page
        elif restartCommentsPage and restartId==page['id']:
          print '**********DIDNT MATCH COMMENTS RESTART PAGE'
          restartOffset+=1

        try:
          rrr=rrrRaw.json()
        except:
          print 'JSON ERROR', rrrRaw.status_code

        while u'error' in rrr.keys() or u'error_msg' in rrr.keys():

          if u'error' in rrr.keys() or u'error_msg' in rrr.keys():
          # API error
            print 'API ERROR: SLEEPING....'
            print rrr,rrrRaw,rrrRaw.status_code,rrrRaw.text
            print rr[u'paging'][u'next']
            time.sleep(10)
            print 'RETRYING'
            nError+=1
            if nError==10:
              print nError,'ERRORS - SKIPPING'
              errorSkip=True
              break
          else:
          # TOKEN ERROR ?
            print '********ERROR',rrr
            sys.exit(1)

          rrr=requests.get(rr[u'paging'][u'next'])
#          print 'rrr',rrr,rrr.text,rrr.status_code
#          print
          rrr=rrr.json()
          logQuery(rr['paging']['next'])
        # Try to get the posts again
        # if the API doesn't respond

        if not commentsPageSkip:
          if v:
            print '# COMMENTS PAGES',nPages,'# POSTS',nPosts,'# MATCHES',nMatches,strftime("%H:%M:%S", time.localtime()),
            if not restartOffset==0:
              print '# OFFSET',restartOffset
            else:
              print ''

        if (not errorSkip and not commentsPageSkip) and not skip:
        # If API has caused 10 errors in a row
        # Or if restarting from a later page of comments
        # or if not already found restart page, skip
          nPages,nPosts=parsePosts(rrr,nPages,nPosts,page[u'category'].encode('utf-8'))
        else:
          print '************NOT PARSING POSTS',errorSkip,commentsPageSkip
          print 'BREAKING'
          break
        rr=rrr
      print '# COMMENTS PAGES',nPages,'# POSTS',nPosts,'# MATCHES',nMatches,strftime("%H:%M:%S", time.localtime())
      if not restartOffset==0:
        print '# OFFSET',restartOffset

      outFile.writerow(['PAGE TOTALS',str(nPages),str(nPosts),str(nMatches)])
      outFile.writerow(['RUNNING PAGE TOTALS',p,str(nPostsTotal),str(nMatchesTotal)])
      nPostsTotal+=nPosts
      nMatchesTotal+=nMatches
      print 'TOTAL SO FAR #POSTS',nPostsTotal,'#MATCHES',nMatchesTotal
      print '-----------'
      restartOffset=0
    else:
      print 'SKIPPING.....',nPostsTotal
  print 'FINISHED',strftime("%H:%M:%S",startTime),'-',strftime("%H:%M:%S",time.localtime())
#####
if __name__=='__main__':
#####
  main()
