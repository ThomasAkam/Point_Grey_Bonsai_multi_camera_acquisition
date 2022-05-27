# Script for acquiring video data from multiple Point Grey cameras using Bonsai to 
# extract the state of the GPIO pins and pipe video data to FFMPEG for compression.

# The script launches Bonsai with a command which loads the workflow and configures
# workflow variables to acquire data from the specified boxes.  Once Bonsai has 
# opened pipes to send data to FFMPEG, the script launches FFMPEG instances which 
# use the GPU to H264 compress the video data. When the script detects that Bonsai 
# has been closed it closes the FFMPEG instances.

# (c) Thomas Akam 2019-2022.  Licenced under the GNU General Public License v3.

import os
import time

from datetime import datetime
from subprocess import Popen

from config import subjects, data_dir, camera_IDs, bonsai_path, workflow_path

datetime_str = datetime.now().strftime('%Y-%m-%d-%H%M%S')

command = bonsai_path + ' ' +  workflow_path  + ' --start'

# Append subject specific info to Bonsai launch command.

for box in camera_IDs.keys():
    command += ' -p:Box{}.Index={}'.format(box, camera_IDs[box])
    if box in subjects.keys(): # Box is being used.
        pinstate_file_path = os.path.join(data_dir, subjects[box] + '_pinstate_' + datetime_str + '.csv')
        command += ' -p:Box{}.Enable=True'.format(box) + \
                   ' -p:Box{}.PinFileName={}'.format(box, pinstate_file_path)
    else: # Box not being used.
        command += ' -p:Box{}.Enable=False'.format(box) + \
                   ' -p:Box{}.PinFileName=temp\\empty{}.csv'.format(box, box)

# Launch Bonsai

bonsai_process = Popen(command)

# Launch FFMPEG instances once video pipes are open.

pipes_open = [False for i in subjects.items()]

ffmpeg_processes = []

while not all(pipes_open):
    for i, (box, subject) in enumerate(subjects.items()):
        if not pipes_open[i]:
            pipe = r'\\.\pipe\videopipe' + str(box)
            if pipe.split('\\')[-1] in os.listdir(r'\\.\pipe'):
                pipes_open[i] = True
                video_file_path = os.path.join(data_dir, subject + '_' + datetime_str + '.mp4')
                ffmpeg_processes.append(Popen(r'ffmpeg -y -f rawvideo -vcodec rawvideo -s 1280x1024 -pix_fmt gray -r 60 -i {} -c:v h264_nvenc -profile:v high -preset slow -an {}'.format(pipe, video_file_path)))
    time.sleep(0.1)

os.system("title " + 'Camera acquisition') # Set name of terminal window.

# Wait untill Bonsai has stopped running.

while bonsai_process.poll() == None:
    time.sleep(1)

print('Closing ffmpeg processes.')

for ffmpeg_process in ffmpeg_processes:
    ffmpeg_process.terminate()
