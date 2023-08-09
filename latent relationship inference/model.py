import torch
from torch_geometric.nn.conv import SAGEConv
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm


class Feature_mean(nn.Module):

    def __init__(self,chunk_num):
        super().__init__()
        self.w = nn.Parameter(torch.ones(chunk_num))
        self.chunk_num = chunk_num
        
    def forward(self,x):

        chunk_len = x.shape[1]//self.chunk_num
        chunk_feature = [x[:,i*chunk_len:(i+1)*chunk_len] for i in range(self.chunk_num)]
        weight = torch.exp(self.w)/(torch.sum(torch.exp(self.w)))
        
        y = sum(weight[i]*chunk_feature[i] for i in range(self.chunk_num))

        return y




class SAGE(torch.nn.Module):

    def __init__(self, in_dim,hidden,out_dim,device):

        super().__init__()
        self.convs = torch.nn.ModuleList()
        self.convs.append(SAGEConv(in_dim,hidden))
        self.convs.append(SAGEConv(hidden,out_dim))

        self.device = device
    
    def forward(self, x, edge_index):

        for i, conv in enumerate(self.convs):
            x = conv(x, edge_index)
            if i < len(self.convs) - 1:
                x = x.relu_()
                x = F.dropout(x, p = 0.5)
        return x
    
    @torch.no_grad()
    def inference(self, x_all, subgraph_loader):

        pbar = tqdm(total=len(subgraph_loader.dataset)*len(self.convs))
        pbar.set_description('Evaluating')

        for i, conv in enumerate(self.convs):
            xs = []
            for batch in subgraph_loader:
                x = x_all[batch.n_id].to(self.device)
                x = conv(x, batch.edge_index.to(self.device))
                if i < len(self.convs) - 1:
                    x = x.relu_()
                xs.append(x[:batch.batch_size].cpu())
                pbar.update(batch.batch_size)
            x_all = torch.cat(xs,dim = 0)

        pbar.close()

        return x_all

        

class pairNet(nn.Module):

    def __init__(self,indim,hidden,outdim,chunk_num,dropout):
        super().__init__()

        #self.feature_mean = Feature_mean(chunk_num)
        self.layers = nn.ModuleList()

        self.layers.append(nn.Linear(indim,hidden))
        self.layers.append(nn.Linear(hidden,outdim))

        self.dropout = dropout

    def forward(self,x,y):

        #x,y = self.feature_mean(x),self.feature_mean(y)

        for i in range(len(self.layers)):
            x,y = self.layers[i](x),self.layers[i](y)
            x,y = F.relu(x),F.relu(y)
            x,y = F.dropout(x,self.dropout,training=self.training),F.dropout(x,self.dropout,training=self.training)
        
        x,y = F.normalize(x,p=2,dim = 1),F.normalize(y,p=2,dim = 1)

        #simi = torch.sigmoid(torch.sum(x*y,dim = 1))
        simi = torch.sum(x*y,dim = 1)

        return simi
    
    def loss(self,pred,label):
        #return F.binary_cross_entropy(pred,label)
        return F.mse_loss(pred,label)






    
   

        