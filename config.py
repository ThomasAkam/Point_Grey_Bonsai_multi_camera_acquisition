# User config setting for Point Grey Bonsai multi camera acquisition.

# Experiment config.

subjects = {1:'m1',  # {box: subject_ID} 
            2:'m2',
            3:'m3',
            4:'m4'}

data_dir = 'D:\\video_test'  # Directory where data will be saved.

# Hardware config.

camera_IDs = {1: 0,      # {box: camera_index}
              2: 1,
              3: 2,
              4: 3}

# Bonsai path config.

bonsai_path = 'C:\\Bonsai\\Bonsai.exe'

workflow_path = 'C:\\Camera_acquisition\\multi_recorder_cuda_CLI.bonsai'