<p align="center">
  <img style="width:30%;" src="https://github.com/alexpinette/SkyFix360/blob/main/logo.png" alt="SkyFix360 Logo">
</p>

# SkyFix360

## Brief introduction

The code is a Python script that creates a GUI (Graphical User Interface) using the PySimpleGUI library. The GUI is for correcting the horizon line in 360-degree images and videos. The GUI has two rows, the first row has an image preview area, and the second row has the options for selecting the folder containing the images or videos, a list of files in the folder, a 'Correct' button for starting the correction process, an 'Export' button for exporting the corrected image or video, a 'Help' button for displaying the help window, and a 'Quit' button for quitting the program.

The code defines several functions for creating different windows, such as the main window, the help window, the correction method selection window, and the success window. The 'runEvents' function is the main loop that handles events in the GUI, such as button clicks, and updates the GUI based on the events.

The script also imports several libraries, such as PySimpleGUI, matplotlib, numpy, PIL, cv2, and sqlalchemy. These libraries are used for various tasks such as creating the GUI, displaying and manipulating images, and working with databases. The project was developed by Nick Croteau, Cathy El-Halal, Anthony Gatti, and Alex Pinette as their final project for the Computer Science program at Wheaton College.


## Installation

### MAC

1. Go to the website: <a href="https://www.dropbox.com/sh/g7qz13tizm3xzk8/AACKXtNQkG8LShkBm-kQo8Xda?dl=0" target="_blank">Dropbox Link</a>
2. Look for a download link called `SkyFix360Mac.zip` for the Mac version of the app.
3. Click on the download link and a download dialogue box should appear.
4. Once the download is complete, locate the downloaded file in your Downloads folder or wherever you saved it. It is greatly recommended that you keep the default location settings and do not move any of the folders that the program creates.
5. Unzip downloaded folder if it did not unzip yet.
6. Double-click on the file to start the installation process. If the file is in a compressed format like .zip or .dmg, you may need to extract it first.
7. If you see a warning message saying that the app is from an unidentified developer, you may need to allow permission from Security and Privacy settings on your Mac.
8. To do this, go to System Preferences > Security & Privacy. Under the General tab, you should see a message saying that the app was blocked. Click on the "Open Anyway" button next to it to allow the app to run.
9. Follow the on-screen instructions to complete the installation process. Once the installation is complete, the application will automatically open on the screen.


### Windows

1. Go to the website: <a href="https://www.dropbox.com/sh/g7qz13tizm3xzk8/AACKXtNQkG8LShkBm-kQo8Xda?dl=0" target="_blank">Dropbox Link</a>
2. Look for a download link called `SkyFix360Windows.zip` for the Windows version of the app.
3. Click on the download link, and a download dialogue box should appear.
4. Once the download is complete, locate the downloaded file in your Downloads folder or wherever you saved it.
4. Double-click on the downloaded file to start the installation process.
5. If you see a warning message from your computer's security software, click "Run" to proceed with the installation.
6. Follow the on-screen instructions to complete the installation process. You may need to select an installation location, agree to terms and conditions, and customize the installation options. It is greatly recommended that you keep the default location settings and do not move any of the folders that the program creates.
7. Unzip downloaded folder.
8. Once the installation is complete, you should see the app icon on your desktop and the application will automatically open on the screen.


### Linux

1. Go to the website: <a href="https://www.dropbox.com/sh/g7qz13tizm3xzk8/AACKXtNQkG8LShkBm-kQo8Xda?dl=0" target="_blank">Dropbox Link</a>
2. Look for a download link called `SkyFix360SLinux.zip` for the Linux version of the app.
3. Click on the download link, and a download dialogue box should appear.
4. Once the download is complete, locate the downloaded file in your Downloads folder or wherever you saved it.
5. Open the terminal and navigate to the directory where you downloaded the file.
6. If the file is in a compressed format like .zip or .tar.gz, you may need to extract it first. You can use the "tar" command to extract the file. For example, if the file is named "app.tar.gz", you can use the command "tar -xzvf app.tar.gz" to extract the files.
7. Run the file by entering the command `chmod +x SkyFix360SLinuxScript.sh` in the terminal, where "SkyFix360SLinuxScript" is the name of the file you downloaded for Linux.
8. Run `./SkyFix360SLinuxScript.sh` so the application starts running automatically.


## What each file represents

This repository contains the following files:

`auto_fix.py`: contains the necessary functions for automatic horizon line correction on images and videos. <br/>

`gui.py`: The main file that runs the PySimpleGUI GUI and emits the events for the corrections for images and videos. The file contains the main code for processing the input image/video and correcting the sky. <br />

`LICENSE`: The file containing the license information for this project.<br />

`horizon_line_modelFINAL.h5`:  The saved Keras model containing all of the weights and the model architecture. <br />

`README.md`: The file you are currently reading, which contains information about the project and instructions on how to use it. <br />
