'''
    NCAA
    GUI.py
    Senior Seminar 2023
'''

from pydoc import visiblename
import PySimpleGUI as sg
from matplotlib.pyplot import margins
import PIL
import os
import io
import numpy as np
from matplotlib.widgets  import RectangleSelector
import matplotlib.figure as figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import sys
import cv2
import matplotlib.image as mpimg
from sqlalchemy import false
from equirectRotate import EquirectRotate, pointRotate
import time


def createWindow():
    sg.theme ("DarkGrey1")

    firstRow = [[sg.Text("File:", font="Arial 10 bold", size=(4,1), visible=False, key="-FILETEXT-"), sg.Text(size=(0, 1), key="-FILENAME-", visible=False)],
                [sg.Image(key="-IMAGE-", background_color = "black", size=(1000, 500))],
                [sg.Canvas(key='controls_cv')],
                [sg.Canvas(key='fig_cv', size=(1000, 500), visible=False)]
                ]

    secondRow = [ #first col
        [sg.Column([[sg.Text("SkyFix360", font= ("Arial", 16, "bold"), size=(200, 1), key="-SKYTEXT-")],
        [sg.In (size=(25,1), enable_events=True, key="-FOLDER-"), sg.FolderBrowse(size=(10, 1), key="-BROWSE-")]], pad=(10, 10), size=(400, 100), key="-FOLDROW-"),
        
        #second col
         sg.Column([[sg.Listbox(values=[], enable_events=True, size=(45,5), key="-FILE LIST-")]], 
         pad=(10, 10), size=(300, 85)),

        #third col
         sg.Column([[sg.Button("Correct", key='-CORRECT-',disabled=True, button_color=('grey', sg.theme_button_color_background()), size=(10, 1))],
         [sg.Button("Export ", key='-EXPORT-', disabled=True, button_color=('grey', sg.theme_button_color_background()), size=(10, 1))],], 
            pad=(10, 10), size=(100, 75))],

         [sg.Button("Help", key='-HELP-', size=(10, 1)), sg.Button("Quit", key='-QUIT-', size=(10, 1))]
    ] 

    layout = [ firstRow, secondRow ]

    window = sg.Window('SkyFix360', layout, element_justification='c')
            
    # Display the window
    # window = sg.Window ("SkyFix360", layout, element_justification='c', resizable = True, finalize = True)
    # window.bind('<Configure>', '-CONFIG-') # Bind to config so can check when window size changes

    return window


def helpWindow():
    helpLayout = [[sg.Text('Need Help?', font=("Arial", 14, "bold"), size=(40, None), auto_size_text=True, justification='center', pad=(0, 5))],
                  [sg.Text("  1.   Click the 'Browse' button to select a folder containing any\n        images or videos.")],
                  [sg.Text("  2.   Files ending with .MP4, .JPEG, and .JPG will appear in the\n        white space to the right.")],
                  [sg.Text("  3.   Select an image/video from this panel. It will then be\n        shown on the preview screen above.")],
                  [sg.Text("  4.   Click 'Correct' button to begin the correction process. Follow\n        the steps in the pop-up window.")],
                  [sg.Text("  5.   Select 'Export' to save your corrected photo/video to\n        your device.")],
                  [sg.Text("  6.   If you wish to quit at any time, select the 'Quit' button.")],
                  [sg.Button("Close", size=(10, 1), pad=((135), (20, 0)))]]
    return helpLayout


def correctMethodWindow():
    correctionLayout = [ [sg.Text('Choose a Correction Method', font=("Arial", 16, "bold"), size=(40, None), auto_size_text=True, justification='center', pad=(0, 5))],      
                         [sg.Button('Manual', size=(10,1)), sg.Text('This method allows for custom specification \nof the horizon by a drawing from the user.\n')], 
                         [sg.Button('Automatic', size=(10,1)), sg.Text('This method automaticaaly finds the horizon \nline and corrects the image/video.')], 
                         [sg.Button("Cancel", size=(10, 1), pad=((135), (20, 0)))]]
    return correctionLayout


def successWindow():
    successLayout = [[sg.Text('Your image/video has been successfully corrected.', font=("Arial", 18), size=(25, None), auto_size_text=True, justification='center')],
                        [sg.Text('Close this window and click the "Export" button to save your photo/video to your device.', size=(40, None), auto_size_text=True, justification='center')],
                        [sg.Button("Close", size=(10, 1), pad=(100, 10))]]
    return successLayout



def runEvents(window):
    
    fileNames = []
    while True:
        event, values = window.read()
        # if user selects 'Help' button, display help window with instructions
        if event == ('-HELP-'):
            helplayout = helpWindow()
            help = sg.Window('Help', helplayout, size=(370, 300), margins=(15, 15))
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
            window["-FILE LIST-"].update (fileNames)



        # User chose file from File List
        if event == "-FILE LIST-":   
            
            try:
            
                fileName = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
                
                
                # display filename in appropriate spot in right column
                window["-FILENAME-"].update(fileName)  
                
                window["-FILETEXT-"].update(visible=True)
                window["-FILENAME-"].update(visible=True)
        
                # Open the image
                pilImage = PIL.Image.open(fileName)
                
                # Get image data, and then use it to update window["-IMAGE-"]
                data = imageToData(pilImage, window["-IMAGE-"].get_size())
                window['-IMAGE-'].update(data=data) 
                
                
                window['-CORRECT-'].update(disabled=False, button_color=('#FFFFFF', '#004F00'))
        
        
            except:
                pass





        # if 'Correct' button is not disabled & clicks, display appropriate window
        if event == ('-CORRECT-'):
            correctMWindow = correctMethodWindow()
            correctWindow = sg.Window('Correction Method', correctMWindow, size=(355,195), margins=(20, 20))
            while True:
                correctEvent, correctVal = correctWindow.read()
                if correctEvent == sg.WIN_CLOSED or correctEvent == ('Cancel'):
                    # Close the help popup
                    correctWindow.close()
                    break
                elif correctEvent == 'Manual':
                    window['-IMAGE-'].update(visible=False)
                    window['-IMAGE-'].Widget.master.pack_forget() 
                    window['fig_cv'].update(visible=True)

                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    DPI = fig.get_dpi()
                    # fig.set_size_inches(505 * 2 / float(DPI), 707 / float(DPI))
                    fig.set_size_inches(505 * 2 / float(DPI), 500 / float(DPI))
                    img = mpimg.imread(fileName)
                    imgplot = plt.imshow(img)
                    # pid = fig.canvas.mpl_connect('key_press_event', lambda event: press(event, fig, pid))  
                    # cid = fig.canvas.mpl_connect('button_press_event', lambda event: press(event, fig, cid))
                    plt.grid()

                    # Define a list to store the coordinates of the line
                    lineCoords = []

                    # Define a function to handle mouse clicks
                    def onclick(event):
                        # Append the coordinates of the click to the list
                        lineCoords.append((event.xdata, event.ydata))

                        # If there are two or more points in the list, draw a line
                        if len(lineCoords) > 1:
                            ax.plot([lineCoords[-2][0], lineCoords[-1][0]],
                                    [lineCoords[-2][1], lineCoords[-1][1]],
                                    color='r')
                            fig.canvas.draw()
                            print(lineCoords)

                    def onkey(event):
                        global closeWin
                        # If the key pressed is 'z' and there are points to remove, remove the last point
                        if event.key == 'z' and len(lineCoords) > 0:
                            lineCoords.pop()
                            # Clear the plot and redraw the lines
                            ax.clear()
                            ax.imshow(img)
                            plt.grid()
                            for i in range(len(lineCoords)-1):
                                ax.plot([lineCoords[i][0], lineCoords[i+1][0]],
                                        [lineCoords[i][1], lineCoords[i+1][1]],
                                        color='r')
                            fig.canvas.draw()

                        if event.key == 'q':
                            # Find the min and max x and y values in the list of coordinates
                            x_coords, y_coords = zip(*lineCoords)
                            min_x, max_x = min(x_coords), max(x_coords)
                            min_y, max_y = min(y_coords), max(y_coords)
                            print(f"Min x: {min_x}, Max x: {max_x}, Min y: {min_y}, Max y: {max_y}")
                            
                            ix = min_x
                            iy = min_y

                            fig.canvas.mpl_disconnect(cid)
                            fig.canvas.mpl_disconnect(cid2)
                            
                            # correctImageMan(fileName, ix, iy)
                            fixScreen(window, fileName)

                    # Connect the onclick function to the mouse click event
                    cid = fig.canvas.mpl_connect('button_press_event', onclick)
                    cid2 = fig.canvas.mpl_connect('key_press_event', onkey)

                    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)
                    # manualCorrect(window, fileName)
            # correctWindow.close()
            # DISPLAY WINDOW WHEN IMAGE/VIDEO IS CORRECTED
            print("Success")
            successMWindow = successWindow()
            sucessWindow = sg.Window('Success', successMWindow, size=(300,155), margins=(10, 10))
            while True:
                successevent, successVal = sucessWindow.read()
                if successevent == sg.WIN_CLOSED or successevent == ('Close'):
                    # Close the help popup
                    sucessWindow.close()
                    # window['-SUCCESS-'].update(disabled=False, button_color=('white', sg.theme_button_color_background()))
                    break
        
        
         
        # if user selects 'Quit' button or default exit button, close window
        if event == ('Quit') or event == sg.WIN_CLOSED:
            break
        
        
# ------------------------------------------------------------------------------  
        
def imageToData(pilImage, resize):
    """ 
    Insert comments here
    """
    
    # store current image and its width and height
    img = pilImage.copy() 
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

def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()

    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)

class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)

def correctImageMan(fileName, ix, iy):
    print('\n Now rotating the image to straighten the horizon.')
    src_image = cv2.imread(fileName)
    h, w, c = src_image.shape
    print("\n Input file's height, width, colors =", h,w,c)

    # Do a 'yaw' rotation such that ix position earth-sky horizon is 
    # at the middle column of the image. Fortunately for an equirectangular
    # image, a yaw is simply sliding the image horizontally, and is done very
    # fast by np.roll.
    shiftx=int(w/2 - ix)
    src_image = np.roll(src_image, shiftx, axis=1) 

    # If iy>0 then the user selected the lowest point of the horizon.
    # After the above 'yaw', the true horizon at the middle of the image
    # is still (iy - h/2) pixels below the camera's equator. This is
    # (iy - h/2)*(180)/h degrees below the camera's equator. So rotate the
    # pitch of the yaw-ed rectilinear image by this amount to get a nearly
    # straight horizon.
    myY, myP, myR = 0, (iy - h/2)*180/h , 0

    # If iy<0 then the user actually recorded the highest point. That
    # is, the true horizon is (h/2 - |iy|) pixels above the camera's
    # equator. So rotate the pitch of the yaw-ed rectilinear image by the
    # amount -(h/2 - |iy|)*180/h to get a nearly straight horizon.
    if iy < 0 :
        myP = -(h/2 - np.abs(iy))*180/h


    print('\n Doing the final rotation (pitch =',str(f'{myP:.2f}'),
            'deg). This can take a while ...')
    # rotate (yaw, pitch, roll)
    equirectRot = EquirectRotate(h, w, (myY, myP, myR))
    rotated_image = equirectRot.rotate(src_image)
    ###################################################################

    final_image = cv2.rotate(rotated_image, cv2.ROTATE_180)

    opfile = os.path.splitext(fileName)[0]+'_f.jpg'
    cv2.imwrite(opfile, final_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    print('\nWrote output file: ', opfile)
    print('Done.')

def fixScreen(window, fileName):
    window['fig_cv'].update(visible=False)
    window['fig_cv'].Widget.master.pack_forget() 
    window['controls_cv'].Widget.master.pack_forget() 
    # window['-FOLDROW-'].update(visible=False)
    window['-FOLDROW-'].Widget.master.pack_forget() 
    # window['-FILE LIST-'].update(visible=False)
    window['-FILE LIST-'].Widget.master.pack_forget() 
    # window['-CORRECT-'].update(visible=False)
    window['-CORRECT-'].Widget.master.pack_forget() 
    # window['-EXPORT-'].update(visible=False)
    window['-EXPORT-'].Widget.master.pack_forget() 
    # window['-HELP-'].update(visible=False)
    window['-HELP-'].Widget.master.pack_forget() 
    # window['-QUIT-'].update(visible=False)
    window['-QUIT-'].Widget.master.pack_forget() 

    window['-IMAGE-'].Widget.master.pack()
    window['-IMAGE-'].update(visible=True)
    opfile = os.path.splitext(fileName)[0]+'_f.jpg'
    pilImage = PIL.Image.open(opfile)
    # Get image data, and then use it to update window["-IMAGE-"]
    data = imageToData(pilImage, window["-IMAGE-"].get_size())
    window['-IMAGE-'].update(data=data)
    
    window['-FOLDROW-'].Widget.master.pack()
    # window['-FOLDROW-'].update(visible=True)
    window['-FILE LIST-'].Widget.master.pack()
    # window['-FILE LIST-'].update(visible=True)
    window['-CORRECT-'].Widget.master.pack()
    # window['-CORRECT-'].update(visible=True)
    window['-EXPORT-'].Widget.master.pack()
    # window['-EXPORT-'].update(visible=True)

    # window.finalize()
    # window.refresh()

# def manualCorrect(window, fileName):




# ------------------------------------------------------------------------------  

def main():
    window = createWindow() # Create window
    runEvents(window) # Run Tasks
    window.close() # Close the window

# ------------------------------------------------------------------------------  

if __name__ == '__main__':
    main()