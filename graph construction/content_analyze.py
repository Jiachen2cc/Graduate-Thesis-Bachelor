import os
from bs4 import BeautifulSoup
import zhconv
import numpy as np
import bs4
import time

def build_fold(src,name):
    
    path = os.path.join(src,name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def get_cn_content(tag):
    
    text = tag.contents[0]
    if isinstance(text,bs4.element.Tag):
        
        text = text.contents[0]
    # check cn_content to make sure it didn't has char '\'
    if '/' in text:
        #print(text)
        text = text.replace('/','')
    return zhconv.convert(text,'zh-cn')

# collect all the contents before the next theme
def content_list(tag):
    
    contents = [tag]
    #print(tag)
    #count = 0
    for sib in tag.next_siblings:
        if content_filter(tag):
            continue
        if sib.name == 'h2':
            break
        contents.append(sib)
    return contents

def intro_end(tag):

    if tag.name == 'div' and tag.get('role') == 'navigation':
        return True
    if tag.name == 'h2':
        return True
    return False

def content_filter(tag):
    filtered = ['div','style','table']
    if not isinstance(tag,bs4.element.Tag):
        return True
    elif tag.name in filtered:
        return True
    return False

def get_intro(tag):
    contents = [tag]
    for sib in tag.next_siblings:
        if sib.name == 'div':
            break
    tar = sib.contents
    #print(tar)
    # find the beginning of the introduction
    restag = None
    for tag in tar:
        if tag.name == 'div' and tag.get('id') == 'mw-content-text':
            #print(tag.contents[0].contents[0])
            #print(tag.contents[0].contents[0:10])
            restag = tag.contents[0].contents[0]
            break
    # find the end of the introduction
    contents = [restag] if restag.name != 'div' else []
    for sib in restag.next_siblings:
        if content_filter(sib):
            continue
        if intro_end(sib):
            break
        contents.append(sib)

    return contents

def store_c(tar,contents):

    with open(tar,'w',encoding = 'utf-8') as f:
        for content in contents:
            f.writelines(str(content))
    
# parse given html files
useless_theme = ['名称','外部链接','参考资料','参考文献']
#target = 'html_analyzer/mix_info'
def html_parser(filename,target,useful_theme = ['经济']):
    
    # get city name
    src = build_fold(target,filename.split('\\')[-1][:-5])
    useful = 0
    print(src)
    with open(filename,'r',encoding = 'utf-8') as html:
        soup = BeautifulSoup(html, 'lxml')
        body = soup.body
        # get the introduction part
        title = body.h1
        #contents = content_list(title)
        contents = get_intro(title)
        store_c(os.path.join(src,'简介.html'),contents)
        
        tags = body.find_all('h2')
        for tag in tags:
            check_list = tag.findAll('span')
            # 检查导航菜单类的选项，并丢弃
            if len(check_list) == 0:
                continue
            theme = get_cn_content(check_list[1])
            #print(theme)
            
            if theme not in useless_theme:
                store_c(os.path.join(src,theme+'.html'),content_list(tag))
        
    return useful

# generate file list 
def build_file_dict(src):
    file_dict = {}
    for con in os.listdir(src):
        continent = os.path.join(src,con)
        for cou in os.listdir(continent):
            file_dict[cou] = []
            country = os.path.join(continent,cou)
            for city in os.listdir(country):
                file_dict[cou].append(os.path.join(country,city))
    return file_dict


def dict_parse(src,file_dict):
    
    for k in file_dict.keys():
        print('country name '+ k)
        fold_path = build_fold(src,k)

        file_list = file_dict[k]
        
        for fname in file_list:
            print(fname)
            contents = html_parser(fname)
           
            tarname = fname.split('\\')[-1]
            tarpath = os.path.join(fold_path,tarname)

            with open(tarpath,'w',encoding = 'utf-8') as f:
                for con in contents:
                    f.writelines(str(con))

    print('finished!')




fuck_city = ['卡巴莱']

# rename txt as html

#src = './html_src/compress'
if __name__ == '__main__':
    
    debug_file = 'error_log.txt'
    src = 'use_country.npy'
    target = 'mix_info'
    
    
    fd = np.load(src,allow_pickle = True)
    res_dict = {}
    all = 0
    start = time.time()
    total_num = 0
    for country in fd.keys():
        print(country)
        ctar = build_fold(target,country)
        use_res = np.array([html_parser(f,ctar) for f in fd[country]])
        count = np.sum(use_res)

        total = np.array(fd[country])
        res_dict[country] = total[use_res.astype(bool)]
        all += count
    end = time.time()
    print(total_num)
    print('average time:{:4f}'.format((end - start)/total_num))
    print(all)
    
#np.save(tar,res_dict)





