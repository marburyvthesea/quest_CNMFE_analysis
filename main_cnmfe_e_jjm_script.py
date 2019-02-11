
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


# In[2]:

# ## LISTING THE MOVIES & LOADING THE PARAMETERS
# 
# The miniscope recording system usually outputs a set of avi files in one folder. First, give the path of this folder and list all the avi files within it. Then, save a file that list all the parameters in a yaml format (see parameters.yaml in the miniscoPy/example_movies/). It's better to have one parameters.yaml per recording folder (the same for the entire session)

# ### DOWNLOADING AN EXAMPLE FILE IF NOT ALREADY PRESENT

# In[14]:


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

def run_CNMFE(path_to_hdf5_file, folder_name):
# ## WORKING WITH HDF5
# 
# The HDF5 file (called data in this example) contains a Numpy array called 'movie' of size (number of frames, number of pixels). The cool thing about HDF5 format is that you can attach attributes (i.e. extra information) to every dataset or group it contains. Here, we attached the attributes of the frame dimension and the recording duration to the dataset 'movie'.
# load hdf5 file with motion corrected data
	parameters = yaml.load(open(folder_name+'/parameters.yaml', 'r'), Loader=PrettySafeLoader)

	c, procs, n_processes = setup_cluster(backend='local', n_processes=8, single_thread=False)
	print('started cluster')

	data = hd.File(path_to_hdf5_file, 'r+')

	#print(data['movie'].attrs['dims']) # width and height of the frame
	#print(data['movie'].attrs['duration']) # number of frames
	#print(data.attrs['folder'])
	#print(data.attrs['filename'])

# In the following example, the datasets contains additional attributes such as the animal's identity and frame rate. Both are located at the root of the HDF5 file.
# Check the first frame of the movie to see if it's in correct order.

	#dims = data['movie'].attrs['dims']
	#frame_0 = data['movie'][0].reshape(dims)
	#figure()
	#imshow(frame_0)
	#show()

# ## RUNNING CNMF-E 

	parameters['cnmfe']['init_params']['thresh_init'] = 1.2
	parameters['cnmfe']['init_params']['min_corr'] = 0.8
	parameters['cnmfe']['init_params']['min_pnr'] = 1.5

	print('starting cnmfe')
	print('file: ' + path_to_hdf5_file)
	cnm = CNMFE(data, parameters['cnmfe'])
	cnm.fit(procs)


# # VISUALIZATION
##Save A and C output before visualization
	dims = cnm.dims
	C = cnm.C.value.copy()
	A = cnm.A.value.copy()

	# A is normalized to 1 for display
	A -= np.vstack(A.min(1))
	A /= np.vstack(A.max(1))
	Atotal = A.sum(0).reshape(dims)
	out_path = folder_name +'/'
	pd.DataFrame(C).to_hdf(out_path+'C', key='df')
	pd.DataFrame(A).to_hdf(out_path+'A', key='df')


	procs.terminate()

	cn, pnr = cnm.get_correlation_info()

# Here all the spatial footprints (the A matrix) are normalized between 0 and 1 and the sum of all responses is then displayed.

	dims = cnm.dims
	C = cnm.C.value.copy()
	A = cnm.A.value.copy()

	# A is normalized to 1 for display
	A -= np.vstack(A.min(1))
	A /= np.vstack(A.max(1))
	Atotal = A.sum(0).reshape(dims)

#plotting functions

	pd.DataFrame(C).to_hdf(out_path+'C', key='df')
	pd.DataFrame(A).to_hdf(out_path+'A', key='df')
	data.close()

	return()

folder_name = str(sys.argv[1])
motion_corrected_file = str(sys.argv[2])
run_CNMFE(folder_name+'/'+motion_corrected_file, folder_name)

