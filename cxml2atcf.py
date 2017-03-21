from TropCy import atcf
from TropCy import cxml
import xml.etree.ElementTree as ET
import sys
import os
from datetime import datetime
import traceback
# pylint: disable=W0311, C0326, C0103, C0301

def save_atcf(basin, number, time, data, fid):
    outstr = atcf.line_out( basin, number, time, data['tech'], data['fhr'], data['lat'] , data['lon'], data['vmax'], data['mslp'] )
    fid.write(outstr)

def cxml2atcf(fname):
  """Read all forecasts for non errored storms and save to appropriate adeck file"""
  if not os.path.isfile(fname):
      print("No file found -- "+fname)
      return
  tree = ET.parse(fname)
  xml_root = tree.getroot()
  ##  Get analysis info from xml.  Defines the storms that exist
  ## Name is optional here and may be empty for TDs
  anl_data = cxml.get_analysis(xml_root)

  cyNo = [ atcf.basin2short(anl_data[idi]['basin'])+str(anl_data[idi]['number']) for idi in anl_data ]
  cyCount = [cyNo.count(num) for num in cyNo]
  for i in range(len(cyCount)):
    if cyCount[i] >= 2:
      for idi in list(anl_data.keys()):
        if (atcf.basin2short(anl_data[idi]['basin'])+str(anl_data[idi]['number']) == cyNo[i]) and ('name' not in anl_data[idi]):
          print("Duplicated cyclone number:"+str(cyNo[i])+" id: "+str(idi)+" ignored  "+fname)
          del anl_data[idi]

  ## ID is a specific ID per storm per xml file. Don't save it but use it to find entries
  for idi in anl_data:
    storm = anl_data[idi]
    if storm['number'] >= 70:
      continue
    out_fname = atcf.filename(storm['basin'], storm['number'], storm['time'] )
    print(out_fname)
    fOut = open(out_fname, 'a')
    for fhr in range(0,144+6,6):
      try:
        data = cxml.get_forecasts( xml_root, "forecast", idi, -999, fhr)
        save_atcf(storm['basin'], storm['number'], storm['time'], data, fOut)
      except:
        pass
    for ensNo in range(0,51,1):
      for fhr in range(0,144+6,6):
        try:
          data = cxml.get_forecasts( xml_root, "ensembleForecast", idi, ensNo, fhr)
          save_atcf(storm['basin'], storm['number'],  storm['time'], data, fOut)
        except:
          pass
    fOut.close()
    ## This could be done in python but sort is easier.
    ## Make sure the columns are ordered by date, tech, fhr and are unique
    try:
     os.system("sort -u -k 3,3n -k 5,5 -k 6,6n "+out_fname+" -o "+out_fname)
    except:
     print("File may contain duplicates")


#  run the main code if called as a script
if __name__ == "__main__":
   try:
    # fname='test_data/z_tigge_c_ecmf_20140905120000_ifs_glob_prod_all_glo.xml'
    fname=sys.argv[1]
    print (fname)
    cxml2atcf(fname)
   except Exception:
     exc_info = sys.exc_info()
     traceback.print_exception(*exc_info)
     print("Pass filename to function")
