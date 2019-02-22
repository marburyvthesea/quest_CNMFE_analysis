#!/bin/bash
#MSUB -A p30771
#MSUB -q short
#MSUB -l walltime=1:00:00
#MSUB -M johnjmarshall@u.northwestern.edu
#MSUB -j oe
#MSUB -N CNMFE
#MSUB -l nodes=1:ppn=12
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


python main_cnmfe_e_jjm_script.py /projects/p30771/miniscope/data/GRIN011/1_24_2019/H10_M19_S59/mmmap_files H10_M19_S59msCam9_rig__d1_480_d2_752_d3_1_order_F_frames_1000_2d_forquest_cnmfe.hdf5
