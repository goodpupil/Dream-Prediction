import warnings
warnings.filterwarnings("ignore")

import h5py
import os, re, sys
import numpy as np
import pandas as pd
import scipy.io as sio


DATA_DIR_REG = './dream_data/'
DATA_DIR_FFT = './dream_data_fft/'

channels_coord = 'channelcoords.mat'
datadir = os.listdir(DATA_DIR_REG)
datadirfft = os.listdir(DATA_DIR_FFT)
SAMPLING_RATE = 500


def readlabels():
    
    # Read trial ids and labels from excel 
    datalabels = pd.read_excel(open('./Dream_reports_healthy.xlsx','rb'),\
                           dtype={'Subject_id':str, 'Quest_number':str, 'Stage':int, 'CE':float, 'Segment excluded':int})
    datalabels.dropna(subset=['CE'], inplace=True)
    datalabels = datalabels[datalabels['Segment excluded'] == 0]
    datalabels.Quest_number = datalabels.Quest_number.apply(lambda x: 'S0'+x if len(x)<2 else 'S'+x)
    return datalabels


def prepare_raw_data(datalabels, second = 20):
    """
    read all data files, create matrix format and save
    second: extract only last given seconds
    """
    print('Reading Raw data')
    # Read and save all data files path and with their names
    datafiles = [] 
    filenames = []
    missingfiles = []
    
    for d in datadir:
        subjectpath = DATA_DIR_REG + d+ '/'
        trialfiles = os.listdir(subjectpath)
        for filename in trialfiles:
            datapath = subjectpath + filename
            #print(datapath)
            filenames.append(filename)
            datafiles.append(datapath)

    print('Total number of .mat files found: ',len(datafiles))
    
    all_data = []
    all_labels = []
    df_ind = []

    for rowid in datalabels.index:
        sid = datalabels.get_value(rowid, 'Subject_id')
        qn = datalabels.get_value(rowid, 'Quest_number')
        label = datalabels.get_value(rowid, 'CE')
        # Find .mat file belongs to this trial
        fname = re.compile(r"^"+sid + "_.*_" + qn+ ".mat")
        fnamelist = list(filter(fname.search, filenames))
        # Check if any match
        if len(fnamelist)>0:
            print(sid, qn , fnamelist)
            ind = filenames.index(fnamelist[0])
            # Find the datapath of file
            fpath = datafiles[ind]
            df_ind.append(ind)
            # read the last 30 second of the file and append it to the list
            arrays = {}
            try :
                f = h5py.File(fpath)
                for k, v in f.items():
                    arrays[k] = np.array(v)

                mydata = (arrays['datavr'])[-(second*SAMPLING_RATE):,0:256]
                all_data.append(mydata)
                all_labels.append(label)
                #print(fpath , 'DONE' )
                f.close()

            except Exception as e:
                print(e)
                missingfiles.append(fpath)


    if len(all_data) == len(datafiles):
        print('In raw, file reading is fine')
    else:
        print('In raw, some files are missed while reading')
        print(len(all_data) , len(datafiles))
        miss = np.setdiff1d(np.arange( len(datafiles)) , np.array( df_ind ))
        for m in miss:
            print('Missing files: ', datafiles[m])


    fileName = str(second)+'sec_raw_data_zip'
    np.savez_compressed(fileName, data=all_data, labels=all_labels)
        
        
def prepare_fft_data(datalabels):
    """
    read all data files, create matrix format and save
    matrix format for each trial is 60 * 512 where first 256 column belongs to delta power and last 256 belong to gamma power
    """
    print('Reading FFT data')
    # Read and save all data files path and with their names
    datafiles = [] 
    filenames = []
    missingfiles = []
    for d in datadirfft:
        subjectpath = DATA_DIR_FFT + d+ '/'
        trialfiles = os.listdir(subjectpath)
        for filename in trialfiles:
            datapath = subjectpath + filename
            #print(datapath)
            filenames.append(filename)
            datafiles.append(datapath)

    print('Total number of .mat files found: ',len(datafiles))

    all_data = []
    all_labels = []
    df_ind = []
    for rowid in datalabels.index:
        sid = datalabels.get_value(rowid, 'Subject_id')
        qn = datalabels.get_value(rowid, 'Quest_number')
        label = datalabels.get_value(rowid, 'CE')
        # Find .mat file belongs to this trial
        fname = re.compile(r"^"+sid + "_.*_" + qn+ "_DeltaGamma.mat")
        fnamelist = list(filter(fname.search, filenames))
        print(sid, qn, fnamelist)
        # Check if any match
        if len(fnamelist)>0:
            #print(sid, qn , fnamelist)
            ind = filenames.index(fnamelist[0])
            # Find the datapath of file
            fpath = datafiles[ind]
            df_ind.append(ind) 
            # read the last 30 second of the file and append it to the list

            try:
                a_trial = sio.loadmat(fpath)
                delta =  a_trial['delta'].T[:,0:256]
                gamma = a_trial['gamma'].T[:,0:256]
                windowed_trial = []
                for ind in range(0, delta.shape[0]):
                    concat = np.concatenate((delta[ind], gamma[ind]), axis=None)
                    windowed_trial.append(concat)  
                two_channel_data = np.asarray(windowed_trial)
                all_data.append(two_channel_data)
                all_labels.append(label)
            except Exception as e:
                print(e)
                print('exception file: ', fpath)
                missingfiles.append(fpath)


    if len(all_data) == len(datafiles):
        print('FFT file reading is fine')
    else:
        print('At FFT, some files are missed while reading')
        print(len(all_data) , len(datafiles))
        miss = np.setdiff1d(np.arange( len(datafiles)) , np.array( df_ind ))
        for m in miss:
            print('Missing files: ', datafiles[m])

    fileName = 'fft_data_zip'
    np.savez_compressed(fileName, data=all_data, labels=all_labels)
        
        
        
        
def main():
    sec = 20
    try:
        sec = int(sys.argv[1])
    except Exception  as e:
        print('How many seconds you want?')

        
    print ('Start reading for ', sec, ' seconds')    
    datalabels = readlabels()
    prepare_raw_data(datalabels, second=sec)
    prepare_fft_data(datalabels)
    print('All done!')  
        
# Command line args are in sys.argv[1], sys.argv[2] ..
# sys.argv[0] is the script name itself and can be ignored

# Standard boilerplate to call the main() function to begin
# the program.

if __name__ == '__main__':
      main()      
        
        
        
        
        

############## TO LOAD ############
# loaded = np.load(fileName+'.npz')
# d = loaded['data']
# l = loaded['labels']
    
    
    
