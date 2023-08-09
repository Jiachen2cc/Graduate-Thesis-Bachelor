import os

def build_fold(src,name):
    
    path = os.path.join(src,name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path

# given title, find the first several sample about one specific field
def get_head(src,title,head_len = 10):
    
    head_info = []
    for country in os.listdir(src):
        if len(head_info) >= head_len:
            break
        pc = os.path.join(src,country)
        for city in os.listdir(pc):
            pcc = os.path.join(pc,city)
            for h2 in os.listdir(pcc):
                if h2 == title:
                    head_info.append(os.path.join(pcc,h2))
            if len(head_info) == head_len:
                break
    return head_info
            
def read_info(info):
    # info means a fold which contains contents about one specific field
    for con in os.listdir(info):
        with open(os.path.join(info,con),'r',encoding = 'utf-8') as f:
            content = f.read()
            print(content)

def city_path(src):

    for country in os.listdir(src):
        coun = os.path.join(src,country)
        for city in os.listdir(coun):
            content = os.path.join(coun,city)
            yield content

def name_filter(name):
    # filter the 'barcket'
    if '(' in name:
        name = name[0:name.find('(')]+name[name.find(')')+1:]
    return name


#get_head('parse_all','行政区划',10)
#print(get_head('parse_all','友好城市'))


#read_info('parse_all\\中国\\义乌市\\友好城市')