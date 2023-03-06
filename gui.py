import PySimpleGUI as sg
from matplotlib.pyplot import margins

def main():
    
    window = createWindow() # Create window

    runEvents(window) # Run Tasks

    window.close() # Close the window

def createWindow():
    sg.theme ("DarkGrey1")

    firstRow = [
            [sg.Image(key="-IMAGE-", background_color = "black", size=(1000, 500))], 
            ]
    
    secondRow = [ #first col
        [sg.Column([[sg.Text("SkyFix360", font="bold", size=(200, 1))],
        [sg.In (size=(25,1), enable_events=True, key="-FOLDER-"), sg.FolderBrowse()], 

    ], pad=(10, 10), size=(400, 100)),
            #second col
            sg.Column([[sg.Listbox(values=[], enable_events=True, size=(40,10), key="-FILE LIST-")]
            
            ], 
            pad=(10, 10), size=(300, 150)),

            #third col
            sg.Column([[sg.Button("Correct", key='-CORRECT-')],
            [sg.Button("Export ", key='-EXPORT-')],
            ], 
            pad=(10, 10), size=(100, 75))],

            [sg.Button("Help", key='-HELP-', size=(None, 1)), sg.Button("Quit", size=(None, 1))]
    ], 

    layout = [ firstRow, secondRow ]

    window = sg.Window('SkyFix360', layout, element_justification='c')
            
    # Display the window
    # window = sg.Window ("SkyFix360", layout, element_justification='c', resizable = True, finalize = True)
    # window.bind('<Configure>', '-CONFIG-') # Bind to config so can check when window size changes

    return window

def runEvents(window):
    while True:
        event, values = window.read()

        if event == "Quit" or event == sg.WIN_CLOSED:
            break

if __name__ == '__main__':
    main()
