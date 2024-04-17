import matplotlib.pyplot as plt
from fit_tools import *
from datetime import datetime as dt 
from datetime import timedelta

def show_fits(dt_data, mask, data, col, with_fit, t_data, slope,\
              intercept, chi_sq, DOF, start_time, end_time, data_label):
# Displays data from cold period with fit line to show 
# warming trend
    s_per_day = 86400
    
    plt.style.use("dark_background")
    
    fig, ax = plt.subplots(figsize = (12,8))
                        
    ax.plot(dt_data.loc[mask], data, "white", label = col[:col.find("(")]\
                    if "(" in col else col)
    
    if with_fit:
        ax.plot(dt_data.loc[mask], lin_fit(t_data, slope, intercept), "r",\
                label = "Warming rate: %.3f K/day,\n $\chi^2$ = %.2f, ndof = %d"\
                % (slope * s_per_day, chi_sq, DOF))
    
    ax.tick_params(axis = "x", labelsize = 8, rotation = 45)
    ax.tick_params(axis = "y", labelsize = 18)
    
    ax.set_ylabel("%s" % data_label, fontsize = 20)
    
    ax.set_title("%s between %s and %s" % (col[:col.find("(")]\
                    if "(" in col else col, str(start_time)[:10],\
                    str(end_time)[:10]), fontsize = 20)
    ax.legend(fontsize = 15)

def show_warming_trends(datetimes, slopes, errs, dates, col):
# Displays warming rates from many cold periods over 
# months/years of operation
    plt.style.use("dark_background")
    s_per_day = 86400

    fig, ax = plt.subplots(figsize = (12,8))

    ax.errorbar(datetimes, slopes * s_per_day, fmt = "ro", yerr = errs * s_per_day,\
                capsize = 5, elinewidth = 0.5)
    
    [ax.annotate(dates[j], (datetimes[j] - timedelta(days = 100),\
                 slopes[j] * s_per_day - 1e-3 * (-1)**(2*j + 1)),\
                 color = "lime" if datetimes[j] == np.max(datetimes)\
                 else "white") for j in range(len(slopes))]
    
    ax.axvspan(dt(2020, 11, 13, 0, 0), dt(2021, 5, 13, 0, 0),\
               color = "lightskyblue", alpha = 0.7, label = "Mask on")
    ax.axvspan(dt(2023, 10, 1, 0, 0), dt(2024, 3, 15, 0, 0),\
               color = "lightskyblue", alpha = 0.7)
    
    ax.set_ylabel("Warming Rate [K/day]", fontsize = 20)
    
    ax.set_title("%s Warming Rate While He Compressor ON" % col[:col.find("(")], fontsize = 20)
    ax.grid(color = "lightgrey")
    ax.legend(fontsize = 15)
    ax.set_xlim(left = dt(2019, 1, 1, 0, 0))
    
    
        