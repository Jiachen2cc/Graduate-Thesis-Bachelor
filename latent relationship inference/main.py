import torch
from utils import edge2table
import numpy as np
import random
from sklearn.metrics import accuracy_score 
from model import pairNet
from torch.optim import Adam



# sample several positive pairs and negative pairs for training
def pair_sample(nodes,edge_dict,edge_list,sample_num):
    
    # sample positive pairs
    pos_num = sample_num
    k = np.random.choice(np.array(range(edge_list.shape[1])),pos_num,replace = False)
    px,py = nodes[edge_list[0,k]],nodes[edge_list[1,k]]
    plabel = torch.ones(pos_num)
    # sample negative pairs
    num,nodenum = 0,nodes.shape[0]
    neg_num = 3*sample_num
    idx,idy = [],[]
    while(True):
        if num == neg_num:
            break
        x,y = random.randint(0,nodenum-1),random.randint(0,nodenum-1)
        if x == y or y in edge_dict[x]:
            pass
        else:
            idx.append(x),idy.append(y)
            num += 1
    nx,ny = nodes[torch.tensor(idx)],nodes[torch.tensor(idy)]
    nlabel = torch.zeros(neg_num)

    
    samplex = torch.concat([px,nx],dim = 0)
    sampley = torch.concat([py,ny],dim = 0)
    label = torch.concat([plabel,nlabel],dim = 0)
    print(len(label))
    print(torch.sum(label))

    #permute the sample
    idx = np.random.permutation(pos_num+neg_num)

    return samplex[idx],sampley[idx],label[idx]



def pair_train(model,optimizer,nodes,edge_dict,edge_list,batchsize,epochs,device):
    
    model.train()
    x,y,label = pair_sample(nodes,edge_dict,edge_list,batchsize//2)
    x,y,label = x.to(device),y.to(device),label.to(device)
    x = x - torch.mean(x,dim = 0)
    y = y - torch.mean(y,dim = 0)
    for i in range(epochs):
        optimizer.zero_grad()
        #x,y,label = pair_sample(nodes,edge_dict,edge_list,batchsize//2)
        #x,y,label = x.to(device),y.to(device),label.to(device)

        pred = model(x,y)
        loss = model.loss(pred,label)
        loss.backward()
        optimizer.step()
       
        #count the accuracy
        #print(pred)
        if (i+1)%50 == 0:
            #print(pred)
            acc = accuracy_score(label.cpu(),(pred.detach().cpu() >= 0.7))
            print(loss,acc)

    return model


device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
lr = 0.01
weight_decay = 5e-4
batchsize = 1024
if __name__ == '__main__':
    
    # load dataset
    x = torch.load('data_table/nodefeatures.pt')

    # load edges
    edges = torch.load('data_table/edges.pt')
    edge_dict = np.load('data_table/edgetable.npy',allow_pickle=True).item()

    model = pairNet(9216,128,64,12,0.5).to(device)
    optimizer = Adam(model.parameters(),lr,weight_decay = weight_decay)

    model = pair_train(model,optimizer,x,edge_dict,edges,batchsize,2000,device)









    




