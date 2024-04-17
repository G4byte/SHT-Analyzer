from graphing_tools import *
from format_tools import *
from fit_tools import *
from scipy.optimize import curve_fit
from itertools import chain


class SHT_Analyzer:
# Catchall analyzer class: stores resampled data, 
# fit parameters, error, plotting functions 

    def __init__(self, filepath):
        self.raw_data = pd.read_csv(filepath)
        self.all_data = bin_by_minute(standardize_datetime(filepath))
        # Bins data into 1min intervals
        self.dt_data = self.all_data["date-time"]
        
        self.abs_start = self.dt_data.iloc[0]
        self.abs_end = self.dt_data.iloc[-1]
        
        self.mask = mask_between(self.dt_data, self.abs_start,\
                                 self.abs_end)
        # Include entire range of times by default
        self.cold_ranges = find_cold_ranges(self.all_data)
        # Get ranges of time where experiment is cold
        self.uncert = 1
        # Default uncertainty
        self.zscore = 2
        # Within how many standard deviations to fit data
        
    def process_data(self, col, data_label, between = (None, None), show_plot = True,\
                     with_fit = True, min_duration = "12h"):

        min_duration = timedelta_from_duration(min_duration)
        # Sets the shortest window of time to be analyzed
        
        start_time, end_time = between
        if between == (None, None):
            # No specific window of time desired; analyze all
            ranges = self.cold_ranges
            self.start_time = self.dt_data.iloc[0]
            self.end_time = self.dt_data.iloc[-1]
        else:
            # Specify window
            ranges = [between]
            self.start_time = dt.strptime(start_time, "%Y/%m/%d %H:%M:%S") if type(start_time) == str else start_time 
            self.end_time = dt.strptime(end_time, "%Y/%m/%d %H:%M:%S") if type(end_time) == str else end_time
        
        self.dates, self.masks, self.slopes, self.intercepts,\
        self.slope_errs, self.intercept_errs, self.chi_sq, self.DOF = [],[],[],[],[],[],[],[]
        # Lists to store data; not sure if this could be optimized

        
        for start_time, end_time in ranges:

            start_time = pd.Timestamp(start_time) + timedelta(hours = 1)
            end_time = pd.Timestamp(end_time) - timedelta(seconds = 600)
            # Truncate 1 hour from start and 10 mins from end to avoid edge values
            
            
            # print(start_time, end_time)

            
            if pd.Timedelta(end_time - start_time).total_seconds() > min_duration.total_seconds():
                mask = mask_between(self.dt_data, start_time, end_time)
                # Selects window specified by [start_time, end_time]
                
                self.data = self.all_data[col]
                # Sets specific Series of interest

                self.data, mask, self.uncert = \
                apply_mask(start_time, end_time, min_duration, mask,self.dt_data,\
                           self.data, col, data_label, self.zscore, self.uncert)
            
                t_data = (self.dt_data - self.dt_data[0]).dt.total_seconds().loc[mask]
                # Turns timestamps into seconds since "t = 0" 
                # so we can look at warming / second

                date = pd.Timestamp(start_time + (end_time - start_time) / 2).strftime("%d %B %Y")
                # Sets the "date" of a cold period
                # to the middle date in the window
        
                fitparams, fit_errs = fit_format(curve_fit(lin_fit, t_data, self.data))
                slope, intercept = fitparams
                slope_err, intercept_err = fit_errs
                chi_sq = get_chi_sq(self.data, lin_fit(t_data, slope, intercept), self.uncert)
                DOF = len(self.data)
                # Gets fit parameters and error (error = sqrt(diag(cov_matrix)))

                self.dates, self.masks, self.slopes, self.intercepts,\
                self.slope_errs, self.intercept_errs, self.chi_sq, self.DOF = \
                append_to_each([self.dates, self.masks, self.slopes, self.intercepts,\
                                self.slope_errs, self.intercept_errs, self.chi_sq, self.DOF],\
                               [date, mask, slope, intercept, slope_err, intercept_err, chi_sq, DOF])
                # Append fit data to respective lists
                
                
                if show_plot:
                    show_fits(self.dt_data, mask, self.data, col, with_fit, t_data, slope,\
                              intercept, chi_sq, DOF, start_time, end_time, data_label)
        plt.show()
