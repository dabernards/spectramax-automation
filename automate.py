#!/usr/bin/env python3
import numpy as np
import os
import re
import json
import yaml
# import argparse ## https://docs.python.org/3/library/argparse.html

DEBUG=False

def loadSettings():
  # Default settings provided here; settings.yml is loaded, for all variables loaded that appear in default settings will be loaded as global variables.
  default_settings = {
                      'delimiter': '\t', 
                      'omit_lower': 0, 'omit_upper': 1, 
                      'elution_volume': 0.5, 'std_units': "[\u03bcg/ml]",
                      'file_list': [name[:-4] for name in os.listdir() if name[-3:]=='txt' and name[:-3]+'spec' in os.listdir()]
                      }
  try:
    yaml_in = yaml.load(open("settings.yml"), Loader=yaml.Loader)
  except:
    yaml_in = default_settings

  for var in default_settings.keys():
    if var in yaml_in:
      globals()[var] = yaml_in[var]
    else:
      globals()[var] = default_settings[var]
    if DEBUG: print(var, globals()[var])

  
def loadFiles(file):
  # First bit of these text files is pesky, so ignore that initial error. 
  # Unclear if this gets replicated in windows or mac. Open read only. 
  # Matches against lines with double tab or tab and digit (that's the start of the temperature); ignores empty lines, strips whitespace and splits the by tab
  with open(file + '.txt', errors='ignore', mode='r') as f:
    plate_data = [line.strip().split('\t') for line in f if re.match('\t[1-9|\t]', line[0:2]) and line.strip()!='']
  temperature = plate_data[0].pop(0)

  # Read in comma delimited descriptor file
  with open(file + '.spec', errors="ignore", mode="r") as f:
    plate_format = [line.strip().split(delimiter) for line in f if line.strip()!='']

  return plate_data, plate_format


def writeFitData(file, conc_std, abs_std, fit_slope, fit_int):
  with open(file + '.fit', 'w') as f:

    f.write("#Slope	#Intercept\n")
    f.write(str(fit_slope) + "\t" + str(fit_int) + "\n")
    f.write("#Conc	#Absorbance (blank substracted)\n")
    data_out = [[str(conc_std[x]), str(abs_std[x])] for x in range(len(conc_std))]
    for line in data_out:
      f.write("\t".join(line) + "\n")


def checkBlank(raw_blk, tolerance=1):
  # FUTURE FEATURE -- can add some checks for outliers in the blanks -- will need to trouble shoot a bit
  # tolerance is how many standard deviations away from the mean should be discarded
  abs_blk = np.mean(raw_blk)


  return abs_blk


def fitStandards(raw_std, abs_blk, omit_lower, omit_upper, omit_outlier=False, write_data=True, plot_data=False):
  # Pass in raw standard data and averaged blk values from checkBlank()
  # [FUTURE FEATURE] omit_outlier gives option to find outliers (will need to define) and omit from fitting
  # Average all abs_in data
  conc_std = [key for key in raw_std]
  abs_std = [(np.mean(raw_std[key]) - abs_blk) for key in raw_std]
  abs_std_sd = [(np.std(raw_std[key]) - abs_blk) for key in raw_std]

  # Sort, keyed on conc_std -- probably a cleaner way to do this...
  sorted_list = np.argsort(conc_std)
  abs_std = [abs_std[x] for x in sorted_list]
  abs_std_sd = [abs_std[x] for x in sorted_list]
  conc_std = [conc_std[x] for x in sorted_list]

  # Adding in finding outliers will be tricky, this might require user input or something more advanced
  [fit_slope, fit_int] = np.polyfit(abs_std[omit_lower:len(abs_std)-omit_upper], conc_std[omit_lower:len(abs_std)-omit_upper], 1)

  if write_data:
    writeFitData(file, conc_std, abs_std, fit_slope, fit_int)
  if plot_data:
    plotting(abs_std, conc_std, fit_slope, fit_int)

  return float(fit_slope), float(fit_int), conc_std, abs_std

def processData(plate_data, plate_format):
  loc_blk = []
  loc_std = {}
  loc_data = {}
  # Iterate through data in .spec to bucket standards, blanks, and data
  for row in range(len(plate_format)):
    for col in range(len(plate_format[row])):
      data_type = plate_format[row][col][0:3]

      # blanket failsafe -- if entry is blank or user goes out of the way to enter 'jnk', ignore it.
      if data_type == "" or data_type == "jnk": continue

      # blk locations go into loc_blk
      if data_type == "blk": loc_blk.append([row, col])

      # std locations go into loc_std -- since concentrations can be anything, a dictionary is used. If a key exists in the dictionary already -- just append it to the existing array, otherwise an array with the first entry is required.
      elif data_type == "std":
        if float(plate_format[row][col][4:]) not in loc_std:
          loc_std[float(plate_format[row][col][4:])] = []
        loc_std[float(plate_format[row][col][4:])].append([row, col])

      # all other items are considered data and go into loc_data
      else:
        data_dilution = 1
        data_time = -1
        [data_name, params] = plate_format[row][col].split('-')
        data_name = data_name.strip()
        for item in params.split('_'):
          if item[0]=="d":
            data_time=int(item[1:].strip())
          elif item[0]=="x":
            data_dilution=float(item[1:].strip())
          elif item[0]=="n":
            data_name=item[1:].strip()
          else: pass #for now we just use these two parameters
        if data_name not in loc_data:
          loc_data[data_name] = {}
        if data_time==-1: data_time=data_name
        if data_time not in loc_data[data_name]:
          loc_data[data_name][data_time] = []
        loc_data[data_name][data_time].append((row, col, data_dilution))

  raw_blk = [ float(plate_data[row][col]) for [row, col] in loc_blk ]
  ## FUTURE FEATURE -- checkBlank -- this should get integrated into checkBlank behavior

  # Put standards into raw_std dictionary
  raw_std = {}
  for key in loc_std:
    raw_std[key] = [ float(plate_data[row][col]) for [row,col] in loc_std[key] ]


  raw_data = {}
  dilution_data = {}
  for device_key in loc_data:
    raw_data[device_key] = {}
    dilution_data[device_key] = {}
    for time_key in loc_data[device_key]:
      raw_data[device_key][time_key] = [ float(plate_data[row][col]) for (row, col, dilution) in loc_data[device_key][time_key] ]
      dilution_data[device_key][time_key] = [ dilution for (row, col, dilution) in loc_data[device_key][time_key] ]
  # Inelegant way, just want to flatten dilution data -- risky for unaware users
  for device_key in loc_data:
    for time_key in loc_data[device_key]:
      dilution_data[device_key][time_key] = np.mean(dilution_data[device_key][time_key])



  return raw_blk, raw_std, raw_data, dilution_data

def formatOutput(json_data, write_data=True):
  all_data = {}
  for device_key in json_data:
    time_in=[]; abs_in=[]; abs_sd_in=[]; conc_in=[]; dilution_in=[]
    for x in range(len(json_data[device_key])):
      time_in.append(json_data[device_key][x][0])
      abs_in.append(json_data[device_key][x][1])
      abs_sd_in.append(json_data[device_key][x][2])
      conc_in.append(json_data[device_key][x][3])
      dilution_in.append(json_data[device_key][x][4])

    sorted_list = np.argsort(time_in)
    abs_in = [abs_in[x] for x in sorted_list]
    abs_in_sd = [abs_sd_in[x] for x in sorted_list]
    dilution_in = [dilution_in[x] for x in sorted_list]
    conc_in = [conc_in[x] for x in sorted_list]
    time_in = [time_in[x] for x in sorted_list]
    all_data[device_key] = [time_in, abs_in, abs_in_sd, conc_in, dilution_in]


  # Gives element of all_data with max size
  row_output = len(all_data[max(all_data, key=lambda k: len(all_data[k][0]))][0])
  data_out = [[] for x in range(row_output+1)]
  #print(row_output, data_out)
  col_labels = ["day_", "abs_", "abs_sd_", "conc_", "dil_"]
  device_list = [x for x in raw_data.keys()]
  device_list.sort()
  for device in device_list:
    data_out[0].extend([col_labels[x] + device for x in range(5)])

  for x in range(row_output):
    for device in device_list:
      if (x >= len(all_data[device][0])):
        data_out[x+1].extend("" for x in range(5))
        continue
      data_out[x+1].extend(str(all_data[device][y][x]) for y in range(5))

  if write_data:
    with open(file + '.out', 'w') as f:
      for line in data_out:
        f.write("\t".join(line) + "\n")

  return data_out

def plotting(abs_std, conc_std, fit_slope, fit_int):
  import matplotlib.pyplot as plt
  _ = plt.plot(abs_std, conc_std, 'o', label='Original data', markersize=10)
  _ = plt.plot(abs_std, [fit_slope * x + fit_int for x in abs_std], 'r', label='Fitted line')
  _ = plt.legend()
  plt.show()

def writeDictionary(raw_data, dilution_data, abs_blk, fit_slope, fit_int):
  # This is quick and dirty to enable combine.py processing. Can improve elegance here later.
  json_data = {}
  for device_key in raw_data:
    json_data[device_key] = []
    for time_key in raw_data[device_key]:
      time_in = time_key
      abs_in = np.mean(raw_data[device_key][time_key] - abs_blk)
      abs_sd_in = np.std(raw_data[device_key][time_key] - abs_blk)
      dilution_in = dilution_data[device_key][time_key]
      conc_in = (fit_slope * abs_in + fit_int) * dilution_data[device_key][time_key]
      json_data[device_key].append([time_in, abs_in, abs_sd_in, conc_in, dilution_in])
  with open(file + '.dict', 'w') as f:
    json.dump(json_data, f)

  return json_data

###################
loadSettings()

for file in file_list:
  plate_data, plate_format = loadFiles(file)
  raw_blk, raw_std, raw_data, dilution_data = processData(plate_data, plate_format)
  abs_blk = checkBlank(raw_blk)
  [fit_slope, fit_int, conc_std, abs_std] = fitStandards(raw_std, abs_blk, omit_lower, omit_upper)
  json_data = writeDictionary(raw_data, dilution_data, abs_blk, fit_slope, fit_int)
  formatOutput(json_data)

  
