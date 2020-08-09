# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 20:28:26 2020

@author: ADI
"""

' IMPORTING FUNCTIONS '
import numpy as np
import sys
import os
import shutil


def read_files() :
    
    if len(sys.argv) == 1 :
        try    :   
            band_yaml = open('band.yaml', 'r').read().split('phonon:')[1]
            vesta     = open('POSCAR.vesta', 'r').read()
        except :  
            print('FILE NOT FOUND : band.yaml & POSCAR.vesta')
            sys.exit(0)
        
    elif len(sys.argv) == 3 :
        try    :   
            band_yaml = open(sys.argv[1], 'r').read().split('phonon:')[1]
            vesta     = open(sys.argv[2], 'r').read()
        except :  
            print('FILES NOT FOUND OR CANNOT OPEN : '
                  '\n %s\n %s \n' %sys.argv[1] %sys.argv[2])
            sys.exit(0)
            
    else : 
        print('FILE NOT FOUND :\n')
        print('Try with' '\n' 'python3 extract_vectors_phonopy.py band.yaml'
              ' POSCAR.vesta')
        sys.exit(0)

    return(band_yaml, vesta)    
    
    
def extract(band_yaml) :
    
    q_point = band_yaml.split('q-position:')[1:]
    q_position = []
    for i in range(len(q_point)) :
        q_position.append(q_point[i].split('[')[1].split(']')[0])

    bands = []
    for band in q_point : 
        if band :
            bands.append(band.split('frequency:')[1:])
    nq_point = len(bands)
    nbands = len(bands[0])
    
    qpoint_band = [['' for band in range(nbands)] for qpoint in range(nq_point)]
    eigenvectors = [['' for band in range(nbands)] for qpoint in range(nq_point)]
    
    for q_point in range(nq_point) :
        for band in range(nbands) :
            data = (bands[q_point][band].split('atom')[1:])
            eigenvectors[q_point][band] = data
            data = float(bands[q_point][band].split('eigenvector')[0])
            qpoint_band[q_point][band] = data
    natoms = len(eigenvectors[0][0]) 
    qpoint_band = np.array(qpoint_band, dtype=float)
               
    displacements = [[[[0 for direction in range(3)] for atom in range(natoms)] 
                    for band in range(nbands)] for qpoint in range(nq_point)]
    
    for q_point in range(nq_point) :
        for band in range(nbands) :
            for atom in range(natoms) :
                vector = eigenvectors[q_point][band][atom]
                for direction in range(3) :
                    data = float(vector.split('[')[direction + 1].split(',')[0])
                    displacements[q_point][band][atom][direction] = data
                    
    displacements = np.array(displacements, dtype=float)
    return(displacements, qpoint_band, q_position)
    # Return Formats : ----------->
    # Displacements [qpoint] [band_index] [atom_index] [direction_index]
    # Contains displacements in given format
    # qpoint_band [qpoint] [band_index]  
    # Contanins frequencies at different q-point
  
def write_VESTA(vesta, displacements, qpoint_band, q_position, scale ):
    
    if not scale :
        scale = 10         # Scaling Factor for vectors    
        
    nqpoint = len(displacements)
    nbands = len(displacements[0])
    natoms = len(displacements[0][0])
    
    path = 'VESTA_FILES'
    if os.path.isdir(path): 
        shutil.rmtree(path)
        os.mkdir(path)
        print('VESTA_FILES ALREADY PRESENT')
        print('OUTPUT VESTA FILES ARE SAVED IN VESTA_FILES')
    else : 
        os.mkdir(path)
        print('OUTPUT VESTA FILES ARE SAVED IN VESTA_FILES')
    
    
    for qpoint in range(nqpoint) :
        
        os.chdir(os.getcwd())
        q_pos = '%.2f' %float(q_position[qpoint].split(',')[0])
        q_pos += '  %.2f' %float(q_position[qpoint].split(',')[1])
        q_pos += '  %.2f' %float(q_position[qpoint].split(',')[2])
        path = 'VESTA_FILES'
        path += '/%s' %q_pos
        if os.path.isdir(path):
            shutil.rmtree(path)
            os.mkdir(path)
        else : os.mkdir(path)
        
        for band in range(nbands) : 
            towrite = vesta.split('VECTR')[0]
            towrite += 'VECTR\n'
            for atom in range(natoms) :  
                towrite += '%5d' %(atom + 1)
                towrite += '%10.5f' %(displacements[qpoint][band][atom][0] * int(scale))
                towrite += '%10.5f' %(displacements[qpoint][band][atom][1] * int(scale))
                towrite += '%10.5f' %(displacements[qpoint][band][atom][2] * int(scale))
                towrite += '\n'
                towrite += '%5d' %(atom + 1)  +  ' 0 0 0 0\n  0 0 0 0 0\n'
            
            towrite += '0 0 0 0 0\n' 
            towrite += 'VECTT\n'
            
            for atom in range(natoms) :
                towrite += '%5d' %(atom + 1)
                towrite += '  0.500 255   0   0 0\n'
                
            towrite += '0 0 0 0 0\n' 
            towrite += 'SPLAN'
            towrite += vesta.split('SPLAN')[1]
                  
            filename = path + '/%d_' %(band + 1)
            filename += '(%.2f)_' %qpoint_band[qpoint][band]
            filename += '.vesta'
            open(filename, 'w').write(towrite)
    
    return(0)
    
    
#------------------------------------------------------
#                       MAIN CODE
#------------------------------------------------------
    
band_yaml, vesta = read_files()
displacements, qpoint_band, q_position = extract(band_yaml)
band_yaml = 0    # Cleaning memory
scale = 5
write_VESTA(vesta, displacements, qpoint_band, q_position, scale)
#-----------------------------------------------------------
# Rough

#-----------------------------------------------------------




