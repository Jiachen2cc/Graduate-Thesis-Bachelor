import urllib.request
import numpy as np
import os
import time
import socket
import random

timeout = 20
socket.setdefaulttimeout(timeout)

headers = ["Mozilla/5.0(Linux;Android6.0;Nexus5Build/MRA58N)AppleWebKit / 537.36(KHTML, likeGecko)Chrome / 75.0.3770.100MobileSafari / 537.36",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
          "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0"]

def getHtml(url):
    
    header = random.choice(headers)
    req = urllib.request.Request(url)
    req.add_header("User-Agent",header)
    file = urllib.request.urlopen(req,timeout = 15)
    html = file.read().decode('utf-8')
    file.close()
    
    return html
def build_fold(path):
    if not os.path.exists(path):
        os.mkdir(path)
# build index parser(so we can start from the last page we dealed with last time)
def index_parser(continent_index,country_index,city_index):
    pass

erro_info = 'error.txt'

def padding_erro_info(cityinfo,url,continent_index,country_index,city_index):

    info = cityinfo+'_'+url+'{}_{}_{}'.format(continent_index,country_index,city_index)+'\n'
    with open(erro_info,'a',encoding = 'utf-8') as f:
        f.write(info)
    
    

src = 'filtered_cityweb'
tar = 'html_src'
prefix = 'https://zh.wikipedia.org/'

if __name__ == '__main__':
    if not os.path.exists(tar):
        os.mkdir(tar)

    foldstart,filestart,countrystart = 1,0,0

    folds = os.listdir(src)
    for foldidx in range(foldstart,len(folds)):
    # build target fold
        fold = folds[foldidx]
        tarfopath = os.path.join(tar,fold)
        build_fold(tarfopath)
    
    # build file fold
        fopath = os.path.join(src,fold)
        files = os.listdir(fopath)
        print(files)

    # reset filestart
        if foldidx > foldstart:
            filestart = 0

        for fileidx in range(filestart,len(files)):
            file = files[fileidx]

            countryname = file[:-4]
            tarffopath = os.path.join(tarfopath,countryname)
            build_fold(tarffopath)
            # from url load country information
            cinfo = np.load(os.path.join(fopath,file),allow_pickle = True)
        
        # reset countrystart
            if fileidx > filestart:
                countrystart = 0

            for idx in range(countrystart, cinfo.shape[1]):
                cityinfo = tarffopath+'\\'+cinfo[0,idx]+'.txt'
                cityurl = prefix+cinfo[1,idx]
                print(cityinfo)
                print(cityurl)
                print('continent index:{}, country index:{}, city index:{}'.format(foldidx,fileidx,idx))
                cityname = cinfo[0,idx]
                url = prefix + cinfo[1,idx]
                res = None
                while res is None:
                    try:
                        res = getHtml(url)
                    except Exception as e:
                        if str(e) == 'HTTP Error 404: Not Found':
                            padding_erro_info(cityinfo,cityurl,foldidx,fileidx,idx)
                            break
                        print(repr(e))
                        print('continent index:{}, country index:{}, city index:{}'.format(foldidx,fileidx,idx))
                        time.sleep(10)

                save_path = cityinfo.replace('/','_')
                with open(save_path,'w',encoding = 'utf-8') as f:
                    if res is None:
                        res = ''
                    f.write(res)
            
                time.sleep(10)
                
            
