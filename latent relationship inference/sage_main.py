import torch
from model import SAGE
from torch_geometric.nn import GAE
import os
from torch.optim import Adam
from torch_geometric.data import Data
from torch_geometric.loader import NeighborLoader
from torch_geometric.utils import negative_sampling,subgraph
import torch.nn.functional as F
import copy
from tqdm import tqdm
from torch_geometric.seed import seed_everything
from torch_geometric.transforms import RandomLinkSplit
from sklearn.metrics import average_precision_score, roc_auc_score
import numpy as np
import time
from utils import dictcombine

src = 'data_table'
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
lr = 1e-3

kwargs = {'batch_size':4096}

def load_data(src):

    x = torch.load(os.path.join(src,'nodefeatures.pt'))
    edge_index = torch.load(os.path.join(src,'edges.pt'))

    #normalize all features
    x = F.normalize(x - torch.mean(x,dim = 0),p = 2,dim = 1)

    return x,edge_index

def test(model:GAE,z,pos_index):

    neg_index = negative_sampling(pos_index,z.shape[0],force_undirected = True)
    auc,aps = model.test(z,pos_index,neg_index)

    return auc,aps
    
def train(model:GAE,optimizer,trainloader,epoch):

    model.train()

    pbar = tqdm(total=int(len(trainloader.dataset)))
    pbar.set_description(f'Epoch {epoch}')

    total_loss,num_sample = 0,0
    total_auc,total_aps = 0,0
    for batch in trainloader:
        optimizer.zero_grad()

        z = model(batch.x,batch.edge_index.to(device))[:batch.batch_size]
        z_edge = subgraph(list(range(z.shape[0])),batch.edge_index)[0]
        neg_edge = negative_sampling(z_edge,z.shape[0],z_edge.shape[1])

        loss = model.recon_loss(z,z_edge,neg_edge)
        loss.backward()
        optimizer.step()
        
        # test performance
        auc,aps = test(model,z,z_edge)

        total_loss += float(loss)*batch.batch_size
        total_auc += float(auc)*batch.batch_size
        total_aps += float(aps)*batch.batch_size
        num_sample += batch.batch_size

        pbar.update(batch.batch_size)

    pbar.close()

    return total_loss/num_sample,total_auc/num_sample,total_aps/num_sample

def inference(model:GAE,data,subgraph_loader,edge_dict):

    model.eval()
    z = model.encoder.inference(data.x,subgraph_loader)
    auc,aps = test(model,z,data.edge_index.cpu())

    extend(z,edge_dict)

    return auc,aps

# use trained model to discover potential friendship between cities
# for extra link we add it only when the confidence > 0.9
def extend(z,edge_dict,threshold = 0.995):

    new_link = {k:[] for k in edge_dict.keys()}
    
    adj = torch.sigmoid(torch.matmul(z,z.T))

    row_idx,col_idx = torch.where(adj >= threshold)

    for i in range(len(row_idx)):
        x,y = row_idx[i].item(),col_idx[i].item()
        if x != y:
            new_link[x].append(y)

    print(sum([len(new_link[k]) for k in new_link.keys()]))

    extend_res = dictcombine(edge_dict,new_link)

    print(sum([len(extend_res[k]) for k in extend_res.keys()]))

    np.save('data_table/latent_friend.npy',extend_res)
    
    return extend_res


    

seed_everything(0)

if __name__ == '__main__':

    x,edge_index = load_data(src)
    graph = Data(x = x, edge_index = edge_index).to(device)
    
    # split train graph and test graph (train 90% nodes test 10% nodes)
    trans = RandomLinkSplit(0.8,0,is_undirected = True)
    traindata,_,testdata = trans(graph)

    train_loader = NeighborLoader(traindata, num_neighbors = [25,10], shuffle = True, **kwargs)
    subgraph_loader = NeighborLoader(copy.copy(testdata), input_nodes=None,num_neighbors=[-1],shuffle = False,**kwargs)

    encoder = SAGE(9216,1024,64,device)
    model = GAE(encoder).to(device)
    optimizer = Adam(model.parameters(),lr = lr)

    edge_dict = np.load('data_table/edgetable.npy',allow_pickle = True).item()

    for i in range(100):
        print(train(model,optimizer,train_loader,i))
    
    print(inference(model,testdata,subgraph_loader,edge_dict))









    


