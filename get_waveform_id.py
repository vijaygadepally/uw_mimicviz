#!/usr/bin/env python

import sys
import os

TEMP_FILE = 'temp_waveform_id.txt'
OUTPUT_FILE = 'waveform_id.txt'

def run(drug_name, patient_id):
    ### XXX Submit federated query here...
    return 325553800011

if __name__ == '__main__':
    drug_name = sys.argv[1]
    patient_id = sys.argv[2]
    file_io_directory = sys.argv[3]

    wf_id = run(drug_name, patient_id)

    with open(file_io_directory + TEMP_FILE, 'w') as fh:
        fh.write(str(wf_id))

    os.rename(file_io_directory + TEMP_FILE, file_io_directory + OUTPUT_FILE)
