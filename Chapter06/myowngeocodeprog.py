from csv import DictReader, DictWriter
from time import sleep

import requests
from tqdm import tqdm

''' This program is me rewriting chapter 06. Four functions needed 
1. function to process search in nominatim 
2. funciton to read from csv
3. function to write to a csv
4. function to bulk call nominatim  but each time, 
show the latitude, longitude and then store, 


'''
base_url = 'https://nominatim.openstreetmap.org/search?'

def nominatim_geocode(name, format="json", addressdetails=1, limit=1, **kwargs):
    ''' this is a function that wraps API to nominatim'''
    params = {"q": name, "format": format, "addressdetails": addressdetails, "limit": limit, **kwargs}
    headers = {"Accept-Language": "en"}
    response = requests.get(base_url, params=params, headers=headers)
    response.raise_for_status()

    sleep(1)
    return response.json()

def read_file(path):
    ''' read csv file and return dictionary'''
    with open(path, "r") as f:
        return list(DictReader(f))
    
def write_file(data, path, mode="w"):
    ''' write into csv file'''
    if mode not in "wa" : #error if not in append or write mode
        raise ValueError('mode should be write or append')
    
    with open(path, "w") as f:
        writer=DictWriter(f, fieldnames=data[0].keys())
        if mode == "w":
            writer.writeheader()
        
        for row in data:
            writer.writerow(row)


def geocode_bulk(data, column="name", verbose=False):
    """assuming data is an iterable of dicts, will attempt to geocode each,
    treating {column} as an address. Returns 2 iterables - result and errored rows"""
    result, errors = [], []
    for row in tqdm(data):
        try:
            search=nominatim_geocode(row[column])
            if len(search)==0:
                print(f' No information found for {row[column]}')
            else:
                info = search[0]
                #print(f' The site {row[column]} is at geolocation Lat: {info["lat"]} and Long: {info["lon"]} in {info["country"]}')
                info.update(row)
                result.append(info)
        except Exception as e:
            if verbose:
                print(e)
            row["error"] = e
            errors.append(row)

    if len(errors) > 0 and verbose:
        print(f"{len(errors)}/{len(data)} rows failed")

    return result, errors

path_in='Chapter06/sites.csv'
path_out='Chapter06/output.csv'
data = read_file(path_in)
results,errors = geocode_bulk(data, column='name', verbose=True)
write_file(results, path_out)

data=read_file(path_out)
for row in data:
    print(f' {row["name"]},{row["country"]} is at latitude: {round(float(row["lat"]),3)} and longitude:{round(float(row["lon"]),3)} ')

