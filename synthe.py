import re
import time
import subprocess

import numpy as np

import user_settings

hardcoded_delta = 0.8

def run_synthe(params, model):
    with open('synthe/current_synthe.sh', 'w') as current_synthe:
        current_synthe.writelines('\n'.join([
                '#! /bin/bash',
                f'EXE={user_settings.kurucz_bin_dir}',
                'export EXE',
                f'LIN={user_settings.atomic_line_dir}',
                'export LIN',
                f'MOL={user_settings.molecular_line_dir}',
                'export MOL',
                f'MODEL={model}',
                'export MODEL',
                f'VMAC="{float(params["vmac"]):.2f}"',
                'export VMAC',
                f'VROT="{float(params["vrot"]):.2f}"',
                'export VROT',
                f'RESOLUTION="{str(params["resolution"]).ljust(6, " ")}"',
                'export RESOLUTION',
                f'blue={float(params["center"]) - hardcoded_delta:.1f}',
                'export blue',
                f'red={float(params["center"]) + hardcoded_delta:.1f}',
                'export red',
                './synthe.sh > synthe.log'
            ])
        )
    
    subprocess.call(['sh', './current_synthe.sh'], cwd='synthe/')
    
    time.sleep(user_settings.FIT_DELAY)

def update_model(params, abn, model):                                                                                   
    with open(model, 'r') as mod_file:                                 
        mod_lines = mod_file.readlines()
        
    abundance_scale = [a for a in mod_lines[4].split(' ') if a != ''][2]
    abundance_scale = np.abs(np.log10(float(abundance_scale)))
                                                                                
    element = params['elmt']
    abn_pattern = f' {element}' + r' -([\.0-9]{5})(.*$)' 

    for i, line in enumerate(mod_lines[4:22]):
        # find desired element
        if True in [s == element for s in line.split(' ')]:
            el_line = i + 4
            abn_row = np.argmax(np.array([s == element for s in line.split(' ')]))
            line_before = ' '.join(mod_lines[el_line].split(' ')[0:abn_row]) + ' ' + element
            line_after = ' '.join(mod_lines[el_line].split(' ')[abn_row+1:])
            break
        # line_after can either start with a space ( -x.xx) or with a negative sign (-xx.xx)
        # the first six characters immediately after the element will be its abundance
    current_abn = line_after[:6]
    line_after = line_after[6:]                                                    

    new_abn = f'{float(abn) - 12.04 + abundance_scale:.2f}'.rjust(7)
    mod_lines[el_line] = line_before + new_abn + line_after         

    # Set microturbulence speed in the model atmosphere
    mdl = mod_lines[23:95]
    for i in range(len(mdl)):
        n = mdl[i].split(' ')
        n[-4] = user_settings.VTURB
        mdl[i] = ' '.join(n)
    mod_lines[23:95] = mdl
                                                                                
    with open(model, 'w') as mod_file:                                 
        mod_file.writelines(mod_lines)
