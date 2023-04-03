'''
    NCAA
    GUI.py
    Senior Seminar 2023
'''

import PIL
import os
import io
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import sys
import cv2
import matplotlib.image as mpimg
import textwrap
import tkinter as tk

from PIL import Image, ImageFilter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from equirectRotate import EquirectRotate

from auto_fix import auto_correct_process


#------------------------------------------------------------------------------
global prevButtonClickedOnce
global doneButtonClickedOnce


def createWindow():
    """ 
        Args:     None
        Returns:  window --> list: The main layout of the program. List of many PySimpleGUI elements 
        Summary:  Creates the main GUI window for the SkyFix360 application with all necessary elements and returns it.
    """
    sg.theme ("DarkGrey1")

    manualDescription = "Click the lowest and highest points of the horizon. To remove the most recent point, press 'z'. Once you are done, click the 'Done' button. If you wish to restart, click the 'Restart' button and try again."
    newManualDescription = textwrap.fill(manualDescription, 52)


    firstRow = [[ sg.Button('<', key='-PREVIOUS BTN-', visible=False, size=(5, 1)),
                  sg.Text('', key='-SPACE1-', visible=True, expand_x=True),
                  sg.Text('File', font="Arial 10 bold", size=(4,1), key='-FILETEXT-', justification='center'), 
                  sg.Input('', key='-FILENAME-', disabled=True, justification='center'),
                  sg.Text('    ', key='-SPACE2-', visible=True, expand_x=True),
                ],

                [sg.Image(key='-IMAGE-', background_color = 'black', size=(1000, 500))],
                [sg.Text('Progress: ', font='Arial 10 bold', key='-ProgressText-', visible=False),
                 sg.ProgressBar(100, orientation='h', size=(15, 15), key='-ProgressBar-',  bar_color='#FFFFFF', visible=False)],
                [sg.Canvas(key='fig_cv', size=(1000, 500), visible=False)]
               ]

    secondRow = [ #first col
        [sg.Column([[sg.Text("SkyFix360", key='-TITLE-', font= ("Arial", 16, "bold"), size=(200, 1))],
                    [sg.Text(newManualDescription, key='-MANUAL DESCRIPTION-', font=("Arial", 10), visible=False, size=(52, 4))],
                    [sg.In (size=(40,1), enable_events=True, key="-FOLDER-"),
                     sg.FolderBrowse(key='-BROWSE-', size=(10, 1))]], pad=(10, 10), size=(400, 100), key="-FOLDROW-"),
    
         #second col
         sg.Column([[sg.Listbox(values=[], enable_events=True, size=(45,5), key="-FILE LIST-")]], size=(300, 85)),

         #third col
         sg.Column([
         [sg.Button('Correct', key='-CORRECT-', disabled=True, button_color=('grey', sg.theme_button_color_background()), size=(10, 1))],
         [sg.Button('Export', key='-EXPORT-', disabled=True, button_color=('grey', sg.theme_button_color_background()), size=(10, 1))],
         [sg.Button('Done', key='-DONE-', visible=False, size=(10, 1))],
         [sg.Button('Restart', key='-RESTART-', visible=False, size=(10, 1))],
         ])
        ],
        [sg.Text("", pad=(0,66), key="-PAD FOR CORRECTION-", visible=False)],
        [sg.Button('Help', key='-HELP-', size=(10, 1)), sg.Button("Quit", key="-QUIT-", size=(10, 1))]
    ] 

    layout = [ firstRow, secondRow ]

    # Display the window
    window = sg.Window ("SkyFix360", layout, element_justification='c', resizable = True, finalize = True)
    
    # bind to config so can check when window size changes
    window.bind('<Configure>', '-CONFIG-')
    
    # bind the closeAllWindows function to the WM_DELETE_WINDOW event of the main window
    window.TKroot.protocol("WM_DELETE_WINDOW", closeAllWindows)

    return window


########### FIXME: MAKE WINDOW LARGER
# ------------------------------------------------------------------------------  
def helpWindow():
    """ 
        Args:     None
        Returns:  helpLayout --> list: The layout as a list of PySimpleGUI text elements to help the user if he/she is confused.
        Summary:  This function creates a help window layout using PySimpleGUI, which provides a step-by-step guide on how to 
                  use the photo/video correction application. The function returns the layout as a list of PySimpleGUI elements.
    """
    
    helpLayout = [[sg.Text(' Need Help?', font=("Arial", 16, "bold"), size=(40, None), justification='center')],
              [sg.Text("   1.   Click the 'Browse' button to select a folder containing any\n         images or videos.", font=("Arial", 12))],
              [sg.Text("   2.   Files ending with .MP4, .JPEG, and .JPG will appear in the\n         white space to the right.", font=("Arial", 12))],
              [sg.Text("   3.   Select an image/video from this panel. It will then be\n        shown on the preview screen above.", font=("Arial", 12))],
              [sg.Text("   4.   Click 'Correct' button to begin the correction process. Follow\n         the steps in the pop-up window.", font=("Arial", 12))],
              [sg.Text("   5.   Select 'Export' to save your corrected photo/video to\n         your device.", font=("Arial", 12))],
              [sg.Text("   6.   If you wish to quit at any time, select the 'Quit' button.", font=("Arial", 12))],
              [sg.Button("Close",font=("Arial", 12), size=(10, 1), pad=((135), (20, 0)))]
             ]

    return helpLayout


# ------------------------------------------------------------------------------  
def correctMethodWindow():
    """ 
        Args:     None
        Returns:  correctionLayout --> list: The layout as a list of PySimpleGUI text and button elements
        Summary:  This function creates a correction method window layout using PySimpleGUI, which allows
                  the user to choose between manual and automatic correction methods. The function returns 
                  the layout as a list of PySimpleGUI elements.
    """
    correctionLayout = [ [sg.Text('Choose a Correction Method', font=("Arial", 16, "bold"), size=(40, None), auto_size_text=True, justification='center', pad=(0, 5))],      
                         [sg.Button('Manual', size=(10,1)), sg.Text('This method allows for custom specification \nof the horizon by a drawing from the user.\n')], 
                         [sg.Button('Automatic', size=(10,1)), sg.Text('This method automaticaaly finds the horizon \nline and corrects the image/video.')], 
                         [sg.Button("Cancel", size=(10, 1), pad=((135), (20, 0)))]]
    return correctionLayout



########### FIXME: MAKE WINDOW LARGER
# ------------------------------------------------------------------------------  
def successWindow():
    """ 
        Args:      None
        Returns:   successLayout --> list: The layout as a list of PySimpleGUI text and button elements.
        Summary:   This function creates a success window layout using PySimpleGUI, which notifies the 
                   user that their image or video has been successfully corrected. The function returns
                   the layout as a list of PySimpleGUI elements.
    """

    successLayout = [[sg.Text('Your image/video has been successfully corrected.', font=("Arial", 18), size=(25, None), auto_size_text=True, justification='center')],
                     [sg.Text('Close this window and click the "Export" button to save your photo/video to your device.', size=(40, None), auto_size_text=True, justification='center', pad=(15, 10))],
                     [sg.Button("Close", size=(10, 1), pad=(100, 5))]]
    
    return successLayout


# ------------------------------------------------------------------------------  
def runEvents(window):
    """ 
        Args:      window --> PySimpleGUI Window: the main window of the application
        Returns:   None
        Summary:   This function handles the event loop of the application.
                   It listens for events triggered by the user and responds accordingly.
    """

    fileNames = []
    prevButtonClickedOnce = False # Will help with fixing correction window displaying incorrectly
    doneButtonClickedOnce = False # Will help with fixing correction window displaying incorrectly
    
    automaticCorrectedOnce = False # Will help with fixing correction window displaying incorrectly
    correctionsCompleted = 0       # Will help with fixing correction window displaying incorrectly
        
    while True:
        event, values = window.read()
                
        # if user selects 'Help' button, display help window with instructions
        if event == ('-HELP-'):
            helplayout = helpWindow()
            help = sg.Window('Help', helplayout, size=(405, 330), margins=(15, 15))
            while True:
                helpEvent, helpValues = help.read()
                if helpEvent == sg.WIN_CLOSED or helpEvent == ('Close'):
                    # Close the help popup
                    help.close()
                    break
        
        # when user selects 'Browse', find folder & update elements
        if event == ('-FOLDER-'):
            # get actual folder that was chosen
            folder = values["-FOLDER-"]
            try:
                # get list of files in chosen folder
                fileList = os.listdir (folder)
            except:
                # no files found!
                fileList = []   

            # list of filenames that are in the chosen folder that end with .jpg, .jpeg, .mp4
            fileNames = [
                f
                for f in fileList
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".jpg", ".jpeg", ".mp4"))
            ]
            # add the filenames to the image file list in first column
            window["-FILE LIST-"].update(fileNames)

        # User chose file from File List
        if event == "-FILE LIST-":   
            try:
                fileName = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
                
                # display filename in appropriate spot in right column
                window["-FILENAME-"].update(fileName)  
                
                # Open the image
                pilImage = PIL.Image.open(fileName)
                
                # Get image data, and then use it to update window["-IMAGE-"]
                data = imageToData(pilImage, window["-IMAGE-"].get_size())
                window['-IMAGE-'].update(data=data) 
                
                window['-CORRECT-'].update(disabled=False, button_color=('#FFFFFF', '#004F00'))
        
            except:
                pass
            
            
            

        # if 'Correct' button is not disabled & clicked, display appropriate window
        if event == ('-CORRECT-'):
            
            correctMWindow = correctMethodWindow()
            correctWindow = sg.Window('Correction Method', correctMWindow, size=(355,195), margins=(20, 20))
            while True:
                correctEvent, correctVal = correctWindow.read()
                if correctEvent == sg.WIN_CLOSED or correctEvent == ('-RESTART-'):
                    # Close the help popup
                    correctWindow.close()
                    
                    break
                elif correctEvent == 'Manual':
                    correctWindow.close()

                    ix = 0
                    iy = 0
                    
                    # Covers the case where correctWinow messes up if automatic was used FIRST, then manual
                    if (automaticCorrectedOnce == True and correctionsCompleted == 1):
                        reformatScreen(window,True)
                        
                        # I know its _forget() here, but the buttons look good
                        window['-CORRECT-'].Widget.master.pack_forget()
                        window['-EXPORT-'].Widget.master.pack_forget() 
                        
                        # window['-CORRECT-'].update(visible=False)
                        # window['-EXPORT-'].update(visible=False) 
                        
                        
                    
                    # If manual was chosen FIRST instead, reformat the screen based on other boolean situations
                    elif (automaticCorrectedOnce == False or correctionsCompleted != 1):
                              
                        if (prevButtonClickedOnce == True or doneButtonClickedOnce == True):
                            reformatScreen(window, True)
                        elif (prevButtonClickedOnce == False and doneButtonClickedOnce == False):
                            reformatScreen(window, False)
                                                        
                    
                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    DPI = fig.get_dpi()

                    fig.set_size_inches(505 * 2 / float(DPI), 500 / float(DPI))
                    img = mpimg.imread(fileName)
                    imgplot = plt.imshow(img)
                    plt.grid()
                    
            

                    # Define a list to store the coordinates of the line
                    lineCoords = []

                    # Define a function to handle mouse clicks
                    def onclick(event):
                        # Append the coordinates of the click to the list
                        if event.xdata != None and event.ydata != None:
                            lineCoords.append((event.xdata, event.ydata))
                            ax.scatter(event.xdata, event.ydata, color='r')
                            fig.canvas.draw()

                    def onkey(event):
                        # If the key pressed is 'z' and there are points to remove, remove the last point
                        if event.key == 'z' and len(lineCoords) > 0:
                            lineCoords.pop()
                            
                            # Clear the plot and redraw the points
                            ax.clear()
                            ax.imshow(img)
                            plt.grid()
                            for point in lineCoords:
                                # Unpack the tuple into x and y coordinates
                                x, y = point
                                # Plot the point using ax.scatter()
                                ax.scatter(x, y, color='r')
                            fig.canvas.draw()

                    # Connect the onclick function to the mouse click event
                    cid = fig.canvas.mpl_connect('button_press_event', onclick)
                    cid2 = fig.canvas.mpl_connect('key_press_event', onkey)
                                  
                    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig)
                    
                    
                
                elif correctEvent == 'Automatic':
                    correctWindow.close()                                        


                    predicted_points = auto_correct_process(fileName, values["-FOLDER-"])
                    
                    predicted_points_list = [item for sublist in predicted_points.tolist() for item in sublist]
                    for i in range(len(predicted_points_list)):
                        if predicted_points_list[i] < 0:
                            predicted_points_list[i] = 1.00

                    # Split the array into two separate arrays for x and y coordinates
                    x_coords = predicted_points_list[::2]
                    y_coords = predicted_points_list[1::2]
                    
                    lineCoords = [(abs(x),y) for x,y in zip(x_coords,y_coords)]


                    
                    # DONT ACTUALLY NEED MAX COORDS, CAN DELETE MAX STUFF
                    point_with_highest_y = max(lineCoords, key=lambda point:point[1])
                    ix = point_with_highest_y[0]
                    iy = -point_with_highest_y[1]


                    # Fix the screen to prepare for image processing
                    fixScreen(window, fileName)

                    # Correct the image (long process)
                    finalImg = correctImageMan(fileName, ix, iy, window)
                    
                    correctWindow.close()

                    window['-FOLDER-'].update(visible=True)
                    window['-FILE LIST-'].update(visible=True)
                    window['-CORRECT-'].update(visible=True)
                    window['-BROWSE-'].update(visible=True)
                    
                    # Assuming `finalImg` is a numpy array with the shape (height, width, channels)
                    # Convert the array from BGR to RGB
                    finalImg = cv2.cvtColor(finalImg, cv2.COLOR_BGR2RGB)

                    # Create a PIL Image object from the numpy array
                    pilImg = PIL.Image.fromarray(finalImg)

                    # Resize the image to fit the window
                    data = imageToData(pilImg, window["-IMAGE-"].get_size())
                    window['-IMAGE-'].update(data=data)
                    updateProgressBar(95,101, window)

                    window['-EXPORT-'].update(visible=True, disabled=False, button_color=('#FFFFFF', '#004F00'))
                    window['-ProgressText-'].update(visible=False)
                    window['-ProgressBar-'].update(visible=False)
                    
                    window["-PAD FOR CORRECTION-"].Widget.master.pack_forget()
                    window["-PAD FOR CORRECTION-"].update(visible=False)
                    
                    
                    window['-FOLDROW-'].Widget.master.pack()
                    window['-FILE LIST-'].Widget.master.pack()
                    window['-BROWSE-'].Widget.master.pack()
                    window['-CORRECT-'].Widget.master.pack()
                    window['-EXPORT-'].Widget.master.pack()
                    window['-HELP-'].Widget.master.pack()
                    window['-QUIT-'].Widget.master.pack()

                    displaySuccess()
                    
                    # Reset progress bar to zero
                    updateProgressBar(0,1,window)
                    
                    automaticCorrectedOnce = True
                    correctionsCompleted += 1

                    

                elif correctEvent == 'Cancel':
                    correctWindow.close()
                    break

        # If user clicks the previous button, return to main window
        if event == '-PREVIOUS BTN-':
            defaultWindow(window)
            prevButtonClickedOnce = True


        if event == ('-DONE-') and lineCoords != []:

                
            if (prevButtonClickedOnce == True or doneButtonClickedOnce == True):
                reformatScreen(window, True)
            elif (prevButtonClickedOnce == False and doneButtonClickedOnce == False):
                reformatScreen(window, False)
            

            # Clear the plot and redraw the image
            ax.clear()
            ax.imshow(img)
            plt.axis('off')
            fig.set_facecolor('none') # set the background to transparent
            fig.canvas.draw()

            # Disconnect from the figure
            fig.canvas.mpl_disconnect(cid)
            fig.canvas.mpl_disconnect(cid2)
            
    
            
            point_with_highest_y = max(lineCoords, key=lambda point:point[1])
            ix = point_with_highest_y[0]
            iy = -point_with_highest_y[1]
            
            # Forget these since there's no point in having them while image is processing.
            window['-PREVIOUS BTN-'].update(visible=False)
            window['-DONE-'].update(visible=False)
            window['-DONE-'].Widget.master.pack_forget() 
            window['-RESTART-'].update(visible=False)
            window['-RESTART-'].Widget.master.pack_forget() 
            
            # Fix the screen to prepare for image processing
            fixScreen(window, fileName)

            # Correct the image (long process)
            finalImg = correctImageMan(fileName, ix, iy, window)
            
            correctWindow.close()

            window['-TITLE-'].update("SkyFix360")
            
            window['-MANUAL DESCRIPTION-'].update(visible=False)
            window['-MANUAL DESCRIPTION-'].Widget.master.pack_forget()  

            window['fig_cv'].update(visible=True)
            window['-FOLDER-'].update(visible=True)
            window['-FILE LIST-'].update(visible=True)
            window['-CORRECT-'].update(visible=True)
            window['-BROWSE-'].update(visible=True)
            
            # Assuming `finalImg` is a numpy array with the shape (height, width, channels)
            # Convert the array from BGR to RGB
            finalImg = cv2.cvtColor(finalImg, cv2.COLOR_BGR2RGB)

            # Create a PIL Image object from the numpy array
            pilImg = PIL.Image.fromarray(finalImg)

            # Resize the image to fit the window
            data = imageToData(pilImg, window["-IMAGE-"].get_size())
            window['-IMAGE-'].update(data=data)
            updateProgressBar(95,101, window)

            window['-EXPORT-'].update(visible=True, disabled=False, button_color=('#FFFFFF', '#004F00'))
            window['-ProgressText-'].update(visible=False)
            window['-ProgressBar-'].update(visible=False)
            
            window["-PAD FOR CORRECTION-"].Widget.master.pack_forget()
            window["-PAD FOR CORRECTION-"].update(visible=False)
            
            
            window['-FOLDROW-'].Widget.master.pack()
            window['-FOLDER-'].Widget.master.pack(side='left', padx=(0,0), pady=(0,0))
            window['-BROWSE-'].Widget.master.pack(side='left', padx=(0,0), pady=(0,0))
            window['-FILE LIST-'].Widget.master.pack()
            window['-CORRECT-'].Widget.master.pack()
            window['-EXPORT-'].Widget.master.pack()
            window['-HELP-'].Widget.master.pack()
            window['-QUIT-'].Widget.master.pack()

            displaySuccess()
            
            # Reset progress bar to zero
            updateProgressBar(0,1,window)

            doneButtonClickedOnce = True
            correctionsCompleted += 1

            if(automaticCorrectedOnce):
                defaultWindow(window)
            
            

        # If user clicks export, export the fixed final image to the current working directory
        if event == '-EXPORT-':
            # Assuming `finalImg` is a numpy array with the shape (height, width, channels)
            # Convert the array from BGR to RGB
            finalImg = cv2.cvtColor(finalImg, cv2.COLOR_BGR2RGB)

            opfile = os.path.splitext(fileName)[0]+'_f.jpg'
            cv2.imwrite(opfile, finalImg, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            window['-EXPORT-'].update(disabled=True, button_color=('grey', sg.theme_button_color_background()))
            print('\nWrote output file: ', opfile)


        # if user clicks Cancel button, clear canvas (restart drawing)
        if event == ('-RESTART-'):
            lineCoords = []
            
            # Clear the plot and redraw the image
            ax.clear()
            ax.imshow(img)
            plt.grid()
            fig.canvas.draw()
            
        # if user selects '-QUIT-' button or default exit button, close window
        if event == ('-QUIT-') or event == sg.WIN_CLOSED:
            break
        
        
# ------------------------------------------------------------------------------  

def imageToData(pilImage, resize, blur=False):
    """ 
        Args:    pilImage --> PIL.Image: The PIL Image to be converted to bytes.
                 resize   --> tuple: A tuple of two integers representing the desired width and height of the image.
                 blur     --> bool, optional: A boolean indicating whether to apply a Gaussian blur filter to the image. Defaults to False.
        Returns: bytes: A byte stream representing the converted image.
        Summary: Converts a PIL Image to bytes and returns said bytes for display in a PySimpleGUI window.
    """

    
    # store current image and its width and height
    img = pilImage.copy()

    if (blur == True):
         # Apply Gaussian blur filter to the image
         img = img.filter(ImageFilter.GaussianBlur(radius=50))

    currentW, currentH = img.size
    
    # if resize image, make new height and width to scale image
    if resize:
        newW, newH = resize
        scale = min(newH/currentH, newW/currentW)
        img = img.resize((int(currentW*scale), int(currentH*scale)), PIL.Image.ANTIALIAS)  
    
    # convert image to bytes and save it
    ImgBytes = io.BytesIO()
    img.save(ImgBytes, format="PNG")
    del img
    return ImgBytes.getvalue()

# ------------------------------------------------------------------------------  

def closeAllWindows():
    """ 
        Args:    None
        Returns: None
        Summary: Close all opened windows
    """
    sys.exit()

# ------------------------------------------------------------------------------  

def draw_figure_w_toolbar(canvas, fig):
    """ 
        Args:    canvas:         --> tkinter canvas onto which the figure will be drawn
                 fig:            --> matplotlib figure to be drawn
                 canvas_toolbar: --> tkinter canvas onto which the toolbar will be packed
        Returns: None
        Summary: 
    """
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)

# ------------------------------------------------------------------------------  

def correctImageMan(fileName, ix, iy, window):
    """ 
        Args:    fileName --> Str: Name of the file to be corrected
                 ix       --> Int: The x-position (column) of the point on the horizon that needs to be aligned with the center column of the corrected image
                 iy       --> Int: The y-position (row) of the point on the horizon that needs to be aligned with the horizontal center of the corrected image
                 window   --> PySimplueGui Object: The main window running the program
        Returns: finalImg --> Image: The corrected image as a NumPy array
        Summary: Corrects an equirectangular image by rotating it such that the horizon becomes straight. This is accomplished by creating an EquirectRotate
                 object. Return the fixed image.

    """

    print('\n Now rotating the image to straighten the horizon.')
    src_image = cv2.imread(fileName)

    h, w, c = src_image.shape
    print("\n Input file's height, width, colors =", h, w, c)

    # Do a 'yaw' rotation such that ix position earth-sky horizon is at the
    # middle column of the image. Fortunately for an equirectangular image, a yaw
    # is simply sliding the image horizontally, and is done very fast by np.roll
    shiftx=int(w/2 - ix)
    src_image = np.roll(src_image, shiftx, axis=1) 
    updateProgressBar(0,11, window)

    # If iy>0 then the user selected the lowest point of the horizon. After the
    # above 'yaw', the true horizon at the middle of the image is still
    # (iy - h/2) pixels below the camera's equator. This is (iy - h/2)*(180)/h degrees
    # degrees below the camera's equator. So rotate the pitch of the yaw-ed
    # rectilinear image by this amount to get a nearly straight horizon.
    myY, myP, myR = 0, (iy - h/2)*180/h , 0

    # If iy<0 then the user actually recorded the highest point. That is, the
    # true horizon is (h/2 - |iy|) pixels above the camera's equator. So rotate
    # the pitch of the yaw-ed rectilinear image by the amount -(h/2 - |iy|)*180/h
    # to get a nearly straight horizon.
    if iy < 0 :
        myP = -(h/2 - np.abs(iy))*180/h

    print('\n Doing the final rotation (pitch =',str(f'{myP:.2f}'), 'deg). This can take a while ...')
    # rotate (yaw, pitch, roll)

    equirectRot = EquirectRotate(h, w, (myY, myP, myR), window)

    rotated_image = equirectRot.rotate(src_image, window)

    finalImg = cv2.rotate(rotated_image, cv2.ROTATE_180)
    updateProgressBar(85,96, window)
    print('Done.')

    return finalImg

# ------------------------------------------------------------------------------  

def fixScreen(window, fileName):
    """ 
        Args:    window    --> PySimpleGui Object: The main window running the application
                 fileName: --> Str: The file name of the image to be opened
        Returns: None
        Summary: This function sets up the PySimpleGUI window to display the original image 
                 and the progress bar and progress text. It hides the controls and toolbar 
                 until the image has been corrected.
    """
     
    window['fig_cv'].update(visible=False)
    window['fig_cv'].Widget.master.pack_forget() 
    window['-FOLDROW-'].Widget.master.pack_forget() 
    window['-FILE LIST-'].Widget.master.pack_forget() 
    window['-CORRECT-'].Widget.master.pack_forget() 
    window['-EXPORT-'].Widget.master.pack_forget() 
    window['-ProgressText-'].Widget.master.pack_forget() 
    window['-ProgressBar-'].Widget.master.pack_forget() 
    window['-HELP-'].Widget.master.pack_forget() 
    window['-QUIT-'].Widget.master.pack_forget() 
    window['-PAD FOR CORRECTION-'].Widget.master.pack_forget()

    window['-IMAGE-'].Widget.master.pack()
    window['-IMAGE-'].update(visible=True)

    # Open the ORIGINAL image
    pilImage = PIL.Image.open(fileName)

    # Get image data, and then use it to update window["-IMAGE-"]
    # Blur the image because it wil be corrected next after returning from this function
    data = imageToData(pilImage, window["-IMAGE-"].get_size(), blur=True)
    window['-IMAGE-'].update(data=data) 

    window['-ProgressText-'].Widget.master.pack()
    window['-ProgressBar-'].Widget.master.pack()
    
    window["-PAD FOR CORRECTION-"].Widget.master.pack()
    window["-PAD FOR CORRECTION-"].update(visible=True)

    window['-PAD FOR CORRECTION-'].Widget.master.pack()
    window['-PAD FOR CORRECTION-'].update(visible=True)

    window['-ProgressText-'].update(visible=True)
    window['-ProgressBar-'].update(visible=True)
    

# ------------------------------------------------------------------------------  

def displaySuccess():
    """ 
        Args:    None
        Returns: None
        Summary: Diplsay the successWindow for when an image is successfully corrected until the user closes it.
    """
     
    successMWindow = successWindow()
    successWin = sg.Window('Success', successMWindow, size=(310,165), margins=(10, 10))
    while True:
        successevent, successVal = successWin.read()
        if successevent == sg.WIN_CLOSED or successevent == ('Close'):
            # Close the help popup
            successWin.close()
            break
        

# ------------------------------------------------------------------------------  

def updateProgressBar(start,end, window):
    """ 
        Args:    start   --> integer signifying where to start the updating
                 end     --> integer signifying where to start the updating
                 window  --> the data of the window that is displayed to user
        Returns: N/A
        Summary: This function updates the progress bar with the window based
                 on the passed in values of start/end.
    """
    
    for i in range(start,end):
        window['-ProgressBar-'].update(i)
        
# ------------------------------------------------------------------------------  

def reformatScreen(window, btnClick):
    # Normal
    if (btnClick == False):

        window['-FILETEXT-'].update(visible=False)
        window['-FILENAME-'].update(visible=False)
        window['-SPACE1-'].update(visible=False)
        window['-SPACE2-'].update(visible=False)

        window['-PREVIOUS BTN-'].update(visible=True)
        window['-SPACE1-'].update(visible=True)
        window['-FILETEXT-'].update(visible=True)
        window['-FILENAME-'].update(visible=True)
        window['-SPACE2-'].update(visible=True)

        window['-IMAGE-'].update(visible=False)
        window['-IMAGE-'].Widget.master.pack_forget()
            
        window['fig_cv'].update(visible=True)
        window['-FOLDER-'].update(visible=False)
        window['-FILE LIST-'].Widget.master.pack_forget() 
        window['-CORRECT-'].update(visible=False)
        window['-BROWSE-'].update(visible=False)
        window['-EXPORT-'].update(visible=False)
        window['-TITLE-'].update("Manual Correction Instructions")
        window['-MANUAL DESCRIPTION-'].update(visible=True)
        window['-RESTART-'].update(visible=True)
        window['-DONE-'].update(visible=True)
    
    # Fixes "correctWindow" display issues
    elif (btnClick == True):

        window['-FILETEXT-'].update(visible=False)
        window['-FILENAME-'].update(visible=False)
        window['-SPACE1-'].update(visible=False)
        window['-SPACE2-'].update(visible=False)
        
        window['-IMAGE-'].Widget.master.pack_forget() 
        window['-FOLDROW-'].Widget.master.pack_forget() 
        window['-FILE LIST-'].Widget.master.pack_forget() 
        window['-CORRECT-'].Widget.master.pack_forget()
        window['-EXPORT-'].Widget.master.pack_forget() 
        window['-HELP-'].Widget.master.pack_forget() 
        window['-QUIT-'].Widget.master.pack_forget() 

        window['-PREVIOUS BTN-'].update(visible=True)
        window['-SPACE1-'].update(visible=True)
        window['-FILETEXT-'].update(visible=True)
        window['-FILENAME-'].update(visible=True)
        window['-SPACE2-'].update(visible=True)
        
        window['fig_cv'].Widget.master.pack() 
        window['fig_cv'].update(visible=True)
        window['-FOLDER-'].update(visible=False)
        window['-BROWSE-'].update(visible=False)
        
        window['-FOLDER-'].Widget.master.pack_forget() 
        window['-BROWSE-'].Widget.master.pack_forget() 
    
        window['-FOLDROW-'].Widget.master.pack()
        window['-TITLE-'].update('Manual Correction Instructions')

        
        manualDescription = "Click the lowest and highest points of the horizon. To remove the most recent point, press 'z'. Once you are done, click the 'Done' button. If you wish to restart, click the 'Restart' button and try again."
        manualDescription = textwrap.fill(manualDescription, 52)
        
        window['-MANUAL DESCRIPTION-'].Widget.master.pack(side='left', padx=(0,0), pady=(0,0)) 
        window['-MANUAL DESCRIPTION-'].update(visible=True)
        window['-MANUAL DESCRIPTION-'].update(manualDescription)


        window['-CORRECT-'].Widget.master.pack()
        window['-EXPORT-'].Widget.master.pack() 
        window['-CORRECT-'].update(visible=False)
        window['-EXPORT-'].update(visible=False)
        window['-DONE-'].Widget.master.pack() 
        window['-DONE-'].update(visible=True)
        window['-RESTART-'].Widget.master.pack() 
        window['-RESTART-'].update(visible=True)
        window['-HELP-'].Widget.master.pack() 
        window['-HELP-'].update(visible=True)
        window['-QUIT-'].Widget.master.pack() 
        window['-QUIT-'].update(visible=True)


def defaultWindow(window):
    window['-PREVIOUS BTN-'].update(visible=False)
    window['-TITLE-'].update(visible=False)
    window['-MANUAL DESCRIPTION-'].update(visible=False)
    window['fig_cv'].update(visible=False)
    window['-DONE-'].update(visible=False)
    window['-RESTART-'].update(visible=False)

    window['fig_cv'].Widget.master.pack_forget() 
    window['-MANUAL DESCRIPTION-'].Widget.master.pack_forget() 
    window['-FOLDROW-'].Widget.master.pack_forget() 
    window['-FILE LIST-'].Widget.master.pack_forget() 
    window['-CORRECT-'].Widget.master.pack_forget()
    window['-EXPORT-'].Widget.master.pack_forget() 
    window['-DONE-'].Widget.master.pack_forget() 
    window['-RESTART-'].Widget.master.pack_forget()
    window['-HELP-'].Widget.master.pack_forget() 
    window['-QUIT-'].Widget.master.pack_forget() 

    window['-IMAGE-'].Widget.master.pack()
    window['-IMAGE-'].update(visible=True)
    window['-FOLDROW-'].Widget.master.pack()
    window['-FOLDROW-'].update(visible=True)
    window['-FOLDROW-'].Widget.update()
    window['-TITLE-'].update(visible=True)
    window['-TITLE-'].update('SkyFix360')
    window['-FOLDER-'].Widget.master.pack()
    window['-FOLDER-'].update(visible=True)
    window['-BROWSE-'].Widget.master.pack()
    window['-BROWSE-'].update(visible=True)
    window['-FILE LIST-'].Widget.master.pack()
    window['-FILE LIST-'].update(visible=True)
    window['-FILE LIST-'].Widget.update()
    window['-CORRECT-'].Widget.master.pack()
    window['-CORRECT-'].update(visible=True)
    window['-EXPORT-'].Widget.master.pack()
    window['-EXPORT-'].update(visible=True)
    window['-HELP-'].Widget.master.pack()
    window['-QUIT-'].Widget.master.pack()
    
# ------------------------------------------------------------------------------


def main():
    window = createWindow() # Create MAIN window of the program
    runEvents(window)       # Run Tasks
    window.close()          # Close the window

# ------------------------------------------------------------------------------  

if __name__ == '__main__':
    main()