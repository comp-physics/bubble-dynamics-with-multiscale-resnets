# ## updated by Scott Sims, 02/19/2022
# ## created by Yuying Liu, 04/30/2020

import os
import sys
import pdb
import torch
import numpy as np
import yaml
from shutil import copyfile

module_path = os.path.abspath(os.path.join(os.getcwd(),'src'))
if module_path not in sys.path:
    sys.path.append(module_path)

import ResNet as net

#=========================================================
# Input Arguments
#=========================================================
with open("parameters.yml", 'r') as stream:
    D = yaml.safe_load(stream)

for key in D:
    globals()[str(key)] = D[key]
    print('{}: {}'.format(str(key), D[key]))
    # transforms key-names from dictionary into global variables, then assigns them the dictionary-values
#=========================================================
arch = [n_inputs]
for j in range(n_layers):
    arch.append(width)
arch.append(n_outputs)
print("ResNet Architecture: {}".format(arch))
#print('PRESS [c] TO CONTINUE. PRESS [q] TO QUIT.')
#pdb.set_trace()
#---------------------------------------           
max_epoch = 100000     # the maximum training epoch for each leaning rate
#=========================================================
# Directories and Paths
#=========================================================
n_steps = np.int64(model_steps * 2**k_max)
data_folder = 'data_dt={}_steps={}_period={}-{}_amp={}-{}_train+val+test={}+{}+{}'.format(dt, n_steps, period_min, period_max, amp_min, amp_max, n_train, n_val, n_test)
data_dir = os.path.join(os.getcwd(), 'data', data_folder)
model_folder = f"models_dt={dt}_steps={n_steps}_period={period_min}-{period_max}_amp={amp_min}-{amp_max}_lr={learn_rate_min}-{learn_rate_max}_resnet={n_inputs}+{n_layers}x{n_neurons}+{n_outputs}"
model_dir = os.path.join(os.getcwd(), 'models', model_folder)
if not os.path.exists(data_dir):
    sys.exit("Cannot find folder ../data/{} in current directory".format(data_folder))
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

parameter_source = os.path.abspath(os.path.join(os.getcwd(), "parameters.yml"))
parameter_dest = os.path.abspath(os.path.join(model_dir, "parameters.yml"))
copyfile(parameter_source, parameter_dest)

#=========================================================
# Start Training
#=========================================================
for k in range(0,k_max+1):
        #=========================================================
        # Load Data, each with step_size = 2^k
        #=========================================================
        step_size = np.int64(2**k)
        train_data = np.load(os.path.join(data_dir, 'train_D{}.npy'.format(step_size)))
        val_data = np.load(os.path.join(data_dir, 'val_D{}.npy'.format(step_size)))
        test_data = np.load(os.path.join(data_dir, 'test.npy'))
        n_train = train_data.shape[0]
        n_val = val_data.shape[0]
        n_test = test_data.shape[0]
        n_steps = test_data.shape[1] - 1
        #=========================================================
        # Train Models, each with step_size = 2^k
        #=========================================================
        print("=======================")
        # create dataset object
        dataset = net.DataSet(train_data, val_data, test_data, dt, step_size, model_steps)
        model_name = 'model_D{}.pt'.format(step_size)
        # create/load model object
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            model = torch.load(os.path.join(model_dir, model_name), map_location=device)
            model.device = device
        except:
            print('TRAIN: {} ...'.format(model_name))
            model = net.ResNet(arch=arch, dt=dt, step_size=step_size)
        # training
        print('training samples: {}'.format(n_train))
        print('device: {}'.format(device))
        model.train_net(dataset, max_epoch=max_epoch, batch_size=batch_size, lr_max=learn_rate_max, lr_min=learn_rate_min,
                        model_path=os.path.join(model_dir, model_name))
