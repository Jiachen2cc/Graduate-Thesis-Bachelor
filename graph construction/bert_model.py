from transformers import BertModel,BertTokenizer
import torch
import torch.nn.functional as F
import time


def init_bert():
    bert_path = 'bert-chinese/'
    tokenizer = BertTokenizer.from_pretrained(bert_path)
    bert = BertModel.from_pretrained(bert_path)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    #device = torch.device('cpu')
    bert.to(device)

    return tokenizer,bert,device

def sim_matrix(embeds):
    # assume that embed is a list of embeddings
    embeds = torch.stack(embeds,dim = 0)
    norm = torch.norm(embeds,dim = 1,keepdim = True)

def vocab_sim(v1,v2,tokenizer,bert,device):
    e1 = get_bert_embedding(v1,tokenizer,bert,device)
    e2 = get_bert_embedding(v2,tokenizer,bert,device)
    return F.cosine_similarity(e1,e2,0)

def get_bert_embedding(v,tokenizer,bert,device):

    input = tokenizer(v,padding = 'max_length',max_length = 30,truncation = True, return_tensors = 'pt')
    _,poolout = bert(input['input_ids'].to(device),input['attention_mask'].to(device),return_dict = False)

    return poolout.squeeze(0)

# split the content into several chunks according to the max_len
def chunk_split(content,chunk_len):
    if len(content) == 0:
        return []
    if len(content) <= chunk_len:
        return [content]
    else:
        chunk_num = len(content)//chunk_len
        chunk_num = chunk_num + 1 if chunk_len*chunk_num < len(content) else chunk_num
        chunks = [content[i*chunk_len:min((i+1)*chunk_len,len(content))] for i in range(chunk_num)]
        return chunks
    
# embed the content of a whole field
def embed_long_content(content,tokenizer,bert,device,chunk_len = 512):
    # assume chunk_len <= 512
    # split the input content into several pieces
    chunks = []
    for sub in content.split('\n\n'):
        chunks.extend(chunk_split(sub,chunk_len))
    
    embedding = []
    for chunk in chunks:
        input = tokenizer(chunk,padding='max_length',max_length = chunk_len, truncation = True, return_tensors = 'pt')
        _,poolout = bert(input['input_ids'].to(device),input['attention_mask'].to(device),return_dict = False)
        embedding.append(poolout)
    embedding = torch.mean(torch.concat(embedding,dim = 0),dim = 0).unsqueeze(dim = 0).detach().cpu()

    return embedding



