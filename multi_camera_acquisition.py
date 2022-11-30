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

from config import subjects, data_dir, camera_IDs, bonsai_path, workflow_path, framerate, camera_res, downsample

datetime_str = datetime.now().strftime('%Y-%m-%d-%H%M%S')

b_command = f'{bonsai_path} {workflow_path} --start' # Command to launch Bonsai.

# Append subject specific info to Bonsai launch command.

for box in camera_IDs.keys():
    b_command += f' -p:Box{box}.Index={camera_IDs[box]}'
    if box in subjects.keys(): # Box is being used.
        pinstate_file_path = os.path.join(data_dir, subjects[box] + '_pinstate_' + datetime_str + '.csv')
        b_command += f' -p:Box{box}.Enable=True -p:Box{box}.PinFileName={pinstate_file_path}'
    else: # Box not being used.
        b_command += f' -p:Box{box}.Enable=False -p:Box{box}.PinFileName=temp\\empty{box}.csv'

# Launch Bonsai

bonsai_process = Popen(b_command)

# Launch FFMPEG instances once video pipes are open.

output_res = (camera_res[0]//downsample,camera_res[1]//downsample) if downsample else camera_res

pipes_open = [False for i in subjects.items()]

ffmpeg_processes = []

while not all(pipes_open):
    for i, (box, subject) in enumerate(subjects.items()):
        if not pipes_open[i]:
            pipe = r'\\.\pipe\videopipe' + str(box)
            if pipe.split('\\')[-1] in os.listdir(r'\\.\pipe'):
                pipes_open[i] = True
                video_file_path = os.path.join(data_dir, subject + '_' + datetime_str + '.mp4')
                ffmpeg_processes.append(Popen(
                    fr'ffmpeg -y -f rawvideo -vcodec rawvideo -s {camera_res[0]}x{camera_res[1]} '
                    fr'-pix_fmt gray -r {framerate} -i {pipe} -c:v h264_nvenc '
                    fr'-profile:v high -preset slow -vf scale={output_res[0]}:{output_res[1]} -an {video_file_path}'
                    ))
    time.sleep(0.1)

os.system("title " + 'Camera acquisition') # Set name of terminal window.

# Wait untill Bonsai has stopped running.

while bonsai_process.poll() == None:
    time.sleep(1)

print('Closing ffmpeg processes.')

for ffmpeg_process in ffmpeg_processes:
    ffmpeg_process.terminate()
