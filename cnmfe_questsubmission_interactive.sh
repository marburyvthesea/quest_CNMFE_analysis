#!/bin/bash

cd ~

#add project directory to PATH
export PATH=$PATH/projects/p30771/

#load modules to use
module load python/anaconda3.6 

#need to cd to load conda environment

cd pythonenvs
source activate miniscoPy

#need to cd to module directory

cd ..
cd /home/jma819/miniscope/analysis_code/miniscoPy/jjm_module

#run normcorr


python main_cnmfe_e_jjm_script.py /projects/p30771/miniscope/data/GRIN011/1_24_2019/H10_M19_S59 motion_corrected.hdf5
