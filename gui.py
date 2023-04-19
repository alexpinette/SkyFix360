'''
    NCAA
    GUI.py
    Senior Seminar 2023
'''

import os, io, sys
import numpy as np
import PySimpleGUI as sg, PIL, cv2, textwrap
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from PIL import Image, ImageFilter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from equirectRotate import EquirectRotate
from moviepy.editor import *

from auto_fix import auto_correct_process

#-------------------------------------------------------------------------------
global prevButtonClickedOnce
global doneButtonClickedOnce


def createWindow():
    """ 
        Args:     None
        Returns:  window --> list: The main layout of the program. List of many PySimpleGUI elements 
        Summary:  Creates the main GUI window for the SkyFix360 application with all necessary elements and returns it.
    """
    sg.theme ("DarkGrey1")

    manualDescription = "Click the lowest and highest points of the horizon. To remove the most recent point, click the `Undo` button. Once you are done, click 'Done'."
    newManualDescription = textwrap.fill(manualDescription, 52)


    firstRow = [[ sg.Button('<', key='-PREVIOUS BTN-', visible=False, size=(5, 1)),
                  sg.Text('', key='-SPACE1-', visible=True, expand_x=True),
                  sg.Text('File', font="Arial 10 bold", size=(4,1), key='-FILETEXT-', justification='center'), 
                  sg.Input('', key='-FILENAME-', disabled=True, justification='center'),
                  sg.Text('    ', key='-SPACE2-', visible=True, expand_x=True),
                ],

                [sg.Image(key='-IMAGE-', background_color = 'black', size=(1200, 600))],
                [sg.Text('Progress: ', font='Arial 10 bold', key='-ProgressText-', visible=False),
                 sg.ProgressBar(100, orientation='h', size=(15, 15), key='-ProgressBar-',  bar_color='#FFFFFF', visible=False)],
                [sg.Canvas(key='controls_cv')],
                [sg.Canvas(key='fig_cv', size=(800, 400), visible=False)]
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
         [sg.Button('Correct', key='-CORRECT-', disabled=True, button_color=('grey', sg.theme_button_color_background()), size=(10, 1)),
           sg.Button('Modify', key='-MODIFY-', visible=False, size=(10, 1)) ],
         [sg.Button('Export', key='-EXPORT-', disabled=True, button_color=('grey', sg.theme_button_color_background()), size=(10, 1))],
         [sg.Button('Undo', key='-UNDO-', visible=False, size=(10, 1))],
         [sg.Button('Done', key='-DONE-', visible=False, size=(10, 1))],
         ])
        ],
        [sg.Text("", pad=(0,66), key="-PAD FOR CORRECTION-", visible=False)],
        [sg.Button('Help', key='-HELP-', size=(10, 1)), sg.Button("Quit", key="-QUIT-", size=(10, 1))]
    ] 

    layout = [ firstRow, secondRow ]

    # Display the window
    window = sg.Window ("SkyFix360", layout, element_justification='c', resizable = True, finalize = True, size=(1300, 860))
    
    # bind to config so can check when window size changes
    window.bind('<Configure>', key='-CONFIG-')
    
    # bind the closeAllWindows function to the WM_DELETE_WINDOW event of the main window
    window.TKroot.protocol("WM_DELETE_WINDOW", closeAllWindows)

    return window

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


# ------------------------------------------------------------------------------  
def runEvents(window):
    """ 
        Args:      window --> PySimpleGUI Window: the main window of the application
        Returns:   None
        Summary:   This function handles the event loop of the application.
                   It listens for events triggered by the user and responds accordingly.
    """

    fileNames = []                 # set fileNames to an empty list that will represent legal input
    prevButtonClickedOnce = False  # Will help with fixing correction window displaying incorrectly
    doneButtonClickedOnce = False  # Will help with fixing correction window displaying incorrectly
    automaticCorrectedOnce = False # Will help with fixing correction window displaying incorrectly
    correctionsCompleted = 0       # Will help with fixing correction window displaying incorrectly
    fileExt = ""                   # Track file extension user selected to correct
    modifyClicked = False          # To keep track of temporary saved corrected image  
        
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
                # file name to process correction method on
                fileName = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
                
                # disable `Export` button since new image was selected
                window['-EXPORT-'].update(disabled=True, button_color=('grey', sg.theme_button_color_background()))
                window['-TITLE-'].update('SkyFix360')
                window['-MODIFY-'].update(visible=False)

                # when the user changes the filename, reset modifyClicked to false
                modifyClicked = False

                # display filename in appropriate spot in right column
                window['-FILENAME-'].update(fileName)
                
                # get the file extension
                fileExt = os.path.splitext(fileName)[1].lower()

                # differentiate between .jpg and .mp4 files
                if fileExt == '.jpg' or fileExt == '.jpeg':
                    fileExt = '.jpg'
                    print('Selected file is a .jpg or .jpeg')
            
                    # Open the image
                    pilImage = PIL.Image.open(fileName)
                    
                elif fileExt == '.mp4':
                    print('Selected file is a .mp4')
                    
                    # read the .mp4 video file
                    cap = cv2.VideoCapture(fileName)
                    
                    # read the first frame of the video
                    ret, frame = cap.read()

                    # convert the OpenCV image to a PIL Image
                    pilImage = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    pilImage.save("vidImage.jpg")
                    
                    # NOTE TO CLOSE/RELEASE THE VIDEOCAPTURE:
                    # cap.release()
                    
                # Get image data, and then use it to update window["-IMAGE-"]
                data = imageToData(pilImage, window["-IMAGE-"].get_size())
                window['-IMAGE-'].update(data=data)
                window['-CORRECT-'].update(disabled=False, button_color=('#FFFFFF', '#004F00'))
                
            except:
                pass
            

        # if 'Correct' button is not disabled & clicked, display appropriate window
        if event == ('-CORRECT-') or event == ('-MODIFY-'):

            # User chose a video file.
            if (fileExt == '.mp4'):
                handleAutomaticVideoCorrection(fileName, window, "vidImage.jpg")
                automaticCorrectedOnce = True
                modifyClicked = False

                correctionsCompleted += 1
                # Reset progress bar to zero
                updateProgressBar(0,1,window)

            # modify only works & is displayed when jpg/jpeg format selected
            elif (fileExt == '.jpg' or fileExt == '.jpeg') or  event == ('-MODIFY-'):
                 # if user clicked `modify` button, temporarily save image to recorrect it
                if event == ('-MODIFY-'):
                    modifyClicked = True
                    finalImg = cv2.cvtColor(finalImg, cv2.COLOR_BGR2RGB)
                    
                    # must flip image when modifying a corrected image
                    finalImg = cv2.flip(finalImg, 0)
                    
                    opfile = os.path.splitext(fileName)[0]+'_f.jpg'
                    fileName = opfile
                    cv2.imwrite(opfile, finalImg, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

                # pop up correction window that allows the user to select manual or automatic correction method
                correctMWindow = correctMethodWindow()
                correctWindow = sg.Window('Correction Method', correctMWindow, size=(355,195), margins=(20, 20))
                while True:
                    correctEvent, correctVal = correctWindow.read()
                    if correctEvent == sg.WIN_CLOSED:
                        # Close the correction window popup
                        correctWindow.close()
                        break
                    
                    elif correctEvent == 'Manual':
                        correctWindow.close()

                        ix = 0
                        iy = 0
                        
                        # Covers the case where correctWinow messes up if automatic was used FIRST, then manual
                        if (automaticCorrectedOnce == True and correctionsCompleted == 1):
                            reformatScreen(window, True)
                            
                            # I know its _forget() here, but the buttons look good
                            window['-CORRECT-'].Widget.master.pack_forget()
                            if modifyClicked: window['-MODIFY-'].Widget.master.pack_forget()
                            window['-EXPORT-'].Widget.master.pack_forget() 
                        
                        # If manual was chosen FIRST instead, reformat the screen based on other boolean situations
                        elif (automaticCorrectedOnce == False or correctionsCompleted != 1):

                            if (prevButtonClickedOnce == True or doneButtonClickedOnce == True):
                                reformatScreen(window, True)
                            elif (prevButtonClickedOnce == False and doneButtonClickedOnce == False):
                                reformatScreen(window, False)

                        # Create a new Figure object with a size of 8 inches by 4 inches and a dpi of 100, 
                        # and enable automatic adjustment of subplots to fit in the figure area               
                        fig = plt.figure(figsize=(8, 4), dpi=100, constrained_layout = True)

                        # Create a new Axes object in the Figure object, with a grid of 1 row and 1 column of subplots, 
                        # and select the first subplot
                        ax = fig.add_subplot(111)

                        # WINDOWS SYSTEM
                        if os.name == 'nt':
                            fig.set_size_inches(1150/100, 575/100, forward=True)
                        
                        # MAC OR LINUX
                        else:
                            fig.set_size_inches(600/100, 300/100, forward=True)

                        # Read the image file into a NumPy array
                        img = mpimg.imread(fileName)

                        # Create a new plot and display the image on it
                        imgplot = plt.imshow(img, aspect="auto")

                        # Add a grid to the plot
                        plt.grid()

                        # Define a list to store the coordinates of the line
                        lineCoords = []

                        # Define a function to handle mouse clicks
                        def onclick(event):
                            # Append the coordinates of the click to the list and display it on the plot
                            if event.xdata != None and event.ydata != None:
                                lineCoords.append((event.xdata, event.ydata))
                                ax.scatter(event.xdata, event.ydata, color='r')
                                fig.canvas.draw()

                        # Connect the onclick function to the mouse click event
                        cid = fig.canvas.mpl_connect('button_press_event', onclick)
                        
                        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
                        
                    elif correctEvent == 'Automatic':
                        correctWindow.close()                                        

                        predicted_points = auto_correct_process(fileName)
                        
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
                        finalImg = correctImageMan(fileName, ix, iy, window, "img")
                        
                        correctWindow.close()

                        window['-FOLDER-'].update(visible=True)
                        window['-FILE LIST-'].update(visible=True)
                        window['-CORRECT-'].update(visible=True, disabled=True, button_color=('grey', sg.theme_button_color_background()))
                        window['-MODIFY-'].update(visible=True)
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
                        
                        window['-PAD FOR CORRECTION-'].Widget.master.pack_forget()
                        window['-PAD FOR CORRECTION-'].update(visible=False)
                        
                        defaultWindow(window, True, True)

                        # Reset progress bar to zero
                        updateProgressBar(0,1,window)
                        
                        automaticCorrectedOnce = True
                        correctionsCompleted += 1

                        # delete saved image if user modifed a corrected image
                        if modifyClicked: os.remove(opfile)

                    elif correctEvent == 'Cancel':
                        correctWindow.close()
                        break


        # If user clicks the previous button, return to main window
        if event == '-PREVIOUS BTN-':
            # delete saved image if user modifed a corrected image
            if modifyClicked:
                os.remove(opfile)

                # convert BGR color space to the RGB color space
                finalImg = cv2.cvtColor(finalImg, cv2.COLOR_BGR2RGB)
                
            defaultWindow(window, False, modifyClicked)
            prevButtonClickedOnce = True

        # continue if user is done plotting the 2 points on the canvas and clicks done
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
            
            point_with_highest_y = max(lineCoords, key=lambda point:point[1])
            ix = point_with_highest_y[0]
            iy = -point_with_highest_y[1]
            
            # Forget these since there's no point in having them while image is processing.
            window['-PREVIOUS BTN-'].update(visible=False)
            window['-UNDO-'].update(visible=False)
            window['-UNDO-'].Widget.master.pack_forget() 
            window['-DONE-'].update(visible=False)
            window['-DONE-'].Widget.master.pack_forget() 
            
            # Fix the screen to prepare for image processing
            fixScreen(window, fileName)

            # Correct the image (long process)
            finalImg = correctImageMan(fileName, ix, iy, window, "img")
            
            correctWindow.close()

            window['-TITLE-'].update('SkyFix360 - COMPLETED')
            window['-MANUAL DESCRIPTION-'].update(visible=False)
            window['-MANUAL DESCRIPTION-'].Widget.master.pack_forget()  
            window['controls_cv'].update(visible=True)
            window['fig_cv'].update(visible=True)
            window['-FOLDER-'].update(visible=True)
            window['-FILE LIST-'].update(visible=True)
            window['-CORRECT-'].update(visible=True, disabled=True, button_color=('grey', sg.theme_button_color_background()))
            window['-MODIFY-'].update(visible=True)
            window['-BROWSE-'].update(visible=True)
            
            # Assuming `finalImg` is a numpy array with the shape (height, width, channels)
            # Convert the array from BGR to RGB
            finalImg = cv2.cvtColor(finalImg, cv2.COLOR_BGR2RGB)

            # Create a PIL Image object from the numpy array
            pilImg = PIL.Image.fromarray(finalImg)

            # Resize the image to fit the window
            data = imageToData(pilImg, window['-IMAGE-'].get_size())
            window['-IMAGE-'].update(data=data)
            updateProgressBar(95,101, window)

            window['-EXPORT-'].update(visible=True, disabled=False, button_color=('#FFFFFF', '#004F00'))
            window['-ProgressText-'].update(visible=False)
            window['-ProgressBar-'].update(visible=False)
            
            window['-PAD FOR CORRECTION-'].Widget.master.pack_forget()
            window['-PAD FOR CORRECTION-'].update(visible=False)
            
            window['-FOLDROW-'].Widget.master.pack()
            window['-FOLDER-'].Widget.master.pack(side='left', padx=(0,0), pady=(0,0))
            window['-BROWSE-'].Widget.master.pack(side='left', padx=(0,0), pady=(0,0))
            window['-FILE LIST-'].Widget.master.pack()
            window['-CORRECT-'].Widget.master.pack()
            window['-MODIFY-'].Widget.master.pack()
            window['-EXPORT-'].Widget.master.pack()
            window['-HELP-'].Widget.master.pack()
            window['-QUIT-'].Widget.master.pack()
            
            # Reset progress bar to zero
            updateProgressBar(0,1,window)

            doneButtonClickedOnce = True
            correctionsCompleted += 1

            if(automaticCorrectedOnce):
                defaultWindow(window, True, True)
            
            # delete saved image if user modifed a corrected image
            if modifyClicked: os.remove(opfile)
            
            
        # If user clicks export, export the fixed final image to the current working directory
        if event == '-EXPORT-':
            
            savePath = getExportPath()
            
            # We only want to try saving and greying out the button if the user did save the image!
            if (savePath != "void"):
                
                # Assuming `finalImg` is a numpy array with the shape (height, width, channels)
                # Convert the array from BGR to RGB
                finalImg = cv2.cvtColor(finalImg, cv2.COLOR_BGR2RGB)
                
                # Save the file to the path specified
                cv2.imwrite(savePath, finalImg, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                window['-EXPORT-'].update(disabled=True, button_color=('grey', sg.theme_button_color_background()))
                
                
        
        # if user clicks `Undo` button, undo last click event on canvas
        if event == ('-UNDO-'):
            
            # Try/Except in case lineCoords is empty
            try:
                lineCoords.pop()
                
                # Clear the plot and redraw the points
                ax.clear()
                ax.imshow(img, aspect='auto')
                plt.grid()
                for point in lineCoords:
                    # Unpack the tuple into x and y coordinates
                    x, y = point
                    # Plot the point using ax.scatter()
                    ax.scatter(x, y, color='r')
                fig.canvas.draw()
            except:
                pass
        
        # if user selects '-QUIT-' button or default exit button, close window
        if event == ('-QUIT-') or event == sg.WIN_CLOSED:
            break
        
        
        
 # ------------------------------------------------------------------------------  

def getExportPath():
    """ 
        Args:       None
        Returns:    save_path: A string representing the full path and name of the file where the image will be saved.
        Summary:    Creates a "Save As" dialog to get the path and name for a corrected image file. It prompts the
                    user to enter a filename and select a directory. The function then checks if the filename is
                    valid, and if a directory was selected or not. It then returns the full path and name of the file
                    where the image will be saved.
    """
    

    # Create a custom "Save As" dialog with a custom "Save" button text
    save_layout = [
             [sg.Text('Give your corrected image file a name in the FIRST textbox.\nIf you want to export to your local directory, leave the SECOND row blank!')],
             [sg.In (size=(40,1), key="-FILENAME-", default_text="Enter Filename Here", enable_events=True)],
             [sg.In (size=(40,1), key="-DIRECTORY-",  default_text="Select Directory (Use Browse -->)", disabled=True),
                 sg.FolderBrowse(key='-BROWSE-', size=(10, 1))],
             [sg.Button('Save')],
            ]
    save_window = sg.Window('Save Your Corrected Image/Movie', save_layout)
    
    # Will be used when saving corrected image below
    sep = os.path.sep
    save_path = "void" # Placeholder

    erasedHint = False
    validSavePath = True


    while True:
        save_event, save_values = save_window.Read()

        if save_event == sg.WIN_CLOSED:
            break

        # FIXME: DOESNT ERASE TEXTBOX IMMEDIATELY (does not register first key stroke)
        if save_event == "-FILENAME-" and erasedHint == False:
            # Remove hint text when user starts typing
            save_window[save_event].update("")
            erasedHint = True    

        # Handle the "Save" button click event
        if save_event == 'Save':
            filename = save_values['-FILENAME-']
            directory = save_values['-DIRECTORY-']

            # Checks if user gave a valid file name (at least entered something)
            if filename == "Enter Filename Here" or filename == "":
                validSavePath = False

            # Must change back to true in case user entered falsely beforehand
            else:
                validSavePath = True
            
             # Check directory
            if directory:

                # If user wants local directory (did not choose separate directory)
                if directory == "Select Directory (Use Browse -->)":
                    save_path = os.getcwd() + sep + filename + '.jpg'

                # If user chose a directory
                else:
                    save_path = directory + sep + filename + '.jpg'


            # Only break out of loop and return save_path if user gave a valid file name
            if (validSavePath == True):
                print("The saved file path: ", save_path)
                break

    save_window.Close()
    
    return save_path
        
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
    img.save(ImgBytes, format='PNG')
    del img
    return ImgBytes.getvalue()

# ------------------------------------------------------------------------------  

def closeAllWindows():
    """ 
        Args:    None
        Returns: None
        Summary:  exits the program, which automatically closes all windows.
    """
    sys.exit()

# ------------------------------------------------------------------------------  

def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    """ 
        Args:    canvas:         --> tkinter canvas onto which the figure will be drawn
                 fig:            --> matplotlib figure to be drawn
                 canvas_toolbar: --> tkinter canvas onto which the toolbar will be packed
        Returns: None
        Summary: 
    """
    
    # Clear any existing children in the canvas
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    
    # Clear any existing children in the toolbar canvas
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    
    # Draw the figure on the canvas using FigureCanvasTkAgg
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()

    # Create & pack the toolbar (only displays the coordinates)
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)                  
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)

# ------------------------------------------------------------------------------  

def correctImageMan(fileName, ix, iy, window, vidImg):
    """ 
        Args:    fileName --> Str: Name of the file to be corrected
                 ix       --> Int: The x-position (column) of the point on the horizon that needs to be aligned with the center column of the corrected image
                 iy       --> Int: The y-position (row) of the point on the horizon that needs to be aligned with the horizontal center of the corrected image
                 window   --> PySimplueGui Object: The main window running the program
                 vidImg   --> Str: Flag indicating whether the function is being called for an image or video ('img' or 'vid')
        Returns: finalImg --> Image: The corrected image as a NumPy array
        Summary: Corrects an equirectangular image by rotating it such that the horizon becomes straight. This is accomplished by creating an EquirectRotate
                 object. Return the fixed image.
    """

    # Read image from file and get shape
    src_image = cv2.imread(fileName)
    h, w, c = src_image.shape

    # Do a 'yaw' rotation such that ix position earth-sky horizon is at the
    # middle column of the image. Fortunately for an equirectangular image, a yaw
    # is simply sliding the image horizontally, and is done very fast by np.roll
    shiftx=int(w/2 - ix)
    src_image = np.roll(src_image, shiftx, axis=1) 
    if vidImg == "img":
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

    # Create an EquirectRotate object and apply pitch and yaw rotations
    equirectRot = EquirectRotate(h, w, (myY, myP, myR), window, vidImg)
    rotated_image = equirectRot.rotate(src_image, window)
    
    # Rotate the image 180 degrees to get the final corrected image
    finalImg = cv2.rotate(rotated_image, cv2.ROTATE_180)

    # Update progress bar if working with an image
    if vidImg == "img":
        updateProgressBar(85,96, window)

    print('Done.')

    return finalImg

# ------------------------------------------------------------------------------ 

def handleAutomaticVideoCorrection(fileName, window, vidImage):
    """ 
        Args:    fileName --> Str: Name of the file to be corrected
                 window   --> PySimplueGui Object: The main window running the program
                 vidImg   --> Str: "img" if processing an image, "vid" if processing a video
        Returns: None
        Summary: Corrects the distortion in a video or image file using the fixVideo function and saves the corrected file.
    """

    # Load the video file
    clip = VideoFileClip(fileName)

    # Extract audio from the video file
    clip.audio.write_audiofile("outputA.mp3")

    # Extract audio
    audioClip = clip.audio

    # # Extract metadata
    duration = clip.duration
    fps = clip.fps
    # size = clip.size

    # # Create a dictionary of metadata
    # metadata = {
    #     "filename": fileName,
    #     "duration": duration,
    #     "fps": fps,
    #     "size": size
    # }

    # Get the frames from the video
    frames = clip.iter_frames()

    # Create a directory for output frames
    output_dir = "frames"
    os.makedirs(output_dir, exist_ok=True)

    # Convert each frame to an image and store it in a list
    images = []
    for frame in frames:
        images.append(frame)

    listOfFrames = []
    # Write each frame to the output directory
    for i, frame in enumerate(images):
        filename = os.path.join(output_dir, f"frame_{i}.jpg")
        listOfFrames.append(filename)
        try:
            clip.save_frame(filename, t=i/fps)
        except Exception as e:
            print(f"Error saving frame {i}: {e}")

    print("IMAGE SAVED")

    # Close the clip
    clip.close()

    # Fix the screen to prepare for video processing
    fixScreen(window, vidImage)

    # Fix each frame in the list of frames
    listOfCorrectedFrames = fixVideo(listOfFrames, window)

    # Create an image sequence clip from the frames
    image_clip = ImageSequenceClip(listOfCorrectedFrames, fps=fps, load_images=True)

    # Set the audio of the image clip
    audio = AudioFileClip("outputA.mp3")
    image_clip = image_clip.set_audio(audio)

    # Write the image sequence clip to a video file
    output_path = "output.mp4"
    image_clip.write_videofile(output_path, codec="libx264", audio=True, audio_codec="aac")

    # Close the image sequence clip
    image_clip.close()
    
    
# ------------------------------------------------------------------------------   

def fixVideo(listOfFrames, window):  
    """ 
        Args:    listOfFrames --> list of numpy arrays representing frames of a video
                 window      --> PySimplueGui Object: The main window running the program
        Returns: None
        Summary: Corrects each frame of the video using the "auto_correct_process" and
                "correctImageMan" functions, saves each corrected frame to a new
                directory, and updates the GUI window to show the corrected video frames.
    """

    print("Num of frames is ", len(listOfFrames))

    # Create a directory to save the corrected frames
    output_dir = "framesC"
    os.makedirs(output_dir, exist_ok=True)    

    # Initialize an empty list to store the filenames of the corrected frames
    listOfCorrectedFrames = []      
    prev = 0 
    valToIncrementBy = 0

    # Too many frames to updateProgressBar by a single digit (expression returns < 1)

    # Get a modulus to update at that value while looping through frames
    if (len(listOfFrames) > 80):
        modToIncrement = (len(listOfFrames)//80)+1

    # Small enough amount of frames to increment every iteration of j
    elif len(listOfFrames) <= 80:
        modToIncrement = 1
        valToIncrementBy = 80//len(listOfFrames)

    # Loop through each frame of the video
    for j in range(len(listOfFrames)):         
        # Use the "auto_correct_process" function to get predicted points for the frame                       
        predicted_points = auto_correct_process(listOfFrames[j])

        # Convert the predicted points to a list and correct any negative values
        predicted_points_list = [item for sublist in predicted_points.tolist() for item in sublist]
        for i in range(len(predicted_points_list)):
            if predicted_points_list[i] < 0:
                predicted_points_list[i] = 1.00
                
                
        # Split the array into two separate arrays for x and y coordinates
        x_coords = predicted_points_list[::2]
        y_coords = predicted_points_list[1::2]
        lineCoords = [(abs(x),y) for x,y in zip(x_coords,y_coords)]
        
        # Get the point with the highest y-coordinate and use its x and y values to correct the image
        point_with_highest_y = max(lineCoords, key=lambda point:point[1])
        ix = point_with_highest_y[0]
        iy = -point_with_highest_y[1]

        # Correct the image (long process)
        finalImg = correctImageMan(listOfFrames[j], ix, iy, window, "vid")
        
        # Assuming `finalImg` is a numpy array with the shape (height, width, channels)
        # Convert the array from BGR to RGB
        finalImg = cv2.cvtColor(finalImg, cv2.COLOR_BGR2RGB)

        # Create a PIL Image object from the numpy array
        pilImg = PIL.Image.fromarray(finalImg)

        # Save the corrected image to the output directory
        filename = os.path.join(output_dir, f"frame_{j}.jpg")
        pilImg.save(filename)

        # Add the filename of the corrected image to the list of corrected frames
        listOfCorrectedFrames.append(filename)
        
       # Increment progressBar while looping at precalculated modulus value (total frames > 80)
        if (j % modToIncrement == 0 and modToIncrement != 1):
            updateProgressBar(prev, prev+1, window)
            prev = prev+1
        
        # Update progress bar everytime because total frames <= 80
        elif (modToIncrement == 1):
            updateProgressBar(prev, prev+valToIncrementBy, window)
            prev = prev+valToIncrementBy
    
    # Update the GUI window to show the corrected video frames
    updateProgressBar(prev, 90, window)  
    window['-FOLDER-'].update(visible=True)
    window['-FILE LIST-'].update(visible=True)
    window['-CORRECT-'].update(visible=True)
    window['-BROWSE-'].update(visible=True)
    # Resize the image to fit the window
    data = imageToData(pilImg, window["-IMAGE-"].get_size())
    window['-IMAGE-'].update(data=data)
    updateProgressBar(90, 101, window)  

    window['-EXPORT-'].update(visible=True, disabled=False, button_color=('#FFFFFF', '#004F00'))
    window['-ProgressText-'].update(visible=False)
    window['-ProgressBar-'].update(visible=False)
    
    window['-PAD FOR CORRECTION-'].Widget.master.pack_forget()
    window['-PAD FOR CORRECTION-'].update(visible=False)
    
    defaultWindow(window, True, False)

    return listOfCorrectedFrames

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
    window['controls_cv'].update(visible=False)
    window['controls_cv'].Widget.master.pack_forget() 
    window['fig_cv'].update(visible=False)
    window['fig_cv'].Widget.master.pack_forget() 
    window['-FOLDROW-'].Widget.master.pack_forget() 
    window['-FILE LIST-'].Widget.master.pack_forget() 
    window['-CORRECT-'].Widget.master.pack_forget()
    window['-MODIFY-'].Widget.master.pack_forget()
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
    data = imageToData(pilImage, window['-IMAGE-'].get_size(), blur=True)
    window['-IMAGE-'].update(data=data) 

    window['-ProgressText-'].Widget.master.pack()
    window['-ProgressBar-'].Widget.master.pack()
    
    # window['-PAD FOR CORRECTION-'].Widget.master.pack()
    # window['-PAD FOR CORRECTION-'].update(visible=True)

    window['-ProgressText-'].update(visible=True)
    window['-ProgressBar-'].update(visible=True)
     
# ------------------------------------------------------------------------------  

def updateProgressBar(start,end, window):
    """ 
        Args:    start   --> integer signifying where to start the updating
                 end     --> integer signifying where to end the updating
                 window  --> the data of the window that is displayed to user
        Returns: None
        Summary: This function updates the progress bar with the window based
                 on the passed in values of start/end.
    """
    
    for i in range(start,end):
        window['-ProgressBar-'].update(i)
        
# ------------------------------------------------------------------------------  

def reformatScreen(window, btnClick):
    """ 
        Args:    window   --> PySimpleGui Window: The main window running the application
                 btnClick --> boolean: keep track of how to redisplay window smoothly
        Returns: None
        Summary: Update the display of the PySimpleGUI Window based on the value of
        btnClick. If btnClick is False, the function hides some elements and displays
        others, while if btnClick is True, the function hides a different set of
        elements and displays yet another set.
    """
        
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
        window['controls_cv'].update(visible=True)
        window['-FOLDER-'].update(visible=False)
        window['-FILE LIST-'].Widget.master.pack_forget() 
        window['-CORRECT-'].update(visible=False)
        window['-MODIFY-'].update(visible=False)
        window['-BROWSE-'].update(visible=False)
        window['-EXPORT-'].update(visible=False)
        window['-TITLE-'].update('Manual Correction Instructions')
        window['-MANUAL DESCRIPTION-'].update(visible=True)
        window['-UNDO-'].update(visible=True)
        window['-DONE-'].update(visible=True)
    
    # Fixes "correctWindow" display issues
    elif (btnClick == True):

        window['-FILETEXT-'].update(visible=False)
        window['-FILENAME-'].update(visible=False)
        window['-SPACE1-'].update(visible=False)
        window['-SPACE2-'].update(visible=False)
        
        window['-ProgressText-'].Widget.master.pack_forget()
        window['-ProgressBar-'].Widget.master.pack_forget()
        
        window['-IMAGE-'].Widget.master.pack_forget() 
        window['-FOLDROW-'].Widget.master.pack_forget() 
        window['-FILE LIST-'].Widget.master.pack_forget() 
        window['-CORRECT-'].Widget.master.pack_forget()
        window['-MODIFY-'].Widget.master.pack_forget()
        window['-EXPORT-'].Widget.master.pack_forget() 
        window['-HELP-'].Widget.master.pack_forget() 
        window['-QUIT-'].Widget.master.pack_forget() 

        window['-PREVIOUS BTN-'].update(visible=True)
        window['-SPACE1-'].update(visible=True)
        window['-FILETEXT-'].update(visible=True)
        window['-FILENAME-'].update(visible=True)
        window['-SPACE2-'].update(visible=True)
    
        window['controls_cv'].Widget.master.pack() 
        window['controls_cv'].update(visible=True)
        window['fig_cv'].Widget.master.pack() 
        window['fig_cv'].update(visible=True)
        
        window['-FOLDER-'].Widget.master.pack_forget() 
        window['-BROWSE-'].Widget.master.pack_forget() 
    
        window['-FOLDROW-'].Widget.master.pack()
        window['-TITLE-'].update('Manual Correction Instructions')

        manualDescription = "Click the lowest and highest points of the horizon. To remove the most recent point, click the `Undo` button. Once you are done, click 'Done'."
        manualDescription = textwrap.fill(manualDescription, 52)
        
        window['-MANUAL DESCRIPTION-'].Widget.master.pack(side='left', padx=(0,0), pady=(0,0)) 
        window['-MANUAL DESCRIPTION-'].update(visible=True)
        window['-MANUAL DESCRIPTION-'].update(manualDescription)
        window['-CORRECT-'].Widget.master.pack()
        window['-MODIFY-'].Widget.master.pack()
        window['-EXPORT-'].Widget.master.pack() 
        window['-CORRECT-'].update(visible=False)
        window['-MODIFY-'].update(visible=False)
        window['-EXPORT-'].update(visible=False)
        window['-DONE-'].Widget.master.pack() 
        window['-DONE-'].update(visible=True)
        window['-UNDO-'].Widget.master.pack() 
        window['-UNDO-'].update(visible=True)
        window['-HELP-'].Widget.master.pack() 
        window['-HELP-'].update(visible=True)
        window['-QUIT-'].Widget.master.pack() 
        window['-QUIT-'].update(visible=True)


# ------------------------------------------------------------------------------  

def defaultWindow(window, correctedStatus, selectedImage):
    """ 
        Args:    window          --> PySimpleGui Window: The main window running the application
                 correctedStatus --> bool: if image is corrected, title text gets updated, else is default title
                 selectedImage   --> bool: if a new image was corrected, display modify button and disable correct
        Returns: None
        Summary: This function modifies the layout of the PySimpleGui window to show/hide elements
                 based on the passed in values of correctedStatus and selectedImage.
    """

    window['-PREVIOUS BTN-'].update(visible=False)
    window['-TITLE-'].update(visible=False)
    window['-MANUAL DESCRIPTION-'].update(visible=False)
    window['controls_cv'].update(visible=False)
    window['fig_cv'].update(visible=False)
    window['-UNDO-'].update(visible=False)
    window['-DONE-'].update(visible=False)

    window['controls_cv'].Widget.master.pack_forget() 
    window['fig_cv'].Widget.master.pack_forget() 
    window['-MANUAL DESCRIPTION-'].Widget.master.pack_forget() 
    window['-FOLDROW-'].Widget.master.pack_forget() 
    window['-FILE LIST-'].Widget.master.pack_forget() 
    window['-CORRECT-'].Widget.master.pack_forget()
    window['-MODIFY-'].Widget.master.pack_forget()
    window['-EXPORT-'].Widget.master.pack_forget() 
    window['-UNDO-'].Widget.master.pack_forget()
    window['-DONE-'].Widget.master.pack_forget() 
    window['-HELP-'].Widget.master.pack_forget() 
    window['-QUIT-'].Widget.master.pack_forget() 
    window['-IMAGE-'].Widget.master.pack()
    window['-IMAGE-'].update(visible=True)
    window['-FOLDROW-'].Widget.master.pack()
    window['-FOLDROW-'].update(visible=True)
    window['-FOLDROW-'].Widget.update()

    # if image/video was corrected, update title to alert user that the correction was completed
    if correctedStatus:
        window['-TITLE-'].update('SkyFix360 - COMPLETED', visible=True)
    else:
        window['-TITLE-'].update('SkyFix360', visible=True)

    window['-FOLDROW-'].Widget.master.pack()
    window['-FOLDER-'].Widget.master.pack(side='left', padx=(0,0), pady=(0,0))
    window['-FOLDER-'].update(visible=True)
    window['-BROWSE-'].Widget.master.pack(side='left', padx=(0,0), pady=(0,0))
    window['-BROWSE-'].update(visible=True)
    window['-FILE LIST-'].Widget.master.pack()
    window['-FILE LIST-'].update(visible=True)
    window['-FILE LIST-'].Widget.update()
    window['-CORRECT-'].Widget.master.pack()
    window['-CORRECT-'].update(visible=True)

    # if image was corrected, display modify button and disable correct on window
    if selectedImage:
        window['-MODIFY-'].Widget.master.pack()
        window['-MODIFY-'].update(visible=True)
        window['-CORRECT-'].update(disabled=True, button_color=('grey', sg.theme_button_color_background()))

    window['-EXPORT-'].Widget.master.pack()
    window['-EXPORT-'].update(visible=True)
    window['-HELP-'].Widget.master.pack()
    window['-QUIT-'].Widget.master.pack()


# ------------------------------------------------------------------------------

class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        """ 
            Args:     *args    --> Variable length argument list.
                      **kwargs --> Arbitrary keyword arguments.
            Returns: None
            Summary: Defines a custom toolbar with a subset of the items from the default toolbar.
        """

        # tuple of toolbar items to be excluded from the default toolbar.
        toolitems = (
            ('Pan'), (None), ('Zoom'), ('Home'), ('Back'), ('Forward'), ('Subplots'), ('Save')
        )

        # list comprehension that sets the toolitems attribute of the instance of the Toolbar class
        self.toolitems = [t for t in NavigationToolbar2Tk.toolitems if t[0] not in toolitems]
        super().__init__(*args, **kwargs)
        
# ------------------------------------------------------------------------------

def main():
    window = createWindow() # Create MAIN window of the program
    runEvents(window)       # Run Tasks
    window.close()          # Close the window

# ------------------------------------------------------------------------------  

if __name__ == '__main__':
    main()