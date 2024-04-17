import pandas as pd
import numpy as np

def bin_by_minute(df):
# Take mean of all values (dropping NaNs) within the same minute 
# (we don't have better resolution for some data) 
    return df.resample("10 min", on = "date-time").mean().dropna().reset_index()
    
def lin_fit(x,a,b):
# Linear fitting function using scipy curve_fit
    return a*x + b
    
def mask_between(data, start, end):
# Convenience function for boolean masking in a specific range
    return (data >= start) & (data <= end)

def get_chi_sq(data, modelled, uncert):
# Get chi squared given data, a model based on fit, and uncertainty in each datum
    return np.sum((data - modelled)**2 / (uncert**2))

def append_to_each(containers, corresp_vals):
# Helper function to shorten appends
    for i in range(len(containers)):
        containers[i].append(corresp_vals[i])
    return containers
    
def find_cold_ranges(all_data):
# Returns pairs of dateime-convertible strings which bookend 
# windows of time where the target system is cold 

    cond = all_data["PtCo1(K)"] < 4.5
    # Cuts out unimportant data
    
    edges = np.where(np.diff(cond))[0]
    # Gets indices representing "bounds" of cold windows
    
    if len(edges) % 2:
        if cond.iloc[-1]:
            edges = np.insert(edges, -1, -1)
        elif cond.iloc[0]:
            edges = np.insert(edges, 0, 0)
    # Handles cases starting or ending at ~4K, would not propery bin otherwise
    

    dt_data = all_data["date-time"]

    unfiltered_edges = np.array(dt_data.iloc[edges])
    # Gets bookend timstamps but includes random temperature spikes;
    # want to filter these out
    
    diffs = np.diff(unfiltered_edges).astype(float)
    rm_locs = np.where((diffs / 1e9) < (20 * 60))[0] 
    # Convert ns to s, check less than 20 mins apart
    rm_locs = np.concatenate((rm_locs, rm_locs + 1))
    edges = np.delete(unfiltered_edges, rm_locs)
    # Removes bookends that correspond to a random spike (short, usually under 20 mins)

    edges = np.reshape(edges, (-1, 2))
    # Formats output into pairs
    
    return edges

def apply_mask(start_time, end_time, min_duration, mask,\
               dt_data, data, col, data_label, zscore, uncert):
# Refines and applies mask to select specific data of interest
    
    not_mask = np.logical_not(mask)
    if np.all(not_mask):
        mask = not_mask
    # Handles cases where dates provided to 'between' parameter
    # are out of bounds; defaults to full time range
    
    if "temperature" in data_label.lower():
        # Distinguishes PtCo data from other columns
        mask &= (data < 300)
        # Removes random spikes over 300K 
        # (sometimes data spikes to 1e6 K or something)
        if start_time != dt_data.iloc[0] and end_time != dt_data.iloc[-1]:
            mask &= (np.abs(data.loc[mask] - np.mean(data.loc[mask]))\
                      < zscore * np.std(data.loc[mask]))
            # Remove outliers with z-score > self.zscore
        uncert = 0.1
    
    data = data.loc[mask]

    return [data, mask, uncert]
    








    

