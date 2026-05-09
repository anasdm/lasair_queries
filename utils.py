import numpy as np
import pandas as pd
import sncosmo
from astropy.table import Table
from astropy.time import Time
import sfdmap 
import json
import os
from astroquery.ipac.ned import Ned
import astropy.units as u
from astropy.coordinates import SkyCoord

sfdmap_dir = 'folder containing sfd_maps'
m = sfdmap.SFDMap(sfdmap_dir)
dust = sncosmo.CCM89Dust()
def lc_to_table(lcdict):
    now = Time.now().jd

    time, band, flux, fluxerr = [], [], [], []

    # 1. Only extract positive detections
    for i in lcdict['candidates']:
        if 'isdiffpos' in i and i['isdiffpos'] == 't':
            time.append(i['jd'])
            
            # Flux conversion
            f = 10**((25 - i['magpsf']) / 2.5)
            ferr = abs(np.log(10) / 2.5 * f * i['sigmapsf'])
            
            flux.append(f)
            fluxerr.append(ferr)
            
            # Filter ID to band string
            filter_map = {1: 'ztfg', 2: 'ztfr', 3: 'ztfi'}

            fid = i.get('fid')
            if fid in filter_map:
                band.append(filter_map[fid])
    
    # 2. Use the length of the new filtered list for constants
    n_points = len(time)
    
    if n_points == 0:
        raise ValueError("No positive detectionss found for this object.")

    zp = [25.0] * n_points
    zpsys = ['ab'] * n_points
    
    # 3. Create lightcurve df
    df = pd.DataFrame({
        'time': time,
        'band': band,
        'flux': flux,
        'fluxerr': fluxerr,
        'zp': zp,
        'zpsys': zpsys
    })
    
    return Table.from_pandas(df)


def get_ned_redshift(ra, dec):
    try:
        coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='icrs')
        result_table = Ned.query_region(coord, radius=30 * u.arcsec)

        if len(result_table) > 0:            
            valid_z = []
            for i, row in enumerate(result_table):
                z = row['Redshift']
                obj_type = row['Type']
                
                is_masked = np.ma.is_masked(z)
                
                if not is_masked and z is not None:
                    z_val = float(z)
                    if z_val > 0:
                        valid_z.append(z_val)
            
            if valid_z:
                return valid_z[0]

    except Exception as e:
        print(f"NED Error: {e}")
    
    return None

def fit_Ia(data,ra,dec):

    g_band_data = data[data['band'] == 'ztfg']
    
    if len(g_band_data) > 0:
        # Find the index of the maximum flux in g-band
        brightest_idx = np.argmax(g_band_data['flux'])
        t0_guess = g_band_data['time'][brightest_idx]
    else:
        # Fallback to brightest overall point if no g-band exists
        t0_guess = data['time'][np.argmax(data['flux'])]

    z_ned = get_ned_redshift(ra, dec)

    model = sncosmo.Model(source='salt2',effects=[dust], effect_names=['MW'], effect_frames=['obs'])
    model.set(MWebv=m.ebv(ra,dec)) # calculate extinction at coordinates
    fit_params = ['z', 't0', 'x0', 'x1', 'c']

    if z_ned:
  
        bounds = {'z':(z_ned-0.0001, z_ned+0.0001),'t0':(t0_guess-3, t0_guess+3),'x1': (-3, 3), 'c': (-1, 1)} #standard SN Ia values
    else:
        
        bounds = {'z': (0.001, 0.2),'t0':(t0_guess-3, t0_guess+3), 'x1': (-3, 3), 'c': (-1, 1)}

    result, fitted_model = sncosmo.fit_lc(data, model,
                                      fit_params,bounds=bounds) 
    return result, fitted_model

DATA_FOLDER = "outputs"
NOTES_PATH = DATA_FOLDER + "/notes.json"

def get_saved_notes():
    """Loads the entire dictionary of notes from the JSON file."""
    if os.path.exists(NOTES_PATH):
        with open(NOTES_PATH, "r") as f:
            return json.load(f)
    return {}

def save_note_to_file(obj_id, text):
    """Updates the JSON file with a new note for a specific ID."""
    notes = get_saved_notes()
    notes[obj_id] = text
    with open(NOTES_PATH, "w") as f:
        json.dump(notes, f, indent=4)
