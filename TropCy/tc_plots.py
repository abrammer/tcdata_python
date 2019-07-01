from TropCy import ensemble
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def add_track_lines(data):
    data.groupby( [ 'tech','number','datetime'] ).apply(
         lambda x: 
           plt.plot(x['lon'], x['lat'],                  
                    c='grey',         # marker colour
                    linestyle='-.',            # marker size
                    transform=ccrs.PlateCarree(),
           )
         )

def add_track_times(data):
    data.groupby( [ 'tech','number','datetime', 'tau'] ).apply(
         lambda x: 
                plt.text( x['lon'], x['lat'], f'{x["tau"].get_values()[0]}',
                    transform=ccrs.PlateCarree(),
                    fontsize=5,
           )
         )

def add_ellipse( x ,fig):
    ell = ensemble.calculate_ellipse(x,min_no=20)
    if(ell is None): return
    fig.add_artist( 
        Ellipse( 
        xy=( x['lon'].mean(), x['lat'].mean() ),
        width=ell['ell_major']*2.,
        height=ell['ell_minor']*2.,
        angle=ell['ell_angle'],
        edgecolor='blue',
        facecolor='none',
        linewidth=3,
        alpha=0.2,
        zorder=10)
    )
    fig.text( x['lon'].mean(), x['lat'].mean(), f'{x["tau"].get_values()[0]}',
                    transform=ccrs.PlateCarree(),
                    fontsize=12,
                    color='blue'
           )



def add_ellipses(data, fig):
    data.groupby( ['number','datetime', 'tau'] ).apply( 
        lambda x: add_ellipse(x,fig) )



def background_map(data):
    land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                        edgecolor='face',
                                        facecolor=cfeature.COLORS['land'])
    ocean_50m = cfeature.NaturalEarthFeature('physical', 'ocean', '50m',
                                        edgecolor='face',
                                        facecolor=cfeature.COLORS['water'])
    width = 15
    height = 15
    fig = plt.figure(figsize=(width, height));
    ax = plt.axes(projection=ccrs.PlateCarree());
    ax.set_extent( ( min(data['lon'])-5,  max(data['lon'])+5, 
                     min(data['lat'])-5,  max(data['lat'])+5 ),
                    ccrs.PlateCarree() )
    ax.add_feature(land_50m)
    ax.add_feature(ocean_50m)
    ax.coastlines(resolution='50m')
    ax.add_feature(cfeature.BORDERS, edgecolor='grey')
    ax.gridlines()
    id = data.iloc[0]['number']
    date= data.iloc[0]['datetime'].to_pydatetime()
    title = f'al{id}{date:%Y} Initilisation date: {date:%m/%d %H:%M}UTC'
    ax.set_title( title )
    return ax


def plot_points(data):
    fig = background_map(data);
    data.groupby( [ 'tech','number','datetime'] ).apply( add_track_lines );
    data[ data['tau']%24 ==0 ].groupby( [ 'tech','number','datetime'] ).apply( add_track_times )
    data[ data['tau']%24 ==0 ].groupby( [ 'number','datetime'] ).apply(lambda x: add_ellipses(x,fig) )
    return plt

