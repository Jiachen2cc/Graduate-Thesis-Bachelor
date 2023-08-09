import urllib.request
import json
import os
import time
from bs4 import BeautifulSoup
import requests
import json
import re
import numpy as np


prefix = 'https://zh.wikipedia.org/zh-cn'
target = 'https://en.wikipedia.org/wiki/%E5%90%84%E5%9C%8B%E5%9F%8E%E5%B8%82%E5%88%97%E8%A1%A8'

html = urllib.request.urlopen(target).read().decode('utf-8')

soup = BeautifulSoup(html, 'html.parser')

# print(soup.title)
def filter1(tag):

  if tag.name == 'th' or tag.name == 'td':
    return True
  return False

def getcoucitydict():
    res = []
    for link in soup.findAll('li'):

        if '城市列表' in str(link):

            # res.extend(link.findAll('a'))

            for sublink in link.findAll('a'):
                if '城市列表' in str(sublink):
                    res.append(sublink)

    res = res[0:-1]

    url_dict = {}

    for link in res:

      title = link.get('title')
      url = link.get('href')

      if '页面不存在' in title:
        url = None
        title = title[0:-11]

      else:
        url = url[6::]
        url = prefix + url
        title = title[0:-4]

      url_dict[title] = url

    return url_dict

def save(mydic, dist):

    with open(dist, 'w') as f:
        ret = json.dumps(mydic, ensure_ascii=False)
        f.write(ret)
'''
def load(src):

    with open(src, 'r', encoding='utf-8') as f:
        dict = json.load(f)

    return dict
'''

def deal_with_tbody(tag,f1 = 'tr',f2 = 'td',trstart = 1,tdstart = 0,cindex = 0):

  cityname,url = [],[]
  # remove the head of the city list
  res = tag.select(f1)[trstart:]
  for link in res:
    #index,box = tdstart,link.findAll(f2)
    index,box = tdstart,link.findAll(filter1)
    if len(box) == 0:
      continue
    #print(box)
    valid = []
    while valid == [] and index < len(box):
      valid = box[index].find_all('a')
      index += 1
    # this city doesn't have any links
    print(box)
    '''
    if valid == []:
      cityname.append(link.find_all('td')[cindex].contents[0]+'(页面不存在)')
      url.append('None')
      continue
    else:
      cityname.append(valid[0].get('title'))
      url.append(valid[0].get('href'))
    
    if index == len(box):
      continue
    '''

    if valid == []:
      if link.find('i') is not None:
        cityname.append(link.find('i').contents[0]+'(页面不存在)')
        url.append(None)
      elif link.find('b') is not None:
        print(link)
        print(link.find('b'))
        cityname.append(link.find('b').contents[0]+'(页面不存在)')
        url.append(None)
      else:
        print(link)
        print('undefined information!')
        exit(0)
        #continue
    else:
      #print(valid)
      goal = None
      for va in valid:
        f = va.get('class')
        if f is not None and f[0] == 'image':
          continue
        else:
          goal = va 
          break
      #if goal == None:
      #  continue
      #valid = box[index - 1].find_all('a')[1]
      cityname.append(goal.get('title'))
      url.append(goal.get('href'))
      
  return cityname,url

def deal_with_ul(tag):

  cityname,url = [],[]
  res = tag.select('li')
  for link in res:
    valids = link.find_all('a')
    valid = None
    for va in valids:
      f = va.get('class')
      if f is not None and f[0] == 'image':
        continue
      else:
        valid = va
        break
    if valid is None:
      #print(link)
      #print(link.contents[0])
      #exit(0)
      print(link)
      cityname.append(link.contents[0]+'(页面不存在)')
      url.append('None')
      continue
      
    cityname.append(valid.get('title'))
    url.append(valid.get('href'))
  
  return cityname,url

def wrus(tag,trstart = 1,tdstart = 0):

  cityname,url = [],[]

  res = tag.select('tr')[trstart:]

  for link in res:

    index,box = tdstart,link.findAll('td')
    if len(box) < index + 1:
      continue
    else:
      goal = box[index].find_all('a')[0]
      cityname.append(goal.get('title'))
      url.append(goal.get('href'))
    
  return cityname,url

def china(tag):

  cityname,url = [],[]
  res = tag.select('li')
  for link in res:
    valids = link.find_all('a')
    for goal in valids:
      cityname.append(goal.get('title'))
      url.append(goal.get('href'))
    
  return cityname,url
      

samurl = 'https://en.wikipedia.org/wiki/The Democratic Republic of the Congo'
COUNTRY_NAME = '刚果民主共和国'
  

html = urllib.request.urlopen(samurl).read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
cityname = []
url = []

# need to be a list rather than a single tag
'''
explore_type = 'tbody'

if explore_type != 'tbody':

  tags = soup.findAll(explore_type)[2:31]
  print(tags[0])
  #print(tags[0])
  for tag in tags:
  #print(tag)
    #c,u = deal_with_ul(tag)
    c,u = china(tag)
    cityname.extend(c)
    url.extend(u)

else:
  tags = soup.findAll('tbody')
#print(tags[3])
#print(tags[0])
  #print(tags[0])
  #cityname,url = deal_with_tbody(tags[1],'tr','th',1,1,0)
  tags = tags[2:3]
  for tag in tags:
    c,u = deal_with_tbody(tag,'tr','th',4,1,0)
    cityname.extend(c)
    url.extend(u)
  #cityname,url = wrus(tags[1],1,2)
'''

#特殊处理：加蓬

# 1
tags = soup.findAll('tbody')
tag = tags[5]
print(tag)
c,u = deal_with_tbody(tag,'tr','th',1,1,0)
cityname.extend(c)
url.extend(u)
# 2
'''
tags = soup.findAll('ul')[2:3]
print(tags[0])
for tag in tags:
  c,u = deal_with_ul(tag)
  cityname.extend(c)
  url.extend(u)
'''
#cityname,url = cityname[:len(cityname) - 1],url[:len(url)-1]
#cityname = cityname_filter(cityname,COUNTRY_NAME)
print(len(cityname),len(url))
print(cityname)
print(url)



fres = np.concatenate([np.array(cityname)[np.newaxis,:],np.array(url)[np.newaxis,:]],axis = 0)
np.save(COUNTRY_NAME+'.npy',fres)




