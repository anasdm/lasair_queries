import pickle
import pandas as pd
import settings
from lasair import lasair_client as lasair
from utils import lc_to_table, fit_Ia

def run_background_processing(csv_path="outputs/supernova_candidates.csv"):
    # 1. Initialise Lasair
    try:
        L = lasair(settings.API_TOKEN, endpoint="https://lasair-ztf.lsst.ac.uk/api")
        print("✅ Lasair client working.")
    except Exception as e:
        return

    # 2. Load CSV
    try:
        df = pd.read_csv(csv_path)
        results = df.to_dict('records')
        print(f"Loaded {len(results)} candidates from {csv_path}.")
    except FileNotFoundError:
        print(f"Error: {csv_path} not found.")
        return

    processed_output = {}

    for row in results:
        obj_id = row['objectId']
        
        try:
            # 3. Fetch LC
            response = L.objects([obj_id]) 
            if not response or 'candidates' not in response[0]:
                continue
            
            tab = lc_to_table(response[0])

            # 4. Perform Ia fit
            result, fitted_model = fit_Ia(tab, row['ramean'], row['decmean'])
            
            # 5. Calculate Absolute Mag
            try:
                peak_mag = fitted_model.source_peakabsmag('bessellb', 'ab')
            except:
                peak_mag = None

            # 6. Store
            processed_output[obj_id] = {
                'metadata': row,
                'lc_table': tab.to_pandas(),
                'fit_params': {
                    'z': result.parameters[0],
                    'chi2': result.chisq,
                    't0': result.parameters[1],
                    'x1':result.parameters[3],
		    'c':result.parameters[4],
                    'abs_mag': peak_mag 
                },
                'model_params': dict(zip(fitted_model.param_names, fitted_model.parameters))
}
            print(f"Successfully ran the fit for {obj_id}")

        except Exception as e:
            print(f"Error during processing for {obj_id}: {str(e)}")
            continue

    # 7. Save
    if processed_output:
        with open('outputs/processed_data.pkl', 'wb') as f:
            pickle.dump(processed_output, f)
        print(f"\nSaved {len(processed_output)} objects to processed_data.pkl")
    else:
        print("\nEmpty output. No data was saved.")

if __name__ == "__main__":
    run_background_processing()
