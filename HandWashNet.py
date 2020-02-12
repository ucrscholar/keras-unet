import os


os.environ["CUDA_VISIBLE_DEVICES"] = "2"
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto(allow_soft_placement=False)
config.gpu_options.per_process_gpu_memory_fraction = 1
#config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)

from tensorflow.keras.utils  import HDF5Matrix
from os import path
import numpy as np
import talos
from numpy import save, load
from sklearn.model_selection import train_test_split
import os.path
import HandWashNet1.dbGenerate as db


import h5py

ROOTPATH = '/data1/shengjun/HandWash/'
#ROOTPATH = 'c:/videos/HandWash/'

CURVERSION = 'v1/'
DB = 'db/'
SIZE = 50
SAMPLESNUM = 3000
TRAININGNUM = 2500
DBNUM = str(SAMPLESNUM)


def modelStandard(x_train, y_train, x_val, y_val, params):

    from HandWashNet1.HandWashModels import modelStandard
    SIZE = params['size']
    model = modelStandard(input_shape=(None, SIZE, SIZE, 1), parameter=params);
    '''
    from HandWashNet1.HandWashModels import modelDemoStandardConvLSTMInception
    SIZE = params['size']
    model = modelDemoStandardConvLSTMInception(input_shape=(None, SIZE, SIZE, 1), parameter=params);
    '''
    print(model.summary())
    from tensorflow.keras.utils import plot_model
    plot_model(model, show_shapes=True,
               to_file=params['rootpath'] + params['curversion'] + params['Name'] + '_model.png')

    # if we want to also test for number of layers and shapes, that's possible
    # hidden_layers(model, params, 1)

    history = model.fit(x_train, y_train, batch_size=params['batch_size'],
                        epochs=params['epochs'], validation_split=0.01,
                        shuffle='batch',
                        workers=1,
                        use_multiprocessing=False)

    # evaluate on new data
    loss, acc = model.evaluate(x_val, y_val, verbose=0, batch_size=params['batch_size'])
    print('loss: %f, acc: %f' % (loss, acc * 100))

    # prediction on new data
    yhat = model.predict(x_val, verbose=0, batch_size=params['batch_size'])
    expected = [np.argmax(y, axis=1, out=None) for y in y_val]
    predicted = np.argmax(yhat, axis=2)
    print('Expected: %s, Predicted: %s ' % (expected, predicted))

    # finally we have to make sure that history object and model are returned
    return history, model


def DBA():
    p = {'modelStandard': {'Name': ['modelStandard'],
                           'dbnumber': [DBNUM],
                           'shuff': [False],
                           'size': [50],
                           'rootpath': [ROOTPATH],
                           'curversion': [CURVERSION],
                           'db': [DB],
                           'activation': ['relu', 'elu'],
                           'optimizer': ['AdaDelta', 'Adam'],
                           'losses': ['logcosh'],
                           'shapes': ['brick'],
                           'first_neuron': [32],
                           'dropout': [.2, .3],
                           'cell1': [40, 60],
                           'cell2': [30, 50],
                           'batch_size': [4, 8, 16],
                           'num_layers': [5],
                           'output_activation': ['sigmoid'],
                           'filters': [64],
                           'epochs': [1]},
         }


    if p['modelStandard']['shuff'][0] == False:
        fileNameTrain = ROOTPATH + DB + 'dba_train' + DBNUM
        fileNameLabel = ROOTPATH + DB + 'dba_label' + DBNUM
        if path.exists(fileNameTrain+ '.h5') :
            #X = load(fileNameTrain+ '.npy')
            #y = load(fileNameLabel+ '.npy')
#TODO: mofiy the label with a consit value but not the variable -- fileNameTrain
            X_train = HDF5Matrix(fileNameTrain+'.h5', fileNameTrain, start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', fileNameLabel, start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', fileNameTrain, start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', fileNameLabel, start=TRAININGNUM, end=SAMPLESNUM)

        else:
            X, y = db.generate_DB_A(size=SIZE, n_patterns=SAMPLESNUM, parameter=p['modelStandard'])
            save(fileNameTrain+ '.npy', X)
            save(fileNameLabel+ '.npy', y)
            f = h5py.File(fileNameTrain+'.h5', 'w')
            # Creating dataset to store features
            X_dset = f.create_dataset(fileNameTrain, X.shape, dtype='f')
            X_dset[:] = X
            y_dset = f.create_dataset(fileNameLabel, y.shape, dtype='i')
            y_dset[:] = y
            f.close()
            X_train = HDF5Matrix(fileNameTrain+'.h5', fileNameTrain, start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', fileNameLabel, start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', fileNameTrain, start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', fileNameLabel, start=TRAININGNUM, end=SAMPLESNUM)

    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state=42)
    print("scan modelStandard")
    t = talos.Scan(x=X_train, y=y_train, x_val=X_test, y_val=y_test, params=p['modelStandard'], model=modelStandard,
                   reduction_metric='val_iou', experiment_name='modelStandard_DBA')


def DBARandomOrder():
    p = {'modelStandard': {'Name': ['modelStandard'],
                           'dbnumber': [DBNUM],
                           'shuff': [True],
                           'size': [50],
                           'rootpath': [ROOTPATH],
                           'curversion': [CURVERSION],
                           'db': [DB],
                           'activation': ['relu', 'elu'],
                           'optimizer': ['AdaDelta', 'Adam'],
                           'losses': ['logcosh'],
                           'shapes': ['brick'],
                           'first_neuron': [32],
                           'dropout': [.2, .3],
                           'cell1': [40, 60],
                           'cell2': [30, 50],
                           'batch_size': [4, 8, 16],
                           'num_layers': [5],
                           'output_activation': ['sigmoid'],
                           'filters': [64],
                           'epochs': [1]},
         }

    if p['modelStandard']['shuff'][0] == True:
        fileNameTrain = ROOTPATH + DB + 'dba_train_shuff' + DBNUM
        fileNameLabel = ROOTPATH + DB + 'dba_label_shuff' + DBNUM
        if path.exists(fileNameTrain+'.h5'):
            #X = load(fileNameTrain+ '.npy')
            #y = load(fileNameLabel+ '.npy')

            X_train = HDF5Matrix(fileNameTrain+'.h5', fileNameTrain, start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', fileNameLabel, start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', fileNameTrain, start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', fileNameLabel, start=TRAININGNUM, end=SAMPLESNUM)

        else:
            X, y = db.generate_DB_A(size=SIZE, n_patterns=SAMPLESNUM, parameter=p['modelStandard'])
            save(fileNameTrain+ '.npy', X)
            save(fileNameLabel+ '.npy', y)
            f = h5py.File(fileNameTrain+'.h5', 'w')
            # Creating dataset to store features
            X_dset = f.create_dataset(fileNameTrain, X.shape, dtype='f')
            X_dset[:] = X
            y_dset = f.create_dataset(fileNameLabel, y.shape, dtype='i')
            y_dset[:] = y
            f.close()

            X_train = HDF5Matrix(fileNameTrain+'.h5', fileNameTrain, start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', fileNameLabel, start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', fileNameTrain, start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', fileNameLabel, start=TRAININGNUM, end=SAMPLESNUM)
            

    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state=42)
    print("scan modelStandard")
    t = talos.Scan(x=X_train, y=y_train, x_val=X_test, y_val=y_test, params=p['modelStandard'], model=modelStandard,
                   reduction_metric='val_iou', experiment_name='modelStandardR_DBARandomOrder')


def DBB():
    p = {'modelStandard': {'Name': ['modelStandard'],
                           'dbnumber': [DBNUM],
                           'shuff': [False],
                           'size': [50],
                           'rootpath': [ROOTPATH],
                           'curversion': [CURVERSION],
                           'db': [DB],
                           'activation': ['relu', 'elu'],
                           'optimizer': ['AdaDelta', 'Adam'],
                           'losses': ['logcosh'],
                           'shapes': ['brick'],
                           'first_neuron': [32],
                           'dropout': [.2, .3],
                           'cell1': [40, 60],
                           'cell2': [30, 50],
                           'batch_size': [4, 8, 16],
                           'num_layers': [5],
                           'output_activation': ['sigmoid'],
                           'filters': [64],
                           'epochs': [1]},
         }

    if p['modelStandard']['shuff'][0] == False:

        fileNameTrain = ROOTPATH + DB + 'dbb_train' + DBNUM
        fileNameLabel = ROOTPATH + DB + 'dbb_label' + DBNUM
        if path.exists(fileNameTrain+'.h5'):
            #X = load(fileNameTrain+ '.npy')
            #y = load(fileNameLabel+ '.npy')

            X_train = HDF5Matrix(fileNameTrain+'.h5', fileNameTrain, start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', fileNameLabel, start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', fileNameTrain, start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', fileNameLabel, start=TRAININGNUM, end=SAMPLESNUM)

        else:
            X, y = db.generate_DB_B(size=SIZE, n_patterns=SAMPLESNUM, parameter=p['modelStandard'])
            save(fileNameTrain+ '.npy', X)
            save(fileNameLabel+ '.npy', y)
            f = h5py.File(fileNameTrain+'.h5', 'w')
            # Creating dataset to store features
            X_dset = f.create_dataset(fileNameTrain, X.shape, dtype='f')
            X_dset[:] = X
            y_dset = f.create_dataset(fileNameLabel, y.shape, dtype='i')
            y_dset[:] = y
            f.close()

            X_train = HDF5Matrix(fileNameTrain+'.h5', fileNameTrain, start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', fileNameLabel, start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', fileNameTrain, start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', fileNameLabel, start=TRAININGNUM, end=SAMPLESNUM)

    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state=42)
    print("scan modelStandard")
    t = talos.Scan(x=X_train, y=y_train, x_val=X_test, y_val=y_test, params=p['modelStandard'], model=modelStandard,
                   reduction_metric='val_iou', experiment_name='modelStandard_DBB')


def DBBRandomOrder():
    p = {'modelStandard': {'Name': ['modelStandard'],
                           'dbnumber': [DBNUM],
                           'shuff': [True],
                           'size': [50],
                           'rootpath': [ROOTPATH],
                           'curversion': [CURVERSION],
                           'db': [DB],
                           'activation': ['relu', 'elu'],
                           'optimizer': ['AdaDelta', 'Adam'],
                           'losses': ['logcosh'],
                           'shapes': ['brick'],
                           'first_neuron': [32],
                           'dropout': [.2, .3],
                           'cell1': [40, 60],
                           'cell2': [30, 50],
                           'batch_size': [4, 8, 16],
                           'num_layers': [5],
                           'output_activation': ['sigmoid'],
                           'filters': [64],
                           'epochs': [1]},
         }

    if p['modelStandard']['shuff'][0] == True:
        fileNameTrain = ROOTPATH + DB + 'dbb_train_shuff' + DBNUM
        fileNameLabel = ROOTPATH + DB + 'dbb_label_shuff' + DBNUM
        if path.exists(fileNameTrain+'.h5') :
            #X = load(fileNameTrain+ '.npy')
            #y = load(fileNameLabel+ '.npy')

            X_train = HDF5Matrix(fileNameTrain+'.h5', 'c:/videos/HandWash/db/dbb_train_shuff3000', start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', 'c:/videos/HandWash/db/dbb_label_shuff3000', start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', 'c:/videos/HandWash/db/dbb_train_shuff3000', start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', 'c:/videos/HandWash/db/dbb_label_shuff3000', start=TRAININGNUM, end=SAMPLESNUM)

        else:
            X, y = db.generate_DB_B(size=SIZE, n_patterns=SAMPLESNUM, parameter=p['modelStandard'])
            save(fileNameTrain+ '.npy', X)
            save(fileNameLabel+ '.npy', y)
            f = h5py.File(fileNameTrain+'.h5', 'w')
            # Creating dataset to store features
            X_dset = f.create_dataset('Train', X.shape, dtype='f')
            X_dset[:] = X
            y_dset = f.create_dataset('Label', y.shape, dtype='i')
            y_dset[:] = y
            f.close()
            X_train = HDF5Matrix(fileNameTrain+'.h5', 'Train', start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', 'Label', start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', 'Train', start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', 'Label', start=TRAININGNUM, end=SAMPLESNUM)


    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state=42)
    print("scan modelStandard")
    t = talos.Scan(x=X_train, y=y_train, x_val=X_test, y_val=y_test, params=p['modelStandard'], model=modelStandard,
                   reduction_metric='val_iou', experiment_name='modelStandard_DBBRandomOrder')


def DBC():
    p = {'modelStandard': {'Name': ['modelStandard'],
                           'dbnumber': [DBNUM],
                           'shuff': [False],
                           'size': [50],
                           'rootpath': [ROOTPATH],
                           'curversion': [CURVERSION],
                           'db': [DB],
                           'activation': ['relu', 'elu'],
                           'optimizer': ['AdaDelta', 'Adam'],
                           'losses': ['logcosh'],
                           'shapes': ['brick'],
                           'first_neuron': [32],
                           'dropout': [.2, .3],
                           'cell1': [40, 60],
                           'cell2': [30, 50],
                           'batch_size': [4, 8, 16],
                           'num_layers': [5],
                           'output_activation': ['sigmoid'],
                           'filters': [64],
                           'epochs': [1]},
         }


    if p['modelStandard']['shuff'][0] == False:
        fileNameTrain = ROOTPATH + DB + 'dbc_train' + DBNUM
        fileNameLabel = ROOTPATH + DB + 'dbc_label' + DBNUM
        if path.exists(fileNameTrain+'.h5'):
            #X = load(fileNameTrain+ '.npy')
            #y = load(fileNameLabel+ '.npy')

            X_train = HDF5Matrix(fileNameTrain+'.h5', 'c:/videos/HandWash/db/dbc_train3000', start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', 'c:/videos/HandWash/db/dbc_label3000', start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', 'c:/videos/HandWash/db/dbc_train3000', start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', 'c:/videos/HandWash/db/dbc_label3000', start=TRAININGNUM, end=SAMPLESNUM)

        else:
            X, y = db.generate_DB_C(size=SIZE, n_patterns=SAMPLESNUM, parameter=p['modelStandard'])
            save(fileNameTrain+ '.npy', X)
            save(fileNameLabel+ '.npy', y)
            f = h5py.File(fileNameTrain+'.h5', 'w')
            # Creating dataset to store features
            X_dset = f.create_dataset(fileNameTrain, X.shape, dtype='f')
            X_dset[:] = X
            y_dset = f.create_dataset(fileNameLabel, y.shape, dtype='i')
            y_dset[:] = y
            f.close()

            X_train = HDF5Matrix(fileNameTrain+'.h5', fileNameTrain, start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', fileNameLabel, start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', fileNameTrain, start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', fileNameLabel, start=TRAININGNUM, end=SAMPLESNUM)

    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state=42)
    print("scan modelStandard")
    t = talos.Scan(x=X_train, y=y_train, x_val=X_test, y_val=y_test, params=p['modelStandard'], model=modelStandard,
                   reduction_metric='val_iou', experiment_name='modelStandard_DBC')


def DBCRandomOrder():
    p = {'modelStandard': {'Name': ['modelStandard'],
                           'dbnumber': [DBNUM],
                           'shuff': [True],
                           'size': [50],
                           'rootpath': [ROOTPATH],
                           'curversion': [CURVERSION],
                           'db': [DB],
                           'activation': ['relu', 'elu'],
                           'optimizer': ['AdaDelta', 'Adam'],
                           'losses': ['logcosh'],
                           'shapes': ['brick'],
                           'first_neuron': [32],
                           'dropout': [.2, .3],
                           'cell1': [40, 60],
                           'cell2': [30, 50],
                           'batch_size': [4, 8, 16],
                           'num_layers': [5],
                           'output_activation': ['sigmoid'],
                           'filters': [64],
                           'epochs': [1]},
         }


    if p['modelStandard']['shuff'][0] == True:
        fileNameTrain = ROOTPATH + DB + 'dbc_train_shuff' + DBNUM
        fileNameLabel = ROOTPATH + DB + 'dbc_label_shuff' + DBNUM
        if path.exists(fileNameTrain+'.h5'):
            #X = load(fileNameTrain+ '.npy')
            #y = load(fileNameLabel+ '.npy')


            X_train = HDF5Matrix(fileNameTrain+'.h5', 'c:/videos/HandWash/db/dbc_train_shuff3000', start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', 'c:/videos/HandWash/db/dbc_label_shuff3000', start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', 'c:/videos/HandWash/db/dbc_train_shuff3000', start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', 'c:/videos/HandWash/db/dbc_label_shuff3000', start=TRAININGNUM, end=SAMPLESNUM)

        else:
            X, y = db.generate_DB_C(size=SIZE, n_patterns=SAMPLESNUM, parameter=p['modelStandard'])
            save(fileNameTrain+ '.npy', X)
            save(fileNameLabel+ '.npy', y)
            f = h5py.File(fileNameTrain+'.h5', 'w')
            # Creating dataset to store features
            X_dset = f.create_dataset(fileNameTrain, X.shape, dtype='f')
            X_dset[:] = X
            y_dset = f.create_dataset(fileNameLabel, y.shape, dtype='i')
            y_dset[:] = y
            f.close()

            X_train = HDF5Matrix(fileNameTrain+'.h5', fileNameTrain, start=0, end=TRAININGNUM)
            y_train = HDF5Matrix(fileNameTrain+'.h5', fileNameLabel, start=0, end=TRAININGNUM)
            X_test = HDF5Matrix(fileNameTrain + '.h5', fileNameTrain, start=TRAININGNUM, end=SAMPLESNUM)
            y_test = HDF5Matrix(fileNameTrain + '.h5', fileNameLabel, start=TRAININGNUM, end=SAMPLESNUM)


    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.01, random_state=42)
    print("scan modelStandard")
    t = talos.Scan(x=X_train, y=y_train, x_val=X_test, y_val=y_test, params=p['modelStandard'], model=modelStandard,
                   reduction_metric='val_iou', experiment_name='modelStandard_DBCRandomOrder')


if __name__ == "__main__":
    tag = {0: 'NailWashLeft', 1: 'NailWashRight', 2: 'ThumbFingureWash', 3: 'ForeFingureWash'}
    inv_tag = {v: k for k, v in tag.items()}


    print('DBA============================================')
    DBA()
    print('DBARandomOrder===================================')
    DBARandomOrder()
    print('DBB==============================================')
    DBB()
    print('DBBRandomOrder==================================')
    DBBRandomOrder()
    print('DBC=============================================')
    DBC()
    print('DBCRandomOrder==================================')
    DBCRandomOrder()


