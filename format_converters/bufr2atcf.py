import bufrpy
from bufrpy.table import libbufr
import sys
sys.path.append("/home11/grad/2010/abrammer/python/tcdata_python/TropCy")
import atcf
import datetime
import codecs
import pandas as pd
import os
import matplotlib.path as mpltPath

BUFR_TABLES = ['/free4/abrammer/applications/libemos/share/libemos/tables/bufrtables/B0000000000000016000.TXT', '/free4/abrammer/applications/libemos/share/libemos/tables/bufrtables/D0000000000000016000.TXT']
SHORT_NAMES = {
    'TIME PERIOD OR DISPLACEMENT' : 'tau',
    'LATITUDE (COARSE ACCURACY)':'lat',
    'LONGITUDE (COARSE ACCURACY)':'lon',
    'PRESSURE REDUCED TO MEAN SEA LEVEL':'mslp',
    'WIND SPEED AT 10 M':'vmax'
    }

NAME_PREFIX = ['', '', 'vmax_', '','mslp_']
INTERP_KEYS = ['lat','lon','mslp','vmax']
BASIN_CODES = {
                'L' : 'al',
                'E' : 'ep',
                'W' : 'wp'
                }
# Ray tracing
def ray_tracing_method(x,y,poly):
    """
    Check whether location x,y is within polygon
    
    """
    n = len(poly)
    inside = False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
    return inside


def which_basin(subset):
    """"
    Check if point is within basin shaped polygons
    return short code when found
    """
    try:
        basin = BASIN_CODES[ subset['STORM IDENTIFIER'][0][2] ]
        return basin
    except KeyError:
        if( subset['STORM IDENTIFIER'][0][:2] < 70 ):
            basin = which_basin(subset.loc[ subset['lon'].notnull(), 'lon'][0],subset.loc[ subset['lon'].notnull(), 'lat'][0])
            return basin
        else:
            basin_lats =  [0,0,60,60, 20, 15,12,10,8.3,9.25,0]
            basin_lons =  [-72,-140,-140,-100,-100, -90,-85,-84,-81.5,-79,-72]
            basin = [[i, j] for i, j in zip(basin_lats,basin_lons)]
            path = mpltPath.Path( basin )
            if( path.contains_points( [[y,x]], radius=0.1 )):
                return "ep"
            basin_lats =  [0,0,60,60, 20, 15,12,10,8.3,9.25,0]
            basin_lons =  [-72,0,0,-100,-100, -90,-85,-84,-81.5,-79,-72]
            basin = [[i, j] for i, j in zip(basin_lats,basin_lons)]
            path = mpltPath.Path( basin )
            if( path.contains_points( [[y,x]], radius=0.1 )):
                return "al"
            basin_lats =  [0,60,60,0,0]
            basin_lons =  [180, 180, 220, 220, 180]
            basin = [[i, j] for i, j in zip(basin_lats,basin_lons)]
            path = mpltPath.Path( basin )
            if( path.contains_points( [[y,x]], radius=0.1 )):
                return "cp"
            basin_lats =  [0,60,60,0,0]
            basin_lons =  [180, 180, 100, 100, 180]
            basin = [[i, j] for i, j in zip(basin_lats,basin_lons)]
            path = mpltPath.Path( basin )
            if( path.contains_points( [[y,x]], radius=0.1 )):
                return "wp"
            basin_lats =  [0,60,60,0,0]
            basin_lons =  [40, 40, 100, 100, 40]
            basin = [[i, j] for i, j in zip(basin_lats,basin_lons)]
            path = mpltPath.Path( basin )
            if( path.contains_points( [[y,x]], radius=0.1 )):
                return "io"
            basin_lats =  [0,-60,-60,0,0]
            basin_lons =  [20, 20, 120, 120, 2]
            basin = [[i, j] for i, j in zip(basin_lats,basin_lons)]
            path = mpltPath.Path( basin )
            if( path.contains_points( [[y,x]], radius=0.1 )):
                return "io"
            return "un"
    
    
    
def to_tech(subset):
    if(subset["TYPE OF ENSEMBLE FORECAST"][0] == 0):
        return "ECMF"
    if(subset["TYPE OF ENSEMBLE FORECAST"][0] == 1):
        return "EE00"
    ens_number = int(subset["ENSEMBLE MEMBER NUMBER"][0])
    return f'EE{ens_number:02}'

def decode_time( time_data ):
    datum = {}
    prefix = 0
    for value in time_data:
        shortname = SHORT_NAMES.get(value.descriptor.significance)
        if( shortname is None ):
            shortname = value.descriptor.significance
        if(value.descriptor.significance == 'METEOROLOGICAL ATTRIBUTE SIGNIFICANCE'):
            try:
                prefix = value.value-1
            except TypeError:
                prefix = 3
            continue
        if(shortname in ['lat','lon']):
            shortname = f'{NAME_PREFIX[prefix]}{shortname}'
        datum[shortname] = value.value
    return datum

def bufr_to_data(msg):
    alldata = []
    for subset in msg.section4.subsets:
        data = []
        data.append(decode_time( subset.values[:-1] ))
        data[0]['date'] = datetime.datetime( data[0]["YEAR"], data[0]["MONTH"],data[0]["DAY"],data[0]["HOUR"] )
        data[0]['tau'] = 0
        for time in subset.values[-1]:
            data.append( decode_time(time) )
        df = pd.DataFrame(data)
        df.loc[ df['lon'] - min(df['lon'])>90 ]['lon'] = df['lon'] - 360.
        df[INTERP_KEYS] = df [ INTERP_KEYS].interpolate().where(df[INTERP_KEYS].bfill().notnull())
        df.loc[ (df['lon']<= -180),'lon'] = df['lon'] + 360.
        df.loc[ (df['lon'] > 180),'lon'] = df['lon'] - 360.
        alldata.append(df)
    return alldata

#//TODO Deal with output file name 

if __name__ == '__main__':
    table = libbufr.read_tables(codecs.open(BUFR_TABLES[0], 'rb', 'utf-8'), codecs.open(BUFR_TABLES[1], 'rb', 'utf-8'))
    bufr_fname = '/ct12/abrammer/graphics/ecmf_tc_data/data/A_JSXX01ECEP141200_C_ECMP_20170714120000_tropical_cyclone_track_FERNANDA_-118p3degW_11degN_bufr4.bin'
    bufr_out = 'test.dat' #bufr_fname.replace('.bin', '.dat')
    bufr_fname = sys.argv[1]
    print(f"Converting {bufr_fname}")
    msg = bufrpy.decode_file(open(bufr_fname, 'rb'), table)
    alldata = bufr_to_data(msg)
    
    with open(bufr_out, 'a') as fout:
        for subset in alldata:
            basin = which_basin(subset)
            for index,datum in subset.iterrows():
                    if( pd.notnull(datum.get_value('lon')) ):
                        fout.write( atcf.line_out(basin, int(subset['STORM IDENTIFIER'][0][:2]), 
                            subset['date'][0], 
                            to_tech(subset),
                            datum['tau'], datum['lat'], datum['lon'], datum['vmax']*1.94384, datum['mslp']/100., TY='XX')
                        )
    try:
        os.system("sort -u -k 3,3n -k 5,5 -k 6,6n "+bufr_out+" -o "+bufr_out)
    except:
        print("File may contain duplicates")


