import os
import json
import scipy.io as spio
import pandas as pd
import re

def loadmat():
    res = ""
    listdir = os.listdir()
    j = 0

    for i in listdir:
        res = re.search("mat", i)
        if res == None:
            continue
        else:
            filename = i
            print(filename)


def read_print_json(liquid):
    # Opening JSON file
    with open('teste.json') as json_file:
        data_dict = json.load(json_file)
        print("Type:", type(data_dict))

        print("\nconfig liquid:", data_dict['config']['liquid'])
        DADOBRUTO = data_dict['A']

        tempo_pulso = data_dict['length']


def _check_keys(dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in dict:
        if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
            dict[key] = _todict(dict[key])
    return dict

def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, spio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict

def mat2json(mat_path, filepath ):
    """
    Converts .mat file to .json and writes new file
    Parameters
    ----------
    mat_path: Str
        Path / filename .mat storage path
    filepath: Str
                 If you need to be saved into JSON, add this path. Otherwise, don't save
    Returns
                 Returns transformed dictionary
    -------
    None
    Examples
    --------    >>> mat2json(blah blah)
    """

    matlabFile = loadmat(mat_path)
    # pop all those dumb fields that don't let you jsonize file
    """    
    matlabFile.pop('__header__')
    matlabFile.pop('__version__')
    matlabFile.pop('__globals__')
    """
    #jsonize the file - orientation is 'index'
    matlabFile = pd.Series(matlabFile).to_json()

    if filepath:
        json_path = os.path.splitext(os.path.split(mat_path)[1])[0] + '.json'
        with open(json_path, 'w') as f:
                f.write(matlabFile)
    return matlabFile


mat2json('teste.mat', 'out.json')