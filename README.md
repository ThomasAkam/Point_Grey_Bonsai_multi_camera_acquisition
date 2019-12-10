# Point Grey - Bonsai multi camera acquisition

This repository contains a [Bonsai](https://bonsai-rx.org//introduction/) work-flow and Python script which together:

- Acquire video data and GPIO pin state from multiple Point Grey cameras simultaneously.
- H264 compress the video data on the graphics card (GPU) allowing video data from multiple cameras to be compressed in parallel while minimally loading the CPU.
- Allow the user to specify in a config file which cameras to acquire from and what subject IDs to use for file names from each camera.
- Save the video data as .mp4 files and the GPIO pin state as as .csv files, with file names given by subject_ID and data/time-stamp when acquisition started.

### Dependencies:

- [Python 3](https://www.python.org/)

- [Bonsai 2.4](https://bitbucket.org/horizongir/bonsai/downloads/) with the following libraries installed using the package manager.
  - PointGrey library
  - Vision library
  - Vision design library

- Point Grey FlyCapture SDK version 2.11.3.425, see bonsai user group post [here](https://groups.google.com/forum/#!msg/bonsai-users/Wq2Bo1DnCD8/jb0BfvIVAgAJ) for download link.

- [FFMPEG / libav](https://developer.nvidia.com/ffmpeg) 

- [CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit)

- [NVENC compatible NVIDIA GPU](https://developer.nvidia.com/video-encode-decode-gpu-support-matrix)

- Point Grey Camera

*Note:* Consumer grade NVIDIA GPUs (GeForce) are typically software restricted to support a maximum of 2 concurrent NVENC sessions. The [Keylase driver patch](https://github.com/keylase/nvidia-patch) can be used to remove this restriction allowing video data from more than 2 cameras to be compressed in parallel on a single graphics card.

### Usage

1. **Initial setup** Before you run the program for the first time:
   1. Edit the Bonsai workflow to match the number of cameras connected to your computer, the current workflow is configured for 4 cameras.
   2. In the file *config.py*:
      1. Edit the `camera_IDs` variable to indicate the IDs of the Point Grey cameras on each box.  The IDs are integers which Bonsai uses to identify which camera is which.   If you have 4 cameras the IDs will be 0,1,2,3, but what determines the ordering is unclear. 
      2. Edit the `bonsai_path` variable to indicate the location of the Bonsai executable.  Edit the `workflow_path` variable to indicate the location of the file *multi_recorder_cuda_CLI.bonsai*
   3. In the Point Grey Fly Capture utility, connect to the cameras you will be using and under **Advanced Camera Settings** tick the GPIO pin state box to tell the camera to output the state of the GPIO pins on each frame.  Save the setting to the camera by so they will be maintained after the camera is disconnected, to do this, select channel 1 under Memory Channels and press the save button.
   4. Make sure ffmpeg.exe is on the windows PATH.
2. **Setting up an experiment:**
   1. Edit the `subjects` dictionary to indicate which subject is running in which box.  Remove any boxes from the dictionary that you do not want to acquire data from.
   2. Edit the `data_dir` variable to indicate the directory where data should be saved.
3. **Running an experiment:**
   1. Run the file multi_camera_acquisition.py.  This will launch Bonsai and start acquiring video.
   2. When you have finished the session, press stop on Bonsai, then wait 5 seconds and close Bonsai. **Do not save any changes to the .bonsai file**, doing so will break the program. If you accidentally do so, open the .bonsai file in Bonsai, click on each 'Box' node in turn, look in the 'properties' bar for the variables under the 'Misc' header and ensure the 'PinFileName' variable is set to 'empty.csv' and the 'StartTime' variable is set to '23:00:00'. 

### How it works:

The Bonsai workflow *multi_recorder_cuda_CLI.bonsai* contains a set of identical nested workflows named `Box1`, `Box2` etc, each of which handles acquisition from a single Point Grey camera.  

To allow acquisition from only those cameras specified by the config file `subjects` dictionary, a `Timer` node in combination with `SubscribeWhen` nodes is used to gate whether output from the cameras is saved to file.  

The GPIO pin state data is sent to a `CsvWriter` node to be saved to disk as a .csv file.  The video data is sent to an `ImageWriter` node which pipes the data to an FFMPEG instance which H264 compresses and saves it to disk.

The Python script *multi_camera_acquisition.py*  launches Bonsai from the command line, specifying the workflow to run, and setting the value of workflow variables which specify the camera IDs, whether data  from each camera should be saved, and the file name to use for the .csv files.

Once Bonsai opens pipes to send video data to FFMPEG, the Python script launche an FFMPEG instance for each camera and configures them with the file path to save the data to.

When the script detects that Bonsai has been closed, it closes the FFMPEG instances.
