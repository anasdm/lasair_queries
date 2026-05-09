# lasair_queries

This tool is designed to identify SNe within the live alert stream of ZTF. It combines SQL querying, light curve fitting and host galaxy information to identify type Ia supernovae.

## Features
* _Real-time Stream Querying:_ Interfaces with the Lasair broker to pull recent transients directly from the ZTF alert stream. Identifies for SNe in their brightening phase within the ZTF data, while filtering for Galactic coordinates to minimise Milky Way dust extinction and requiring a minimum number of detections to eliminate artifacts, asteroids, and bad subtractions. It also supports Lasair watchlists for focusing on specific sky regions or host galaxies (more information on watchlists [here](https://lasair.readthedocs.io/en/develop/core_functions/watchlists.html)).
* _Redshift Validation:_ Cross-matches candidates with the [NASA/IPAC Extragalactic Database (NED)](https://ned.ipac.caltech.edu/) to retrieve spectroscopic host redshifts when available, improving fit accuracy.
* _SALT2 Light Curve Fitting:_ Includes sncosmo to fit Type Ia templates. Can be swapped with alternative SN models.
* _Interactive Dashboard:_ A Streamlit-based viewer to visualise light curves, inspect host galaxy context via Legacy Survey cutouts, and record notes on a separate JSON file.

## Getting started
1.  **Clone the repository:** 
```
git clone [https://github.com/anasdm/lasair_queries.git](https://github.com/anasdm/lasair_queries.git)
cd lasair_queries
```
If you simply want to access the viewer using the sample data in the `outputs` folder, skip to step 5

2.  **Configure API Access:**

Ensure you have a settings.py file with your API_TOKEN from the Lasair-ZTF platform. (Instructions [here](https://lasair.readthedocs.io/en/develop/core_functions/rest-api.html#get-your-token).)

3. **Download SFD maps:**
   
These are used for the dust calculation in the fitting. You can find them [here](https://github.com/kbarbary/sfddata). Don't forget to add the path to these in `utils.py` 

4. **Run the pipeline:**

   3.1 Run the query script  `query.py` 
    
   3.2 Fit a light curve model using  `lc_fits.py`

5. **Open the streamlit viewer:**
```
streamlit run viewer.py
```

## Contact
If you want to chat about any things supernovae, science outreach or else, I would love to hear from you!
