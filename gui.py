'''
    NCAA
    GUI.py
    Senior Seminar 2023
'''

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

def createWindow():
    sg.theme ("DarkGrey1")

    firstRow = [[sg.Text("File:", font="Arial 10 bold", size=(4,1), visible=False, key="-FILETEXT-"), sg.Text(size=(0, 1), key="-FILENAME-", visible=False)],
                [sg.Image(key="-IMAGE-", background_color = "black", size=(1000, 500))],]
    
    secondRow = [ #first col
        [sg.Column([[sg.Text("SkyFix360", font= ("Arial", 16, "bold"), size=(200, 1))],
        [sg.In (size=(25,1), enable_events=True, key="-FOLDER-"), sg.FolderBrowse(size=(10, 1))]], pad=(10, 10), size=(400, 100)),
        
        #second col
         sg.Column([[sg.Listbox(values=[], enable_events=True, size=(45,5), key="-FILE LIST-")]], 
         pad=(10, 10), size=(300, 85)),

        #third col
         sg.Column([[sg.Button("Correct", key='-CORRECT-',disabled=True, button_color=('grey', sg.theme_button_color_background()), size=(10, 1))],
         [sg.Button("Export ", key='-EXPORT-', disabled=True, button_color=('grey', sg.theme_button_color_background()), size=(10, 1))],], 
            pad=(10, 10), size=(100, 75))],

         [sg.Button("Help", key='-HELP-', size=(10, 1)), sg.Button("Quit", key=('-QUIT-'), size=(10, 1))],
         [sg.Canvas(key='controls_cv')],
         [sg.Canvas(key='fig_cv', size=(500 * 2, 200))]
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
            correctMWidnow = correctMethodWindow()
            correctWindow = sg.Window('Correction Method', correctMWidnow, size=(355,195), margins=(20, 20))
            while True:
                correctEvent, correctVal = correctWindow.read()
                if correctEvent == sg.WIN_CLOSED or correctEvent == ('Cancel'):
                    # Close the help popup
                    correctWindow.close()
                    break
                elif correctEvent == 'Manual':
                    # fig = figure.Figure()
                    # ax = fig.add_subplot(111)
                    # DPI = fig.get_dpi()
                    # fig.set_size_inches(505 * 2 / float(DPI), 707 / float(DPI))

                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    DPI = fig.get_dpi()
                    # fig.set_size_inches(505 * 2 / float(DPI), 707 / float(DPI))
                    fig.set_size_inches(505 * 2 / float(DPI), 707 / float(DPI))
                    img = mpimg.imread(fileName)
                    imgplot = plt.imshow(img)
                    plt.grid()

                    x = np.linspace(0, 2 * np.pi)
                    y = np.sin(x)
                    line, = ax.plot(x, y)
                    rs = RectangleSelector(ax, line_select_callback,
                                useblit=False, button=[1],
                                minspanx=5, minspany=5, spancoords='pixels',
                                interactive=True)
                    draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)

        # DISPLAY WINDOW WHEN IMAGE/VIDEO IS CORRECTED
        # successMWindow = successWindow()
        # sucessWindow = sg.Window('Sucess', successMWindow, size=(300,155), margins=(10, 10))
        # while True:
        #     successevent, successVal = sucessWindow.read()
        #     if successevent == sg.WIN_CLOSED or successevent == ('Close'):
        #         # Close the help popup
        #         sucessWindow.close()
        #         window['-SUCCESS-'].update(disabled=False, button_color=('white', sg.theme_button_color_background()))
        #         break
        
        
         
        # if user selects 'Quit' button or default exit button, close window
        if event == ('Quit') or event == sg.WIN_CLOSED:
            break
        
        
# ------------------------------------------------------------------------------  
'''
    def imageToData - the method calcuates the bytes of the image to draw the terrain
                      map after reading and storing the elevation values, it will
                      update the image size.
    @ param image   - passing the image to update/draw again on the GUI
    @ param resize  - whether or not the image should be resized
    precondition    - image should be valid after reading the array, method should
                      be called in main function
    postcondition   - image size is updated & image is displayed in GUI; method
                      returns the new image with its updated size
'''
def imageToData(pilImage, resize):
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

'''
'''
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


'''
'''
def line_select_callback(eclick, erelease):
    fig = figure.Figure()
    ax = fig.add_subplot(111)
    DPI = fig.get_dpi()
    fig.set_size_inches(505 * 2 / float(DPI), 707 / float(DPI))

    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata

    rect = plt.Rectangle( (min(x1,x2),min(y1,y2)), np.abs(x1-x2), np.abs(y1-y2) )
    print(rect)
    ax.add_patch(rect)
    fig.canvas.draw()

class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)
    

# ------------------------------------------------------------------------------  

def main():
    window = createWindow() # Create window
    runEvents(window) # Run Tasks
    window.close() # Close the window

# ------------------------------------------------------------------------------  

if __name__ == '__main__':
    main()