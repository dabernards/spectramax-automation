#!/usr/bin/python3
import json



DEBUG=False

def loadAllData():
  with open("file.list", mode='r') as f:
    file_list = [line.strip() for line in f]

  all_data = {}
  for file in file_list:
    with open(file, mode='r') as f:
      data_in = json.load(f)
    for key in data_in:
      if key not in all_data:
        all_data[key] = []
      all_data[key].extend(data_in[key])
  return all_data

def formatOutput(all_data):
  # Gives element of all_data with max size
  row_output = len(all_data[max(all_data, key=lambda k: len(all_data[k]))])
  data_out = [[] for x in range(row_output+1)]
  col_labels = ["day_", "abs_", "abs_sd_", "conc_"]
  device_list = [x for x in all_data.keys()]
  device_list.sort()
  for device in device_list:
    data_out[0].extend([col_labels[x] + device for x in range(4)])
  for x in range(row_output):
    for device in device_list:
      if (x >= len(all_data[device])):
        data_out[x+1].extend("" for x in range(4))
        continue
      data_out[x+1].extend([str(all_data[device][x][y]) for y in range(4)])
  return data_out

def writeFile(file, data_out):
  with open(file + '.data', 'w') as f:
    for line in data_out:
      f.write("\t".join(line) + "\n")


all_data = loadAllData()

data_out = formatOutput(all_data)
writeFile('data', data_out)
