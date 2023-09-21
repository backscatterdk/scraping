"""
Script for converting a txt file of search queries into a df with Instagram location ID's.
"""
import instaloader
import os
import pandas as pd
from tqdm import tqdm

# input username
L = instaloader.Instaloader()
USER=""
L.load_session_from_file(USER)

# n search results to obtain per search 
n = 20

def main():
    
    # read search terms
    with open(os.getcwd()+"/search_terms.txt", "r") as f:
        search_terms = f.read().splitlines()

    terms = []
    topresult = []
    locids = []
    locnnames = []
    slugnnames = []
    long =[]
    lat = []

    for loc in tqdm(search_terms):
        suggestions = instaloader.TopSearchResults(L.context, loc).get_locations()
        for i in range(0,n):    
            try:
                topresult.append(str(i))
                terms.append(loc)
                location = next(suggestions)
                locids.append(str(location.id))
                locnnames.append(str(location.name))
                slugnnames.append(str(location.slug))
                long.append(str(location.lng))
                lat.append(str(location.lat))
            except StopIteration:
                locids.append("NA")
                locnnames.append("NA")
                slugnnames.append("NA")
                long.append("NA")
                lat.append("NA")

    data = {"search_terms": terms,
            "search_resul_n": topresult,
            "locnames": locnnames,
            "locids": locids,
            "slugnamªes": slugnnames,
            "long": long,
            "lat": lat}
    
    df = pd.DataFrame(data)
    final = df[df['locnames']!="NA"].copy(True)

    final.to_excel(os.getcwd()+"/locationsIDs.xlsx")
    final.to_csv(os.getcwd()+"/locationsIDs.csv")

if __name__:
    main()
