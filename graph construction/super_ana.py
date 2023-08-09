from bs4 import BeautifulSoup
import bs4
from content_analyze import build_fold
import zhconv
import os
import shutil

sample_file = 'html_analyzer/economy/马达加斯加/塔那那利佛.html'

outer =['中国/莆田市','中国/贵溪市','中国/龙岩市','克罗地亚/圣内德利亚','日本/笛吹市','中国/齐齐哈尔市']

zero = []



zero_file = 'html_analyzer/zero_content.txt'

def has_img(tag):
    if tag.name == 'img':
        return True
    if tag.name == 'a' and tag.get('class') == 'image':
        return True
    return False

def get_cn_content(tag):
    
    text = tag.contents[0]
    if isinstance(text,bs4.element.Tag):
        if has_img(text) and len(tag.contents) > 1:
            text = tag.contents[1]
        else:
            text = text.contents[0]
    # check cn_content to make sure it didn't has char '\'
    if '/' in text:
        #print(text)
        text = text.replace('/','')
    text = tag_check(text)
    return zhconv.convert(text,'zh-cn')
        
def get_tagcontent(tag):

    allcon = tag.contents
    if len(allcon) == 0:
        return ''
    else:
        return allcon[0]

def file_copy(record,tar_fold):

    with open(record,'r',encoding = 'utf-8') as f:
        
        for filename in f.readlines():
            filename = filename[:-1]
            subname = filename.split('\\')[-1]
            target_path = os.path.join(tar_fold,subname)
            print(target_path)
            shutil.copyfile(filename,target_path)
    print('finish!')


def tag_check(res):

    if isinstance(res,bs4.element.Tag):
        #img 网页中插入的图片，不做处理 | sup 词条上标，用于解释
        if res.name in ['img','sup','link','br','i','style','ruby']:
            return ''
        #字体加粗，再取一遍content即可
        elif res.name in ['b','a','mark','small','s','big','span','font','sub']:
            res = get_tagcontent(res)
            res = tag_check(res)
    
    #print(res)    
    return res

def a_parser(tag):
    if tag.get('class') == ['image']:
        return ''
    else:
        con = get_tagcontent(tag)
        if isinstance(con,bs4.element.Tag):
            if con.name == 'img':
                return ''
        con = tag_check(con)
        return con
    
# analyze the contents in some special tags: p or li
def p_parser(tag):
    result = ''
    for cn in tag.contents:
        res = cn
        if isinstance(cn,bs4.element.Tag):
            if cn.name == 'a':
                res = a_parser(cn)
            if cn.name in ['b','u']:
                res = p_parser(cn)

        #print(cn)
        #print(res)
        res = tag_check(res)
        #print(res)
        result += res
    return result

def li_parser(tag):
    total = ''
    if tag.name == 'a':
        total += a_parser(tag)
    elif tag.name == 'p':
        total += p_parser(tag)
    elif tag.name == 'ul':
        #pass
        total += ul_parser(tag)

    return zhconv.convert(total,'zh-cn')

def content_parser(tag):
    total = ''
    if tag.name == 'a':
        #print(tag)
        total += a_parser(tag)
    elif tag.name == 'p':
        total += p_parser(tag)
    elif tag.name == 'ul':
        #pass
        total += ul_parser(tag)
        #print('----content-------')
        #print(total)

    return zhconv.convert(total,'zh-cn')
    
def ul_parser(tag):
    all = ''
    #print(tag)
    for ltag in tag.contents:
        sub = ''
        if not isinstance(ltag,bs4.element.Tag):
            continue
        for content in ltag.contents:
            if isinstance(content,bs4.element.Tag):
                sub += content_parser(content)
            else:
                sub += content
        #print(sub)
        all += sub+'\n'
    #print('finished')
    #print(all)
    return all

def name_check(name):
    if '·' in name:
        name = name.replace('·','')
    return name

# focus on economic segment
def seg_parser(filename,soup,ctype = 'other'):

    start = soup.body.contents[0]
    content_dict = {}
    sub_field = '综合'
    #print(start)
    content_list = soup.body.contents if ctype == '简介' else start.next_siblings
    for tag in content_list:
        if not isinstance(tag,bs4.element.Tag):
            continue
        if tag.name == 'table' and tag.get('class') == 'navbox':
            break
        #if tag.name[0] == 'hr':
        if tag.name == 'h3':
            #print(tag)
            sub_field = tag.findAll('span')[1]
            #print(sub_field)
            sub_field = get_cn_content(sub_field)
            #print(sub_field)
        else:
            if 'h4' <= tag.name <= 'h9':
                result = get_cn_content(tag.findAll('span')[1])+'\n'
            else:
                result = content_parser(tag)
            #print(result)
            if sub_field not in content_dict.keys():
                content_dict[sub_field] = result
            else:
                content_dict[sub_field] += result

    if len(content_dict) == 0:
        zero.append(filename)
        #print('exceptions!')
        #exit(0)

    return content_dict

def dict_store(fold,res_dict):

    for k in res_dict.keys():
        path = os.path.join(fold,k+'.txt')
        with open(path,'w',encoding = 'utf-8') as f:
            f.write(res_dict[k]) 

def test_single(src,filepath,ctype = 'other'):
    src = 'html_analyzer/mix_info'
    filepath = os.path.join(src,filepath)
    with open(filepath,'r',encoding = 'utf-8') as html:
        soup = BeautifulSoup(html,'lxml')
        #print(soup)
        #print(soup)
        res = seg_parser(filepath,soup,ctype)
        for k in res.keys():
            print(k)
            print(res[k])
        
useless = ['参见','参考','注释','参考来源','相关条目','备注','图片','图集','参看','图库','注脚']
if __name__ == '__main__':

    src = 'html_analyzer/mix_info'
    tar = 'html_analyzer/parse_all'
    #flag = 0
    for country in os.listdir(src):
        srcp = os.path.join(src,country)
        tarp = build_fold(tar,country)

        for city in os.listdir(srcp):
            '''
            if city == '伊利 (剑桥郡)':
                flag = 1
            if not flag:
                continue 
            '''
            
            srcpp = os.path.join(srcp,city)
            tarpp = build_fold(tarp,city)
            print('start parsing '+tarpp)
            for word in os.listdir(srcpp):
                wordname = word[:-5]
                print(wordname)
                if wordname in useless:
                    continue
                tarppp = build_fold(tarpp,wordname)
                filename = os.path.join(srcpp,word)

                with open(filename, 'r', encoding = 'utf-8') as html:
                    soup = BeautifulSoup(html,'lxml')
                    result = seg_parser(filename,soup,wordname)
                    dict_store(tarppp,result)

            #print('finish parsing '+tarpp)   
            




    '''
    for country in os.listdir(src):
        srcp = os.path.join(src,country)
        tarp = build_fold(tar,country)
        print(country)
        for city in os.listdir(srcp):
            tarpp = build_fold(tarp,city[:-5])
            filename = os.path.join(srcp,city)

            with open(filename,'r',encoding = 'utf-8') as html:
                soup = BeautifulSoup(html,'lxml')
                result = seg_parser(filename,soup)
                dict_store(tarpp,result)
            
            print('finish parsing '+tarpp)
    

    
    print(len(zero))
    with open(zero_file,'w',encoding = 'utf-8') as f:
        for file in zero:
            f.writelines(file+'\n')
    '''
    #test_single(src,outer[4]+'.html')
    #file_copy(zero_file,'html_analyzer/checker')
    #test_single(src,'中国/温岭市/政治.html','政治')
            
            
            
            
        


    