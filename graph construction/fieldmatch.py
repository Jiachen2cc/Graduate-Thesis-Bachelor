from data_utils import useless,h2_convert
import numpy as np
from bert_model import vocab_sim,init_bert
from tqdm import tqdm
import os
import shutil
from utils import city_path,build_fold

# help build a structural dataset

def fold_copy(src,det,count):
    # src the source fold | det the target fold
    # rename the file to avoid overwrite original file
    #count = 0
    for root,_,fnames in os.walk(src):
        for fname in sorted(fnames):
            fpath = os.path.join(root,fname)
            shutil.copy(fpath,os.path.join(det,fname[:-4]+'_'+str(count)+'.txt'))
            count += 1
    return count

def simeple_match(v):

    # we will compare the input v with the fieldname we already have
    # and the ouput will be one of the filedname or just 'useless' or 'unkown'

    # check if the v is useless
    out = 'unknown'

    for uv in useless:
        if v in uv or uv in v:
            return 'useless'
    
    for key in h2_convert.keys():
        for hv in h2_convert[key]:
            if v in hv or hv in v:
                out = key

    return out

def bert_match(v,thresh1 = 0.9,thresh2 = 0.95):
    
    bert,tokenizer,device = init_bert()
    # first, match c with the useless
    for key in useless:
        if vocab_sim(v,key,bert,tokenizer,device).detach().numpy() > thresh1:
            return 'useless'
        
    # secondly , match c with those useful term
    scores = []
    for key in h2_convert.keys():
        scores.append(max([vocab_sim(v,v1,bert,tokenizer,device).detach().numpy() for v1 in h2_convert[key]]))

    maxidx = np.argmax(np.array(scores))
    maxscore = scores[maxidx]

    if maxscore > thresh2:
        return list(h2_convert.keys())[maxidx]
    else:
        return 'useless'

# extract useful term in the table and filter again

def extract_sub(fpath):

    sub = []
    with open(fpath,'r',encoding = 'utf-8') as f:
        for line in f:
            line = line.rstrip()
            if line.split(' ')[1] != 'useless':
                sub.append(line+'\n')
    with open('sub_table.txt','w',encoding = 'utf-8') as f:
        f.writelines(sub)         
    
# count size for unified fields
def count_unify(full_table,unify_table):

    num_table = {k:0 for k in h2_convert}
    num_table['useless'] = 0
    with open(full_table,'r',encoding = 'utf-8') as f:
        myfull = [line.rstrip() for line in f]
    with open(unify_table,'r',encoding = 'utf-8') as f:
        myunify = [line.rstrip() for line in f]
    
    for full,unify in zip(myfull,myunify):
        tag = unify.split(' ')[1]
        num_table[tag] += int(full.split(' ')[1])
    print(num_table)


# rename each field to unify all the countries
def rename_field(srcpath, tarpath):

    # import convert table
    func_table = {}
    with open('convert_table.txt','r',encoding = 'utf-8') as f:
        for line in f:
            k,v = line.rstrip().split(' ')
            func_table[k] = v
    
    # construct target fold
    for coun in tqdm(os.listdir(srcpath)):
        tcoun = build_fold(tarpath,coun)
        scoun = os.path.join(srcpath,coun)
        for city in os.listdir(scoun):
            scity = os.path.join(scoun,city)
            tcity = build_fold(tcoun,city)
            count = 0
            for tag in os.listdir(scity):
                if func_table[tag] == 'useless':
                    continue
                tar_fold = build_fold(tcity,func_table[tag])
                count = fold_copy(os.path.join(scity,tag),tar_fold,count)

def rename_city(path):

    for city in city_path(path):
        newname = city

        if ' ' in newname:
            parts = newname.split(' ')
            newname = ''.join(parts)

        if '(' in newname:
            index = newname.find('(')
            regionname = newname[index+1:len(newname)-1]
            newname = newname[0:index]+'_'+regionname

        if not os.path.exists(newname):
            os.rename(city,newname)

        elif newname != city:
            print(city)
            print(newname)





#print('aoregnoare.txt'[:-4])
        

#extract_sub('convert_table.txt')
#print(simeple_match('立法'))
#count_unify('h2statis.txt','convert_table.txt')
#rename_field('parse_all','merge_all')
rename_city('merge_all')

'''
if __name__ == '__main__':
    
    fpath = 'h2statis.txt'
    tpath = 'convert_table.txt'
    matchres = []
    ucount = 0

    with open(fpath,mode = 'r',encoding = 'utf-8') as f:

        for line in tqdm(f):

            line = line.rstrip()
            field,count = line.split(' ')[0],int(line.split(' ')[1])

            res1 = simeple_match(field)

            if res1 == 'unknown':
                res1 = bert_match(field)
            #print(res1)
            matchres.append(field+' '+res1+'\n')
        
    with open(tpath,mode = 'w',encoding = 'utf-8') as f:
        f.writelines(matchres)
'''    
            

    



        


    