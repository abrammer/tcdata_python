import sys
sys.path.append("/home11/grad/2010/abrammer/python/tcdata_python")
from TropCy import atcf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob
import time
import seaborn as sns

def haversine( lat1,lon1,lat2, lon2 ):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    -- This is duplicated in ensemble.py 
    -- TODO// Simplify and remove
    """
    # convert decimal degrees to radians 
    lon1, lat1 = map(np.radians, [lon1, lat1] )
    lon2, lat2 = map(np.radians, [lon2, lat2] )
    # haversine formula 
    dlon = np.subtract(lon1,lon2) 
    dlat = np.subtract(lat1,lat2) 
    a = (np.sin(dlat/2)**2  + 
        np.multiply( (np.cos(lat1)* np.sin(dlon/2)**2), np.cos(lat2) ) )
    c = 2 * np.arcsin(np.sqrt(a)) 
    km = 6371 * c
    return km



def initial_final_error(group):
	if any(group['tau']==120) & any(group['tau']==12):
		x =  group[ (group['tau']==120) ]['track_error']
		x.name = 'final_error'
		y =  group[ (group['tau']==12)  ]['track_error']
		return [x,y]
	 


if __name__ == '__main__':
	ftime, btime,f_time = 0,0,0
	start = time.process_time()
	files = glob.glob("/home11/grad/2010/abrammer/data/nhc_tracks/cxml/aal[0-2][0-9]201[6].dat")
	for k,f in enumerate(files):
		storm = f.split('/')[-1][1:9]
	
		fstart = time.process_time()
		forecast_data = atcf.read_adeck(f)
		ftime = ftime + (time.process_time() - fstart)
   
		EEMN = forecast_data.loc[ forecast_data['tech']!="ECMF" ].groupby(['datetime', 'tau', 'validtime']).mean()
		EEMN['tech']= "EEMN"
		EEMN = EEMN.reset_index()
		forecast_data = forecast_data.append(EEMN)
	
		fstart = time.process_time()
		adeck = f"/home11/grad/2010/abrammer/data/nhc_tracks/aid/a{storm}.dat.gz"
		forecast_data = forecast_data.append( atcf.read_adeck( adeck, tech=[ 'OFCL','AVNO','CMC','HWRF','AEMN']+[f'AP{i:>02}' for i in range(0,21,1)]), ignore_index=True)
		f_time = f_time + (time.process_time() - fstart)
	
		bstart = time.process_time()
		bdeck = f"/home11/grad/2010/abrammer/data/nhc_tracks/btk/b{storm}.dat.gz"
		verif_data = atcf.read_adeck(bdeck)
		verif_data = verif_data[ ['datetime', 'tech', 'tau','lat', 'lon', 'vmax', 'mslp', 'validtime'] ].drop_duplicates()
		btime = btime + (time.process_time() - bstart)
	
		forecast_data = forecast_data.merge(verif_data, on='validtime', suffixes=('','_btrk'))
	
		if(k==0):
			outdata = forecast_data
		else:
			outdata = outdata.append( forecast_data, ignore_index=True)
		print(storm, len(outdata) )

	outdata['track_error'] = haversine( outdata['lat'], outdata['lon'], outdata['lat_btrk'], outdata['lon_btrk'])
	outdata['mslp_error'] = outdata['mslp'] - outdata['mslp_btrk']
	outdata['vmax_error'] = outdata['vmax'] - outdata['vmax_btrk']

	end = time.process_time()
	print(end- start)

	EC_ens_techs = [ "EE"+str(i).zfill(2) for i in range(0,51)]
	AP_ens_techs = [ "AP"+str(i).zfill(2) for i in range(0,21)]
	label_techs = [ 'OFCL','ECMF','EEMN','EExx','AVNO','APxx','HWRF']


	print(ftime, btime)
	ens_data = outdata[ (outdata['tech'].isin(AP_ens_techs)|outdata['tech'].isin(EC_ens_techs)) ].groupby(['datetime','tech','basin','number'])
	xy = pd.DataFrame(columns=["initial_error", "final_error"])

	for name,group in ens_data:
		if any(group['tau']==120) & any(group['tau']==12):
			x =  group.loc[ (group['tau']==120) ]['track_error']
			y =  group.loc[ (group['tau']==12)  ]['track_error']
			xy.loc[-1] = [x.values[0],y.values[0]]
			xy.index = xy.index+1
		
	fig,(ax)=plt.subplots(1,1,figsize=(15.5,8.5))
	sns.jointplot(y="final_error", x="initial_error",kind="hex", data=xy)
	# sns.despine(offset=10, trim=True)
	ax.set_ylim(0,200);
	# ax.set_yticks(np.arange(0,600,100))
	# ax.set_ylabel('Distance [km]');
	# ax.set_xlabel('Forecast hour');
	# ax.set_title('Mean Absolute Position Error')
	# plt.legend(frameon=1, loc=2, title="Tech")
	plt.show()








	outdata['tech'] = outdata['tech'].replace( AP_ens_techs, "APxx" )
	outdata['tech'] = outdata['tech'].replace( EC_ens_techs, "EExx" )



	fig,(ax)=plt.subplots(1,1,figsize=(15.5,8.5))
	data = outdata[ (outdata['tech'].isin(label_techs)) & ( outdata['tau']%24 == 0) & ( outdata['tau'] <= 120)   ]
	sns.barplot(y='track_error', x="tau",hue="tech", data=data, ax=ax, hue_order=label_techs)
	sns.despine(offset=10, trim=True)
	ax.set_ylim(0,600);
	ax.set_yticks(np.arange(0,600,100))
	ax.set_ylabel('Distance [km]');
	ax.set_xlabel('Forecast hour');
	ax.set_title('Mean Absolute Position Error')
	plt.legend(frameon=1, loc=2, title="Tech")
	plt.show()








	data = outdata[ (outdata['tech'].isin(label_techs)) & ( outdata['tau'] == 120)   ]
	fig,(ax)=plt.subplots(1,1,figsize=(15.5,8.5))
	sns.pointplot(y='track_error', x="year",hue="tech", dodge=0.1,data=data, ax=ax, hue_order=label_techs)
	sns.despine(offset=10, trim=True)
	ax.set_ylim(0,850);
	ax.set_yticks(np.arange(0,850,100))
	ax.set_ylabel('Distance [km]');
	ax.set_xlabel('Forecast hour');
	ax.set_title('Mean Absolute Position Error by Year | fhr:120')
	plt.legend(frameon=1, loc=2, title="Tech")
	plt.show()


	fig,(ax)=plt.subplots(1,1,figsize=(15.5,8.5))
	data = outdata[ (outdata['tech'].isin(label_techs)) & ( outdata['tau']%24 == 0) & ( outdata['tau'] <= 120)   ]
	sns.boxplot(y='track_error', x="tau",hue="tech", data=data, ax=ax, hue_order=label_techs, notch=True, fliersize=0)
	sns.despine(offset=10, trim=True)
	ax.set_ylim(0,1000);
	ax.set_yticks(np.arange(0,1000,100))
	ax.set_ylabel('Distance [km]');
	ax.set_xlabel('Forecast hour');
	ax.set_title('Absolute Position Error')
	plt.legend(frameon=1, loc=2, title="Tech")
	plt.show()

	fig,(ax)=plt.subplots(1,1,figsize=(15.5,8.5))
	data = outdata[ (outdata['tech'].isin(label_techs)) & ( outdata['tau']%24 == 0) & ( outdata['tau'] <= 120)   ]
	sns.boxplot(y='mslp_error', x="tau",hue="tech", data=data, ax=ax, hue_order=label_techs, notch=True, fliersize=0)
	sns.despine(offset=10, trim=True)
	ax.set_ylim(-40,40);
	ax.set_yticks(np.arange(-40,40,10))
	ax.set_ylabel('Pressure [hPa]');
	ax.set_xlabel('Forecast hour');
	ax.set_title('Pressure Error')
	plt.legend(frameon=1, loc=2, title="Tech")
	plt.show()


	fig,(ax)=plt.subplots(1,1,figsize=(15.5,8.5))
	data = outdata[ (outdata['tech'].isin(label_techs)) & ( outdata['tau']%24 == 0) & ( outdata['tau'] <= 120)   ]
	sns.boxplot(y='vmax_error', x="tau",hue="tech", data=data, ax=ax, hue_order=label_techs, notch=True, fliersize=0)
	sns.despine(offset=10, trim=True)
	ax.set_ylim(-30,30);
	ax.set_yticks(np.arange(-30,30,5))
	ax.set_ylabel('Wind Speed [m/s]');
	ax.set_xlabel('Forecast hour');
	ax.set_title('V-Max Error')
	plt.legend(frameon=1, loc=2, title="Tech")
	plt.show()
