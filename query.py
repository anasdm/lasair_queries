import settings
from lasair import LasairError, lasair_client as lasair
import pandas as pd
import os

DATA_FOLDER = "outputs"

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

def query(watchlistID=None):

    selected = """
    objects.objectId, 
    objects.ramean, 
    objects.decmean, 
    objects.jdmin - 2400000.5 AS mjdmin, 
    objects.jdmax - 2400000.5 AS mjdmax, 
    objects.magrmin, 
    objects.rmag, 
    sherlock_classifications.classification
    """

    tables = "objects, sherlock_classifications"
    conditions = "objects.objectId = sherlock_classifications.objectId"

    # Add Watchlist if an ID is provided
    if watchlistID is not None:
        selected += """, 
        watchlist_hits.name,
        watchlist_hits.arcsec"""
        
        tables += f", watchlist:{watchlistID}"
        
        conditions += f" AND objects.objectId = watchlist_hits.objectId"
        conditions += f" AND watchlist_hits.wl_id = {watchlistID}"

    conditions += """
    AND objects.jdmax > JDNOW() - 14.00000 
    AND objects.ncand > 3 
    AND objects.gmag < 21 
    AND objects.rmag > 14 
    AND objects.ncandgp > 1 
    AND sherlock_classifications.classification = "SN"
    AND ABS(objects.glatmean) > 15  
    AND (objects.dmdt_g > 0 OR objects.dmdt_r > 0) 

    """

    L = lasair(settings.API_TOKEN, endpoint="https://lasair-ztf.lsst.ac.uk/api")
    
    try:
        results = L.query(selected, tables, conditions + " ORDER BY mjdmin DESC", limit=5) # set a small limit as an example
        return results
    except LasairError as e:
        print(f"Error: {e}")

def save_results(results, filename="candidates.csv"):
    if not results:
        print("No results found to save.")
        return
    
    df = pd.DataFrame(results)

    file_path = os.path.join(DATA_FOLDER, filename)
    
    # Check if file exists to merge with old data
    if os.path.exists(file_path):
        old_df = pd.read_csv(file_path)
   
        combined_df = pd.concat([old_df, df], ignore_index=True)
    else:
        combined_df = df
    
    # Remove duplicates based on objectId
    # 'last' keeps the most recent detection info if the same ID appears twice
    total_before = len(combined_df)
    combined_df.drop_duplicates(subset=['objectId'], keep='last', inplace=True)
    total_after = len(combined_df)
    
    combined_df.to_csv(file_path, index=False)
    
    new_added = total_after - (total_before - len(df))
    print(f"File updated. Added {new_added} new unique candidates. Total candidates: {total_after}")


query_results = query()
save_results(query_results, "supernova_candidates.csv")
