import numpy as np
import atcf

def calculate_ellipse(data)
    date_array = data['datetime'].unique()
    for date in date_array:
      tau_array = data[ data['datetime']==date ]['tau'].unique()
      for tau in tau_array:
        sub_data = data[ (data['datetime']==date) & (data['tau'] == tau) ]
        mean_locs = data.groupby(['datetime','tau'])['lat','lon'] - data.groupby(['datetime','tau'])['lat','lon'].mean()        
        Pb = []
        Pb[0] = sum( (sub_data['lon'] - mean_lons)**2)
        Pb[1] = sum( (sub_data['lat'] - mean_lats)**2)
        Pb[2] = sum( (sub_data['lat'] - mean_lats) * (sub_data['lon'] - mean_lons) )


for name, group in data.groupby(['datetime','tau']):
  mean_locs = group[ ['lat', 'lon'] ].mean()
  anom_locs = group[ ['lat', 'lon'] ] - mean_locs
  Pb = []
  Pb.append(  sum( anom_locs['lon']**2 )  )
  Pb.append(  sum( anom_locs['lat']**2 )  )
  Pb.append(  sum( anom_locs['lon'] * anom_locs['lat'] )  )
  print( Pb[0] == 0 or Pb[1] == 0)
  Pb[:] = [x / len(anom_locs) for x in Pb]
  rho = Pb[2] / np.sqrt( Pb[1]) *  np.sqrt(Pb[0])   
  
# Pb= new( (/2,2/), float)
# Pb(:,:) = 0.0
# 
# Pb(0,0) = dim_sum( (x(:)-mx) * (x(:)-mx) )  ; Pb[0]
# Pb(1,1) = dim_sum( (y(:)-my) * (y(:)-my) )  ; Pb[1]
# Pb(1,0) = dim_sum( (y(:)-my) * (x(:)-mx) )  ; Pb[2]

Pb(0,1) = Pb(1,0)

if( Pb(0,0) .eq.0 .or. Pb(1,1) .eq. 0)
  continue
end if
Pb(:,:) = Pb(:,:) / int2flt(num(.not.ismissing(y))-1)
rho     = Pb(1,0) / (sqrt(Pb(0,0)) * sqrt(Pb(1,1)))
sigmax  = sqrt(Pb(0,0))
sigmay  = sqrt(Pb(1,1))
fac     = 1.0 / (2.0 * (1 - rho * rho))








if __name__ == '__main__':
  fname ="~/data/nhc_tracks/aid/aal042015.dat.gz"
  data = atcf.read_adeck(fname)
