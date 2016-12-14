import xml.etree.ElementTree as ET
from datetime import datetime
# pylint: disable=W0311, C0326, C0103, C0301

### run code as:
#   python cxml_decode.py z_tigge_c_ecmf_20140912000000_ifs_glob_prod_all_glo.xml

def parse_variable(datum, variable):
  """Find relevant forecast element, pull out values and return data"""
  if variable == "latitude":
    try:
      tmpvar = float(datum.find('latitude').text)
      if datum.find('latitude').attrib['units'] == 'deg S':
        tmpvar = -tmpvar
    except AttributeError:
      tmpvar = float(datum.find('fix/latitude').text)
      if datum.find('fix/latitude').attrib['units'] == 'deg S':
        tmpvar = -tmpvar
    except:
      tmpvar = -999.
    finally:
      return tmpvar
  if variable == "longitude":
    try:
      tmpvar = float(datum.find('longitude').text)
      if datum.find('longitude').attrib['units'] == 'deg W':
        tmpvar = -tmpvar
    except AttributeError:
      tmpvar = float(datum.find('fix/longitude').text)
      if datum.find('fix/longitude').attrib['units'] == 'deg W':
        tmpvar = -tmpvar
    except:
      tmpvar = -999.
    finally:
      return tmpvar
  if variable == "time":
    dformat = '%Y-%m-%dT%H:%M:%SZ'
    try:
      tmpvar = datetime.strptime(datum.find('validTime').text, dformat)
    except AttributeError:
      tmpvar = datetime.strptime(datum.find('fix/validTime').text, dformat)
    except:
      tmpvar = ""
    finally:
      return tmpvar
  if variable == "fhr":
    return int(datum.attrib['hour'])
  if variable == "mslp":
    try:
      mslp = float(datum.find('cycloneData/minimumPressure/pressure').text)
    except:
      mslp = -999.
    return mslp
  if variable == "mwnd":
    try:
      mwnd = float(datum.find('cycloneData/maximumWind/speed').text)
      mwnd = mwnd*1.9438
    except:
      mwnd = -999.
    return mwnd
  print("variable pass to parse_variable not recognised")


def get_forecasts(xml_root, type, cycloneID,  ensNo, fhr):
  """Get Forecast entries for specifc storm, time, fhr"""
  retdata = {}
  if type == "ensembleForecast":
   tech = "EE%02.0f"%ensNo
   data = xml_root.findall("./data[@type='"+type+"'][@member='"+str(ensNo)+"']/disturbance[@ID='"+cycloneID+"']/fix[@hour='"+str(fhr)+"']")
  else:
   tech = "ECMF"
   data = xml_root.findall("./data[@type='"+type+"']/disturbance[@ID='"+cycloneID+"']/fix[@hour='"+str(fhr)+"']")
  for datum in data:
    retdata['lat'] = parse_variable(datum, 'latitude')
    retdata['lon'] = parse_variable(datum, 'longitude')
    retdata['time'] = parse_variable(datum, 'time')
    retdata['fhr'] = parse_variable(datum, 'fhr')
    retdata['mslp'] = parse_variable(datum, 'mslp')
    retdata['vmax'] = parse_variable(datum, 'mwnd')
    retdata['tech'] = tech
  if('lat' not in retdata or retdata['lat'] == retdata['lon'] == retdata['mslp'] == 0):
    raise Exception("No forecast data found")
  else:
    return retdata

## Find relevant analysis info, pull out values and return data
def get_analysis(xml_root):
  """Pull out disturbance analysis info from xml file"""
  data = xml_root.findall("./data[@type='analysis']/disturbance")
  retdata = {}
  for datum in data:
    id = datum.attrib['ID']
    retdata[id] = {}
    try:
      retdata[id]['name'] = datum.find('cycloneName').text
    except:
      pass
    try:
      retdata[id]['number'] = int(datum.find('cycloneNumber').text )
      retdata[id]['basin']  = datum.find('basin').text
      retdata[id]['lat']    = parse_variable(datum, 'latitude')
      retdata[id]['lon']    = parse_variable(datum, 'longitude')
      retdata[id]['time']   = parse_variable(datum, 'time')
    except:
      del retdata[id]
  return retdata


###  Beginning of an output function. Currently just dump to std out
def print_output(time, idno, name, basin, data):
    print (idno, data)

