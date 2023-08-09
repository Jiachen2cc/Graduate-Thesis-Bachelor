# select information to construct the dataset for our work
# try friendly city and other things like this
import os
import numpy as np
from utils import city_path,name_filter,build_fold
from tqdm import tqdm
from data_utils import h2_convert
from bert_model import init_bert,embed_long_content
import torch
# build a country-city dict
def c2citytable(src_path,tar_fold):

    allcountry = os.listdir(src_path)
    country2city = {c:[] for c in allcountry}

    for coun in allcountry:
        cpath = os.path.join(src_path,coun)
        for city in os.listdir(cpath):
            # remove () in the city name
            city = name_filter(city)
            country2city[coun].append(city)
    
    print(country2city)
    np.save(os.path.join(tar_fold,'country2city.npy'),country2city)
    return country2city

# convert the country-city dict to a country-city array(to help access the dataset with index)
def c2cityarray(c2city,tar_fold):

    c2citya = []
    for c in c2city.keys():
        citylist = c2city[c]
        newlist = [c+'_'+city for city in citylist]
        c2citya.extend(newlist)
    print(c2citya)
    np.save(os.path.join(tar_fold,'country2cityarray.npy'),c2citya)
    

# find the city with term "friend city" and parse the information
def analyze_friendship(src,c2city,c2cityarray,tarfold):
    all = {}
    all_len,index = 0,0
    badcase = []
    for city in tqdm(city_path(src)):
        total = []
        if '友好城市' not in os.listdir(city):
            continue
        infopaths = os.path.join(city,'友好城市')
        for ip in os.listdir(infopaths):
            city_list = parse_friendship(os.path.join(infopaths,ip),c2city,c2cityarray)
            total.extend(city_list)
        all_len += len(total)
        all[c2cityarray[index]] = total
        index += 1 
        if len(total) == 0:
            badcase.append(city)
    np.save(os.path.join(tarfold,'friendcity.npy'),all)
    # mark the city that has friendcity file but can not be parsed
    np.save(os.path.join(tarfold,'lostcity.npy'),badcase)
    print(all_len)
        

def prepare_candiates(c2city,line):
    candidates = []
    for country in c2city.keys():
        if country in line:
            candidates.extend(country + '_'+ city for city in c2city[country])

    if ('中华民国' in line or '中华人民共和国' in line or '台湾' in line) and (not '中国' in line):
        candidates.extend('中国' + '_'+ city for city in c2city['中国'])

    #candidates = list(dict.fromkeys(candidates))
    return candidates

def match_friend(candidates,line):
    
    friend = []
    for candi in candidates:
        match_sub = candi.split('_')[1]
        if '市' in match_sub:
            match_sub = match_sub[:-1]
        if match_sub in line:
            friend.append(candi)
    return friend
        
def parse_friendship(path,c2citydict,c2cityarray):
    # analyze friendcity relationship based on the friendcity file
    # store the city that has friend city term but haven't be captured
    # analyze the files by lines
    linked_city = []
    with open(path,'r',encoding = 'utf-8') as f:
        for line in f:
            #prepare candidates friend city
            candidates = prepare_candiates(c2citydict,line)
            if len(candidates) == 0:
                candidates = c2cityarray
            friend = match_friend(candidates,line)
            linked_city.extend(friend)
    return linked_city

def get_field_content(foldpath):

    content = ''
    for file in os.listdir(foldpath):
        filepath = os.path.join(foldpath,file)
        with open(filepath,mode = 'r',encoding = 'utf-8') as f:
            content += f.read()+'\n\n'
    return content

# get all the contents belong to the same field and combine them into a single file
def merge_field(srcpath,tarpath):

    for cpath in city_path(srcpath):
        country,city = cpath.split('\\')[1],cpath.split('\\')[2]

        fields = os.listdir(cpath)
        countrypath = build_fold(tarpath,country)
        citypath = build_fold(countrypath,city)

        for field in fields:
            content = get_field_content(os.path.join(cpath,field))
            if len(content) == 0:
                continue
            with open(os.path.join(citypath,field+'.txt'),mode = 'w',encoding = 'utf-8') as f:
                f.write(content)


# convert the content of each field to features
# except the friend city field (since it is our label)
def content2features(srcpath,tarpath):

    tokenizer,bert,device = init_bert()
    
    all_feature = []
    for city in city_path(srcpath):
        fields = os.listdir(city)
        features = []
        for k in list(h2_convert.keys()):
            if k == '友好城市':
                continue
            if k+'.txt' in fields:
                with open(os.path.join(city,k+'.txt'),'r',encoding = 'utf-8') as f:
                    content = f.read()
                feature = embed_long_content(content,tokenizer,bert,device,chunk_len = 512)
            else:
                feature = torch.zeros((1,384))
            features.append(feature)
        all_feature.append(torch.concat(features,dim = 1))
    all_feature = torch.concat(all_feature,dim = 0)

    torch.save(all_feature,os.path.join(tarpath,'nodefeatures.pt'))

    return all_feature

# convert (city,city) dict to (index,index) array
def friend2edge(friendcity,c2cityarray,tarpath):

    # convert c2cityarray to {city:index} dict
    c2index = {c2cityarray[i]:i for i in range(len(c2cityarray))}

    edges = []
    for city in friendcity.keys():
        idx1 = c2index[city]
        for fcity in friendcity[city]:
            edges.append([idx1,c2index[fcity]])

    edges = torch.LongTensor(edges)
    torch.save(edges,os.path.join(tarpath,'edges.pt'))
    return edges



#c2citytable('merge_all','data_table')

if __name__ == '__main__':
    #merge_field('merge_all','city_dataset')
    #c2citydict = np.load('data_table/country2city.npy',allow_pickle = True).item()
    #c2cityarray(c2citydict,'data_table')
    #c2citya = np.load('data_table/country2cityarray.npy',allow_pickle = True)
    #analyze_friendship('merge_all',c2citydict,c2citya,'data_table')
    
    '''
    badcase = np.load('data_table/lostcity.npy',allow_pickle = True)
    print(len(badcase))
    friendcity = np.load('data_table/friendcity.npy',allow_pickle = True).item()
    print(sum([len(friendcity[k]) for k in friendcity.keys()]))
    '''
    #c2citytable('merge_all','data_table')
    #res = np.load('data_table/country2city.npy',allow_pickle = True).item()
    #print(res.keys())
    #res = np.load('data_table/friendship.npy')
    #print(res)
    #analyze_friendship('merge_all',np.load('data_table/country2city.npy',allow_pickle = True).item(),'data_table')
    #pass
    '''
    friendcity = np.load('data_table/friendcity.npy',allow_pickle = True).item()

    for c1 in friendcity.keys():
        print(c1,friendcity[c1])
    '''
    #analyze_friendship('merge_all',np.load('data_table/country2city.npy',allow_pickle = True).item(),'data_table')