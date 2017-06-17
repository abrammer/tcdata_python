"""Simple functions to currently aid in reading/writing ATCF format files"""
#ATCF read / Write Module
# pylint: disable=W0311, C0326, C0103
import pandas as pd

def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text

def str2ll(x):
    """Convert atcf str to latlon -- internal single value only"""
    converters = {'N':1,'S':-1,'W':-1,'E':1}
    ret = (int(x[:-1])*converters[x[-1]]) / 10
    return ret

def lat(x):
  """Convert numeric lat to atcf lat string"""
  if x > 0.0:
    latstr = '%3.0i' % int(round(x*10.0)) + "N"
  else:
    latstr = '%3.0i' % int(round(-x*10.0)) + "S"
  return latstr

def lon(x):
  """Convert numeric lon to atcf lon string"""
  if x > 0.0:
    latstr = '%4.0i' % int(round(x*10.0)) + "E"
  else:
    latstr = '%4.0i' % int(round(-x*10.0)) + "W"
  return latstr

def basin2short(longname):
    """convert long basin name to short acronym"""
    dictionary =  {   "North Atlantic" : "al",\
                    "Northeast Pacific" : "ep",\
                      "Central Pacific" : "cp",\
                    "Northwest Pacific" : "wp",\
                         "North Indian" : "io",\
                     "Southwest Indian" : "sh",\
                     "Southeast Indian" : "sh",\
                    "Southwest Pacific" : "sh"  }
    try:
      return dictionary[longname]
    except KeyError:
      return longname

def basin2long(shortname):
    """convert short basin acronym to long name"""
    dictionary =  { "al":  "North Atlantic" ,\
                         "ep": "Northeast Pacific",\
                         "cp":   "Central Pacific",\
                         "wp": "Northwest Pacific",\
                         "io":      "North Indian",\
                         "sh":  "Southwest Hemisphere" }
    try:
      return dictionary[shortname]
    except KeyError:
      return shortname


def line_out( basin, cyNo, rdate, tech, tau, inlat, inlon, vmax, mslp, TY='XX' ):
    """Format data int atcf string style
    TODO: update this to fstring so it's more readable"""
    basin = basin2short(basin)
    outline = ("{basin}, {cyNo:02}, "
               "{time.year:04.0f}{time.month:02.0f}{time.day:02.0f}{time.hour:02.0f}, "
               "03, {tech}, {tau:3.0f}, {lat}, {lon}, {vmax:3.0f}, {mslp:4.0f}, {ty:>2}\n")
    string =  outline.format(basin=basin.upper(), cyNo=cyNo, time=rdate, tech=tech,tau=tau,
                             lat=lat(inlat), lon=lon(inlon), vmax=vmax, mslp=mslp, ty=TY )
    return  string

def filename(basin, storm, date):
    """Create atcf filename from basin (str), storm number (int) and date (datetime)"""
    string = "a{bb}{nn:02.0f}{time.year:04.0f}.dat"
    fmt_string = string.format(bb=basin2short(basin),nn=storm,time=date )
    return fmt_string

# def read_all_and_correct_vmax(filename):
#   from numpy import genfromtxt
#   import csv
#   datum = genfromtxt('cxml/'+filename, delimiter=',', dtype=str)

#   for data in datum:
#     vmax = int(data[8])*1.94384
#     data[8] = "{vmax:4.0f}".format(vmax=vmax)

#   fw = open('adeck/'+filename, 'w')
#   cw = csv.writer(fw, delimiter=',')
#   cw.writerows(datum)

def read_storm_names(fname):
  """Read storm names master list into pandas dataframe"""
  atcfNames = ["name","basin","basin_code","bc2","bc3","bc4","bc5","number","year","type","trackshape",
  "startdate", "enddate","size","gen_num", "par1","par2","priority","state", "wt_numer","id"]
  datum = pd.read_csv(fname, sep=' *, *', names=atcfNames, engine='python', index_col=False,usecols=range(len(atcfNames)) )
  return datum[ ['name', 'basin', 'number','year', 'type', 'startdate', 'enddate','id'] ]
  

def read_adeck(fname, tech=None):
  """Read adeck from filename into pandas dataframe"""
  ## Tried versions of parsing colums in the read_csv func and they were much slower
  atcfNames = ["basin","number","datetime","tnum","tech","tau","lat","lon","vmax","mslp","type","rad","windcode","rad1",
            "rad2","rad3","rad4","pouter","router","rmw","gusts","eye","subregion"]
  converters = {   'lat' : str2ll,
                   'lon' : str2ll}
  # n.b. ' *, *' takes care of stripping whitespace
  #  python engine allows for providing too many column names
  #  datetime as converter is super slow, str2ll is neglible time addition
  datum = pd.read_csv(fname, sep=' *, *',engine='python', index_col=False,
     usecols=range(len(atcfNames)),
     names=atcfNames,
     converters=converters )
  #  Quicker to process dates in series after than as a converter
  datum['datetime'] = pd.to_datetime(datum['datetime'], format="%Y%m%d%H")
  datum['validtime'] =  datum['datetime']  + pd.to_timedelta(datum['tau'], unit="h")
  datum = datum.loc[ (datum['lat']!=0) | (datum['lon']!=0) ]
  if tech is None:
    return datum
  else:
    return datum.loc[ datum['tech'].isin(tech) ]
    

    
if __name__ == '__main__':
  fname = "~/Desktop/tigge_cxml/adeck/aal022011.dat"
  data = read_adeck(fname)
  # for k,datum in data.iterrows():
  #   print( line_out( datum['basin'], datum['number'], datum['datetime'], datum['tech'], datum['tau'], datum['lat'], datum['lon'], datum['vmax'], datum['mslp']) )
