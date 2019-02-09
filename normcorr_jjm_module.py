
# coding: utf-8

# # Testing MiniscoPy with true data
# 
# MiniscopPy is a Python 3.0 implementation of the CNMF-E algorithm (Zhou et al., 2016). It has been optimized for the MiniScope (Cai et al., 2016), a portable microscope for calcium imaging in freely moving animals.
# 

# ## BASIC IMPORTS

## Designed to run as self contained script from command line on quest


import warnings
warnings.filterwarnings('ignore')
import numpy as np
from time import time
from matplotlib.pyplot import *
import scipy
import glob
import yaml
import sys,os
import h5py as hd
from time import time
import av
#specific to miniscopy
from motion_correction_jjm import *
from miniscopy import setup_cluster, CNMFE, generate_data, get_default_parameters
import tables
#import dview


def load_movies(folder_name):

	files = glob.glob(folder_name+'/msCam*.avi')
	if len(files) == 0:
		import urllib.request
		url = "https://www.dropbox.com/s/0x3twp8bidl9svu/msCam1.avi?dl=1"
		with urllib.request.urlopen(url) as response, open(folder_name+"/msCam1.avi", 'wb') as out_file:
			data = response.read()
			out_file.write(data)
		files = glob.glob(folder_name+'/*.avi')
		if len(files) == 0: print("No avi files found, please provide one at least")

	return(files) 	

## for loading parameter file 

class PrettySafeLoader(yaml.SafeLoader):
	def construct_python_tuple(self, node):
		return tuple(self.construct_sequence(node))

	def construct_python_list(self, node):
		return tuple(self.construct_sequence(node))

PrettySafeLoader.add_constructor(
	u'tag:yaml.org,2002:python/tuple',
	PrettySafeLoader.construct_python_tuple)

PrettySafeLoader.add_constructor(
	u'tag:yaml.org,2002:python/list',
	PrettySafeLoader.construct_python_list)


def run_normcorr(folder_name,files):

	parameters = yaml.load(open(folder_name+'/parameters.yaml', 'r'), Loader=PrettySafeLoader)

# ## STARTING THE CLUSTER 
# For now, pool mapping is used only for the motion correction algorithm. Instantiating "procs = None" works as well, it all depends on your local configuration.

	c, procs, n_processes = setup_cluster(backend='local', n_processes=8, single_thread=False)
	print('started cluster')

# ## MOTION CORRECTION
 # This function implements Normcorre (see...). All the outputs and associated information are stored in one HDF5 per session that will eventually be used for detection of calcium transients. 

	files_to_load = [str(file) for file in files[:]]

	print('processing files')
	print(files_to_load)

	data, video_info = normcorre(files_to_load, procs, parameters['motion_correction'])

	data.close()

	print('finished motion correction')
	video_info # some information about the dataset

	return()



