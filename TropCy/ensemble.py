import numpy as np
import pandas as pd

def calculate_ellipse(group, min_no=0):
    if(len(group) < min_no):
        return
    sigm_locs = group[ ['lat', 'lon'] ].std()**2
    if( any( sigm_locs <=  0.01 )):
        return
    rho = group['lat'].cov( group['lon'] )
    try:
        eig_val, eig_vec = np.linalg.eig( [ [sigm_locs['lat'], rho],[rho, sigm_locs['lon']]] )
        eig_val = np.sqrt( abs(eig_val) )
        srt = np.argsort(eig_val)[::-1]
        angls = 180-np.degrees( np.arctan2( eig_vec[srt,0], eig_vec[srt,1]))
        retval = pd.Series( { 'ell_major' : eig_val[srt[0]] ,    \
                              'ell_minor' : eig_val[srt[1]],  \
                              'ell_angle' : angls[0]          })
        return retval
    except Exception as e:
        print( mean_locs, sigm_locs, rho )
        print("======")
        return 

def haversine_distance_angle( lat1, lon1, lat2, lon2):
    R = 6371. # Earths Circumferences  [km]
    rlat1 = np.radians( lat1 )
    rlon1 = np.radians( lon1 )
    rlat2 = np.radians( lat2 )
    rlon2 = np.radians( lon2 )
    d = np.arccos( np.sin(rlat1)*np.sin(rlat2) + np.cos(rlat1)*np.cos(rlat2)*np.cos(rlon2-rlon1) ) * R
    brng = np.degrees( np.arctan2(np.cos(rlat1)*np.sin(rlat2)- \
                      np.sin(rlat1)*np.cos(rlat2)*np.cos(rlon2-rlon1), \
                                np.sin(rlon2-rlon1)*np.cos(rlat2)) )
    return d, brng


def absolute_track_spread(data):
    d, brng = haversine_distance_angle(  data['lat'],  data['lon'],  data['lat'].mean(), data['lon'].mean()  )
    data['ats_dist'] = d
    data['ats_angl'] = brng
    return data



# def along_across_error(data):
#     lat2 = np.radians( data['lat'].mean() )
#     lon2 = np.radians( data['lon'].mean() )
#     d, brng = [ haversine_distance_angle()]
#     data['ats'] = d
#     return data



