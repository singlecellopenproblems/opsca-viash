import sys

import torch
from torch.utils.data import DataLoader
# from sklearn.model_selection import train_test_split

import anndata as ad
import pickle

#check gpu available
if (torch.cuda.is_available()):
    device = 'cuda:0' #switch to current device
    print('current device: gpu', flush=True)
else:
    device = 'cpu'
    print('current device: cpu', flush=True)


## VIASH START

par = {
  'input_train_mod1': 'resources_test/predict_modality/openproblems_neurips2021_normal/bmmc_cite/train_mod1.h5ad',
  'input_train_mod2': 'resources_test/predict_modality/openproblems_neurips2021_normal/bmmc_cite/train_mod2.h5ad',
  'output': 'model.pt'
}

meta = {
   'resources_dir': 'src/tasks/predict_modality/methods/novel',
}
## VIASH END


sys.path.append(meta['resources_dir'])
from helper_functions import train_and_valid, lsiTransformer, ModalityMatchingDataset
from helper_functions import ModelRegressionAtac2Gex, ModelRegressionAdt2Gex, ModelRegressionGex2Adt, ModelRegressionGex2Atac

print('Load data', flush=True)

# TODO: something went really wrong while refactoring this component,
# because the train script is not supposed to get access to the test data.
# see this version of the code to start:
# https://github.com/openproblems-bio/neurips2021_multimodal_topmethods/blob/dc7bd58dacbe804dcc7be047531d795b1b04741e/src/predict_modality/methods/novel/train/script.py#L27-L28


input_train_mod1 = ad.read_h5ad(par['input_train_mod1'])
input_train_mod2 = ad.read_h5ad(par['input_train_mod2'])

mod1 = input_train_mod1.uns['modality']
mod2 = input_train_mod2.uns['modality']

input_train_mod1.X = input_train_mod2.layers['counts']
input_train_mod2.X = input_train_mod1.layers['counts']

input_train_mod2_df = input_train_mod2.to_df()

print('Start train', flush=True)
if mod1 != 'ADT':  
  lsi_transformer_gex = lsiTransformer(n_components=256)
  input_train_mod1_df = lsi_transformer_gex.fit_transform(input_train_mod1)
else:
  input_train_mod1_df = input_train_mod1.to_df()

# reproduce train/test split from phase 1
batch = input_train_mod1.obs["batch"]
train_ix = [ k for k,v in enumerate(batch) if v not in {'s1d2', 's3d7'} ]
test_ix = [ k for k,v in enumerate(batch) if v in {'s1d2', 's3d7'} ]

train_mod1 = input_train_mod1_df.iloc[train_ix, :]
train_mod2 = input_train_mod2_df.iloc[train_ix, :]
test_mod1 = input_train_mod1_df.iloc[test_ix, :]
test_mod2 = input_train_mod2_df.iloc[test_ix, :]
  
# train_mod1, test_mod1, train_mod2, test_mod2 = train_test_split(input_train_mod1, input_train_mod2, test_size=0.25, random_state=666)

if mod1 == 'ATAC' and mod2 == 'GEX':
  dataset_train = ModalityMatchingDataset(train_mod1, train_mod2)
  dataloader_train = DataLoader(dataset_train, 256, shuffle = True, num_workers = 8)

  dataset_test = ModalityMatchingDataset(test_mod1, test_mod2)
  dataloader_test = DataLoader(dataset_test, 64, shuffle = False, num_workers = 8)

  model = ModelRegressionAtac2Gex(256,13431).to(device)
  optimizer = torch.optim.AdamW(model.parameters(), lr=0.00008386597445284492,weight_decay=0.000684887347727808)
        
elif mod1 == 'ADT' and mod2 == 'GEX':
  dataset_train = ModalityMatchingDataset(train_mod1, train_mod2)
  dataloader_train = DataLoader(dataset_train, 64, shuffle = True, num_workers = 4)

  dataset_test = ModalityMatchingDataset(test_mod1, test_mod2)
  dataloader_test = DataLoader(dataset_test, 32, shuffle = False, num_workers = 4)

  model = ModelRegressionAdt2Gex(134,13953).to(device)
  optimizer = torch.optim.Adam(model.parameters(), lr=0.00041, weight_decay=0.0000139)


elif mod1 == 'GEX' and mod2 == 'ADT':
  dataset_train = ModalityMatchingDataset(train_mod1, train_mod2)
  dataloader_train = DataLoader(dataset_train, 32, shuffle = True, num_workers = 8)

  dataset_test = ModalityMatchingDataset(test_mod1, test_mod2)
  dataloader_test = DataLoader(dataset_test, 64, shuffle = False, num_workers = 8)

  model = ModelRegressionGex2Adt(256,134).to(device)
  optimizer = torch.optim.AdamW(model.parameters(), lr=0.000034609210829678734, weight_decay=0.0009965881574697426)


elif mod1 == 'GEX' and mod2 == 'ATAC':
  dataset_train = ModalityMatchingDataset(train_mod1, train_mod2)
  dataloader_train = DataLoader(dataset_train, 64, shuffle = True, num_workers = 8)

  dataset_test = ModalityMatchingDataset(test_mod1, test_mod2)
  dataloader_test = DataLoader(dataset_test, 64, shuffle = False, num_workers = 8)

  model = ModelRegressionGex2Atac(256,10000).to(device)
  optimizer = torch.optim.AdamW(model.parameters(), lr=0.00001806762345275399, weight_decay=0.0004084171379280058)

loss_fn = torch.nn.MSELoss()
train_and_valid(model, optimizer, loss_fn, dataloader_train, dataloader_test, par['output'], device)

if mod1 != 'ADT':
    with open(par['output_pretrain'] + '/lsi_transformer.pickle', 'wb') as f:
        pickle.dump(lsi_transformer_gex, f)

