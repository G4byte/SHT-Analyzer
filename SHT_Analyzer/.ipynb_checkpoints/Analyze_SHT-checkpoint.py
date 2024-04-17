import PySimpleGUI as sg
from analyzer import *
import os.path

labels = ["PtCo1(K)","PtCo2(K)","H2-Press(Torr)", "VAC-PM","VAC-CC10 (Pa)"]
unit_dict = {"PtCo1(K)":"Temperature [K]","PtCo2(K)":"Temperature [K]",\
             "VAC-CC10 (Pa)":"Pressure [Pa]", "VAC-PM":"Pressure [mbar]",\
             "H2-Press(Torr)" : "Pressure [Torr]"}

measurement_menu_def = ["Select measurement", labels]
minimum_window = "24 h"
label = ""

sg.LOOK_AND_FEEL_TABLE["CustomTheme"] = {'BACKGROUND': '#000000',\
                                        'TEXT': '#ffffff',\
                                        'INPUT': '#000000', 
                                        'TEXT_INPUT': '#ffffff',\
                                        'SCROLL': '#99CC99',\
                                        'BUTTON': ('#ffffff', '#d62728'),\
                                        'PROGRESS': ('#D1826B', '#CC8019'),\
                                        'BORDER': 1, 'SLIDER_DEPTH': 0,  'PROGRESS_DEPTH': 0, }
  
sg.theme("CustomTheme") 

# First the window layout in 2 columns

file_list_column = [
    [
        sg.Text("Data Folder"),
        sg.In(enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]

plot_viewer_column = [
    [sg.Text("Choose a folder on the left and select a file")],\
    [sg.Text("File selected: "), sg.Text(auto_size_text=True, key="-TOUT-")],\
    [sg.Text("Start date of data: "), sg.Text(auto_size_text=True, key="-START DATE-")],\
    [sg.Text("End date of data: "), sg.Text(auto_size_text=True, key="-END DATE-")],\


    [sg.ButtonMenu(button_text = "Select measurement", menu_def = measurement_menu_def,\
                   auto_size_button = True, key = "-SELECT MEASUREMENT-")],\
    [sg.Text("Units: "), sg.Text(key = "-MEASOUT-")],\
    [sg.Text("Measurement: "), sg.Text(key = "-UNITOUT-")],\
    [sg.Checkbox("Show entire time range", key = "-FULL PLOT-")],
    [sg.Text("Minimum measurement window: "),\
     sg.In(minimum_window, enable_events=True, size=20, key = "-MINOUT-")],\
    [sg.Button("Show plot", auto_size_button = True, disabled = True, key = "-SHOW PLOT-"),\
     sg.Checkbox("Include fit", key = "-INCLUDE FIT-")],\
    [sg.Button("Generate warming rate trends", auto_size_button = True, disabled = True,\
               key = "-TRENDS PLOT-")],\
]

layout = [
    [
        sg.Column(file_list_column, expand_x = True, expand_y = True),
        sg.VSeperator(),
        sg.Column(plot_viewer_column, expand_x = True, expand_y = True),
        
    ]
]

window = sg.Window("SHT Measurement Viewer", layout, resizable = True)
fnames = []

while True:
        
    event, values = window.read()
    
    if event == "Exit" or event == sg.WIN_CLOSED:
        window.close()
        break
        
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []
    
        fnames = [f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".csv"))
        ]
        window["-FILE LIST-"].update(fnames)

        if label != "":
            window["-SHOW PLOT-"].update(disabled = False)
            window["-TRENDS PLOT-"].update(disabled = False)
        
    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update(values["-FILE LIST-"][0])
            
            sa = SHT_Analyzer(filename)
            window["-START DATE-"].update(sa.abs_start)
            window["-END DATE-"].update(sa.abs_end)

        except:
            pass
            
    if event == "-SELECT MEASUREMENT-":
        try:
            
            label = str(values["-SELECT MEASUREMENT-"])
            unit_selected = unit_dict[label]
            window["-MEASOUT-"].update(label)
            window["-UNITOUT-"].update(unit_selected)
            
            if fnames != []:
                window["-SHOW PLOT-"].update(disabled = False)
                window["-TRENDS PLOT-"].update(disabled = False)
        except:
            pass
    if event == "-MINOUT-":
        try:
            minimum_window = values["-MINOUT-"]
        except:
            pass

    if event == "-SHOW PLOT-":
        # try:
        if window["-FULL PLOT-"].get():
            sa.process_data(label, unit_selected, min_duration = minimum_window, \
                        with_fit = window["-INCLUDE FIT-"].get(), between = (sa.abs_start, sa.abs_end))
        else:
            sa.process_data(label, unit_selected, min_duration = minimum_window,\
                        with_fit = window["-INCLUDE FIT-"].get())
        # except:
        #     pass 
    if event == "-TRENDS PLOT-":
        try:
            dates = []
            datetimes = []
            slopes = []
            errs = []
            
            for i, filepath in enumerate(fnames):
                sg.one_line_progress_meter("", i, len(fnames), orientation = "h")
                if filepath.endswith(".csv"):
                    sa = SHT_Analyzer(os.path.join(folder, filepath))
                    sa.process_data(label, unit_selected, min_duration = minimum_window,\
                            with_fit = False, show_plot = False)
    
                    dates.append(sa.dates)
                    datetimes.append([dt.strptime(date, "%d %B %Y") for date in sa.dates])
                    slopes.append(sa.slopes)
                    errs.append(sa.slope_errs)
                    
            dates = list(chain(*dates))
            datetimes = list(chain(*datetimes))
            slopes = np.array(list(chain(*slopes)))
            errs = np.array(list(chain(*errs)))
            show_warming_trends(datetimes, slopes, errs, dates, label)
            plt.show()
        except:
            pass
    