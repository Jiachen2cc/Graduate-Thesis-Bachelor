import os
import numpy as np

src1 = 'filtered_cityweb'
src2 = 'html_src'

continent = ['African','Asian','Australia','European','Latin America','North America']

def find_first_error(src1,src2):
    # convert to list
    src1,src2 = list(src1),list(src2)
    num = min(len(src1),len(src2))
    for i in range(num):
        if src1[i] != src2[i][:-4]:
            print('index:{}'.format(i)+' original name '+src1[i]+' html name '+src2[i])
            return
    print('no erroe detected!')

def unique_filter(info_array):
    _,idx = np.unique(info_array[0],return_index = True)
    return info_array[:,idx]

# delete this file if it has specific char
def delete_file(src,filelist,schar):
    for f in filelist:
        if schar in f:
            fpath = os.path.join(src,f)
            os.remove(fpath)
# filter out cityname with specific char
def filter_name(cinfo,schar):
    idx = []
    for i in range(len(cinfo[0])):
        if schar in cinfo[0][i]:
            continue
        idx.append(i)
    idx = np.array(idx)
    return cinfo[:,idx]

count1,count2 = 0,0
for c in continent:
    path1 = os.path.join(src1,c)
    path2 = os.path.join(src2,c)

    countries = os.listdir(path2)

    for co in countries:
        filename = co + '.npy'
        filepath = os.path.join(path1,filename)
        #print(filepath)
        cinfo1 = np.load(filepath,allow_pickle = True)
        idx = np.argsort(cinfo1[0])
        cinfo1 = cinfo1[:,idx]
        count1 += cinfo1.shape[1]
        
        
        foldpath = os.path.join(path2,co)
        cinfo2 = os.listdir(foldpath)
        cinfo2.sort()
        count2 += len(cinfo2)
        

        if cinfo1.shape[1] != len(cinfo2):
            
            cinfo1 = unique_filter(cinfo1)
            #cinfo1 = filter_name(cinfo1,'圣克鲁斯省 (玻利维亚)')
            print(cinfo1[0])
            print(cinfo2)
            #np.save(filepath,cinfo1)
            find_first_error(cinfo1[0],cinfo2)
            print(co,'original num:{} html num:{}'.format(cinfo1.shape[1],len(cinfo2)))
            '''
            print(cinfo1[:,idx])
            print(cinfo1[0])
            print(cinfo2)
            print(cinfo1.shape[1])
            print(len(cinfo2))
            '''
            #exit(0)

print(count1,count2)  

