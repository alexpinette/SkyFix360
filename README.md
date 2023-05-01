# SkyFix360

## Brief introduction

The code is a Python script that creates a GUI (Graphical User Interface) using the PySimpleGUI library. The GUI is for correcting the horizon line in 360-degree images and videos. The GUI has two rows, the first row has an image preview area, and the second row has the options for selecting the folder containing the images or videos, a list of files in the folder, a 'Correct' button for starting the correction process, an 'Export' button for exporting the corrected image or video, a 'Help' button for displaying the help window, and a 'Quit' button for quitting the program.

The code defines several functions for creating different windows, such as the main window, the help window, the correction method selection window, and the success window. The 'runEvents' function is the main loop that handles events in the GUI, such as button clicks, and updates the GUI based on the events.

The script also imports several libraries, such as PySimpleGUI, matplotlib, numpy, PIL, cv2, and sqlalchemy. These libraries are used for various tasks such as creating the GUI, displaying and manipulating images, and working with databases. The project was developed by Nick Croteau, Cathy El-Halal, Anthony Gatti, and Alex Pinette as their final project for the Computer Science program at Wheaton College.


## Installation

To use SkyFix360, you need to install the required dependencies first. You can do this by running the following command in your command prompt:
`pip install -r requirements.txt`

or you can pip install the following:

## Usage

After installing the dependencies, you can run the SkyFix360 tool by executing the `gui.py` file. The program can only run when interacting with the PySimpleGUI window, so there is only one command to run and then nothing will be prompted from the console, only interactions on the window GUI.

`python gui.py`

The tool will launch a PySimpleGUI window where you can load your 360-degree sky image, adjust the parameters and see the output image with the corrected sky. You can customize the output image by adjusting the various parameters available in the window.


## What each file represents

This repository contains the following files:

`auto_fix.py`: contains the necessary functions for automatic horizon line correction on images and videos.
`gui.py`: The main file that runs the PySimpleGUI GUI and emits the events for the corrections for images and videos. The file contains the main code for processing the input image/video and correcting the sky.
`horizon_line_model_new14.h5`: The Artificial Intelligence model that will assist with the automatic correction processes. 
`requirements.txt`: The file containing the list of required dependencies.
`LICENSE`: The file containing the license information for this project.
`README.md`: The file you are currently reading, which contains information about the project and instructions on how to use it.
