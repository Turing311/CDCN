from __future__ import print_function, division
import os
import torch
import pandas as pd
#from skimage import io, transform
import cv2
import numpy as np
import random
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import pdb
import math
import os 


frames_total = 8    # each video 8 uniform samples


class Normaliztion_valtest(object):
    """
        same as mxnet, normalize into [-1, 1]
        image = (image - 127.5)/128
    """
    def __call__(self, sample):
        image_x, binary_mask, string_name = sample['image_x'],sample['binary_mask'],sample['string_name']
        new_image_x = (image_x - 127.5)/128     # [-1,1]
        
        return {'image_x': new_image_x, 'binary_mask': binary_mask, 'string_name': string_name}


class ToTensor_valtest(object):
    """
        Convert ndarrays in sample to Tensors.
        process only one batch every time
    """

    def __call__(self, sample):
        image_x, binary_mask, string_name = sample['image_x'],sample['binary_mask'],sample['string_name']
        
        # swap color axis because    BGR2RGB
        # numpy image: (batch_size) x T x H x W x C
        # torch image: (batch_size) x T x C X H X W
        image_x = image_x[:,:,:,::-1].transpose((0, 3, 1, 2))
        image_x = np.array(image_x)
                        
        binary_mask = np.array(binary_mask)
        
        return {'image_x': torch.from_numpy(image_x.astype(np.float)).float(), 'binary_mask': torch.from_numpy(binary_mask.astype(np.float)).float(), 'string_name': string_name} 



class Spoofing_valtest(Dataset):

    def __init__(self, info_list, root_dir,  transform=None):

#        self.landmarks_frame = pd.read_csv(info_list, delimiter=' ', header=None)
        self.root_dir = root_dir
        self.transform = transform
        self.dataset = DataLmdb("/kaggle/working/Fake/valid", db_size=28332, crop_size=128, flip=False, scale=1.0)

    def __len__(self):
        return len(self.dataset)

    
    def __getitem__(self, idx):
        #print(self.landmarks_frame.iloc[idx, 0])    

        face, spoofing_label = self.dataset[idx]

        image_x, binary_mask = self.get_single_image_x(face[0])

        if spoofing_label == 1:
            spoofing_label = 1            # real
        else:
            spoofing_label = 0            # fake
            binary_mask = np.zeros((32, 32))    
        
        
        #frequency_label = self.landmarks_frame.iloc[idx, 2:2+50].values  

        sample = {'image_x': image_x, 'binary_mask': binary_mask, 'spoofing_label': spoofing_label}

        if self.transform:
            sample = self.transform(sample)
        return sample

    def get_single_image_x(self, image_128):
        
        
        image_x = np.zeros((256, 256, 3))
        binary_mask = np.zeros((32, 32))
 
        image_x_temp = np.zeros((128, 128, 3), dtype=np.uint8)
        image_x_temp[:, :, 0] = image_128
        image_x_temp[:, :, 1] = image_128
        image_x_temp[:, :, 2] = image_128        

        image_x_temp_gray = cv2.cvtColor(image_x_temp, cv2.COLOR_BGR2GRAY)  # cv2.imread(image_path, 0)

        image_x = cv2.resize(image_x_temp, (256, 256))
        image_x_temp_gray = cv2.resize(image_x_temp_gray, (32, 32))

        image_x_aug = seq.augment_image(image_x) 
        
             
        
        for i in range(32):
            for j in range(32):
                if image_x_temp_gray[i,j]>0:
                    binary_mask[i,j]=1
                else:
                    binary_mask[i,j]=0
        
        
        
   
        return image_x_aug, binary_mask







if __name__ == '__main__':
    # usage
    # MAHNOB
    root_list = '/wrk/yuzitong/DONOTREMOVE/BioVid_Pain/data/cropped_frm/'
    trainval_list = '/wrk/yuzitong/DONOTREMOVE/BioVid_Pain/data/ImageSet_5fold/trainval_zitong_fold1.txt'
    

    BioVid_train = BioVid(trainval_list, root_list, transform=transforms.Compose([Normaliztion(), Rescale((133,108)),RandomCrop((125,100)),RandomHorizontalFlip(),  ToTensor()]))
    
    dataloader = DataLoader(BioVid_train, batch_size=1, shuffle=True, num_workers=8)
    
    # print first batch for evaluation
    for i_batch, sample_batched in enumerate(dataloader):
        #print(i_batch, sample_batched['image_x'].size(), sample_batched['video_label'].size())
        print(i_batch, sample_batched['image_x'], sample_batched['pain_label'], sample_batched['ecg'])
        pdb.set_trace()
        break

            
 


