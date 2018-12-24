#!/usr/bin/python


import warnings
warnings.filterwarnings("ignore")

import os, sys
import numpy as np
import pandas as pd
import scipy.io as sio
from sklearn.preprocessing import MinMaxScaler
from keras.utils import np_utils

from dreamUtils import *
np.random.seed(1453)


DATA_DIR = './'
channels_coord = DATA_DIR + 'channelcoords.mat'
locs_3D = sio.loadmat(channels_coord)['locstemp']
locs_2D = map_to_2d(locs_3D)
print(locs_2D.shape)



def create_videos_single(video_size, image_size, sec):
    # Load raw data 
    filename = DATA_DIR + str(sec) + 'sec_raw_data_zip'
    loaded = np.load(filename+'.npz')
    rawdata = loaded['data']
    label = loaded['labels']
    
    
    # centerize raw data for reference electrode
    rawdata_normalized = []
    scaler = MinMaxScaler(feature_range=(-1,1))
    for trial in rawdata:
        #centerized
        n_trial =  centerize_reference(trial)
        #min-max scale
        #scaler.fit(n_trial)
        #mm_trial = scaler.transform(n_trial)
        rawdata_normalized.append(n_trial)

    rawdata = np.array(rawdata_normalized)   
    
    
    x_tr, x_te, y_tr, y_te = tt_split(rawdata, label, ratio=0.9)
    
    
    x_tr_video = []
    VIDEO_SIZE = video_size
    SLIDE = 10

    y_train_list = []
    x_train_list = []
    
    #Clip the video of 100 frames for train data
    for ind, trial in enumerate(x_tr):
        num_video = (trial.shape[0]-VIDEO_SIZE-SLIDE)//VIDEO_SIZE
        start = 0
        for i in range(num_video):
            a_video = trial[start: start+VIDEO_SIZE, :]
            x_tr_video.append(a_video)
            start += SLIDE

        value = np.array(x_tr_video)

        #Balance the dataset
        if y_tr[ind] == 2:
            selected = value[np.random.randint(value.shape[0], size=int(value.shape[0] * 0.35)), :]
            x_train_list.append(selected)
            y_train_list.append(lab(2, selected.shape[0]))

        elif y_tr[ind] == 1:
            selected = value[np.random.randint(value.shape[0], size=int(value.shape[0] * 0.45)), :]
            x_train_list.append(selected)
            y_train_list.append(lab(1, selected.shape[0]))
        else :
            x_train_list.append(value)
            y_train_list.append(lab(0, value.shape[0]))
        
        
    #Create train matrix  
    X_train = np.concatenate(x_train_list, axis = 0)
    y_train = np.concatenate(y_train_list, axis = 0)
    
    video_images = [gen_images(locs_2D, x, image_size) for x in X_train]
    X_train_video_images = np.array(video_images)
    
    
    x_te_video = []
    VIDEO_SIZE = video_size
    SLIDE = 10
    x_test_list = []
    y_test_list = []

    #Clip the video of 100 frames for train data
    for ind, trial in enumerate(x_te):
        num_video = (trial.shape[0]-VIDEO_SIZE-SLIDE)//VIDEO_SIZE
        start = 0
        for i in range(num_video):
            a_video = trial[start: start+VIDEO_SIZE, :]
            x_tr_video.append(a_video)
            start += SLIDE
    
        value = np.array(x_tr_video)
        x_test_list.append(value)
        y_test_list.append(lab(0, value.shape[0]))
    
    X_test = np.concatenate(x_test_list, axis=0)
    y_test = np.concatenate(y_test_list, axis=0)  
    
    video_images = [gen_images(locs_2D, x, image_size) for x in X_test]
    X_test_video_images = np.array(video_images)
    
    # encode labels as one-hot vectors
    y_train = np_utils.to_categorical(y_train)
    y_test = np_utils.to_categorical(y_test)
    
    
    fileName =  str(image_size)+'_'+str(image_size)+'_last'+str(sec)+'sec_video'
    np.savez_compressed(fileName, train_video=X_train_video_images, train_labels=y_train, test_video=X_test_video_images, test_labels=y_test)
    
    
    
def create_videos_multi(video_size, image_size):
    # Load fft data 
    filename = DATA_DIR +'fft_data_zip'
    loaded = np.load(filename+'.npz')
    rawdata = loaded['data']
    label = loaded['labels']
    
    x_tr, x_te, y_tr, y_te = tt_split(rawdata, label, ratio=0.9)
    
    x_tr_video = []
    VIDEO_SIZE = video_size
    SLIDE = 1

    y_train_list = []
    x_train_list = []
    
    #Clip the video of 10 frames for train data
    for ind, trial in enumerate(x_tr):
        num_video = (trial.shape[0]-VIDEO_SIZE-SLIDE)//VIDEO_SIZE
        start = 0
        for i in range(num_video):
            a_video = trial[start: start+VIDEO_SIZE, :]
            x_tr_video.append(a_video)
            start += SLIDE

        value = np.array(x_tr_video)

        #Balance the dataset
        if y_tr[ind] == 2:
            selected = value[np.random.randint(value.shape[0], size=int(value.shape[0] * 0.35)), :]
            x_train_list.append(selected)
            y_train_list.append(lab(2, selected.shape[0]))

        elif y_tr[ind] == 1:
            selected = value[np.random.randint(value.shape[0], size=int(value.shape[0] * 0.45)), :]
            x_train_list.append(selected)
            y_train_list.append(lab(1, selected.shape[0]))
        else :
            x_train_list.append(value)
            y_train_list.append(lab(0, value.shape[0]))
        
        
    #Create train matrix  
    X_train = np.concatenate(x_train_list, axis = 0)
    y_train = np.concatenate(y_train_list, axis = 0)
    
    video_images = [gen_images(locs_2D, x, image_size) for x in X_train]
    X_train_video_images = np.array(video_images)
    
    
    x_te_video = []
    VIDEO_SIZE = video_size
    SLIDE = 1
    x_test_list = []
    y_test_list = []

    #Clip the video of 100 frames for train data
    for ind, trial in enumerate(x_te):
        num_video = (trial.shape[0]-VIDEO_SIZE-SLIDE)//VIDEO_SIZE
        start = 0
        for i in range(num_video):
            a_video = trial[start: start+VIDEO_SIZE, :]
            x_tr_video.append(a_video)
            start += SLIDE
    
        value = np.array(x_tr_video)
        x_test_list.append(value)
        y_test_list.append(lab(0, value.shape[0]))
    
    X_test = np.concatenate(x_test_list, axis=0)
    y_test = np.concatenate(y_test_list, axis=0)  
    
    video_images = [gen_images(locs_2D, x, image_size) for x in X_test]
    X_test_video_images = np.array(video_images)
    
    # encode labels as one-hot vectors
    y_train = np_utils.to_categorical(y_train)
    y_test = np_utils.to_categorical(y_test)
    
    
    
    fileName =  str(image_size)+'_'+str(image_size)+'_multichannel_videos'
    np.savez_compressed(fileName, train_video=X_train_video_images, train_labels=y_train, test_video=X_test_video_images, test_labels=y_test)
   
    

def main():
    image_size = 32
    sec = 20
    video_size_single=100
    video_size_multi = 10
    try:
        image_size = int(sys.argv[1])
        sec = int(sys.argv[2])
    except Exception  as e:
        print('Identify image size and second')

        
    print ('Start interpolate videos of ',video_size_single, 'x', image_size, 'x', image_size)    
    create_videos_single(video_size_single, image_size, sec )
    print ('Start interpolate videos of ',video_size_multi, 'x', image_size, 'x', image_size, 'x',2 )
    create_videos_multi(video_size_multi, image_size)
    print('All done!')  
        
# Command line args are in sys.argv[1], sys.argv[2] ..
# sys.argv[0] is the script name itself and can be ignored

# Standard boilerplate to call the main() function to begin
# the program.

if __name__ == '__main__':
      main()      
    
    
    
    
    
        
        
        
        