import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

options = Options()
driver = webdriver.Chrome(options=options)

years = [2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007]  

species = ["krondyr", "daadyr", "sika", "raadyr", "muflon", "vildsvin", "hare", "vildkanin", "bisamrotte", "raev", "maarhund", "vaskebjoern", "ilder", "mink", "husmaar"]

kommuner = [165, 201, 420, 151, 530, 400, 153, 810, 155, 240, 561, 563, 710, 320, 210, 607, 147, 813, 250, 260, 190, 430, 157, 159, 161, 253, 270, 376, 510, 766, 217, 163, 657, 219, 860, 316, 661, 615, 167, 169, 223, 756, 183, 849, 326, 440, 621, 101, 259, 482, 350, 665, 360, 173, 825, 846, 410, 773, 707, 480, 450, 370, 727, 461, 306, 730, 840, 760, 329, 265, 230, 175, 741, 740, 746, 779, 330, 269, 340, 336, 671, 479, 706, 540, 787, 550, 185, 187, 573, 575, 630, 820, 791, 390, 492, 580, 851, 751]

year_tokens = {
    2022: "Y706mj8R0",
    2021: "nR8ZkL4LY",
    2020: "jYn5Yl70R",
    2019: "PjYgj4mpl",
    2018: "x6l86DPp9",
    2017: "Dq06q5pVK",
    2016: "369E65omM",
    2015: "57WV75JJA",
    2014: "w0k20BOAm", 
    2013: "pZzBZ0EQQ",
    2012: "x6l86DKXr",
    2011: "w0k20BWZg",
    2010: "79AY954YO",
    2009: "WP8pPD4j4",
    2008: "A6mW654Q1",
    2007: "BrnOr54nn"
    
    
    
    # Add the rest of the years and their corresponding tokens here
}

# Base URL
base_url = "https://api.vildtudbytte.ecoscience.dk/download/detaljer"

# Iterate over each combination
for year in years:
    print(year)
    token = year_tokens.get(year, "")  # Retrieve the token for the year
    if not token:
        print(f"No token found for year {year}")
        continue

    for specie in species:
        print(specie)
        for kom in kommuner:
            print(kom)
            # Construct the URL
            url = f"{base_url}/{year}/{token}/{specie}?kommuneId={kom}"
            print(url)

            # Make the GET request
            response = requests.get(url)
            if response.status_code == 200:
                # Process the response
                print(response.text)
            else:
                print(f"Failed to fetch data for year {year}, specie {specie}, kommune {kom}")
            
            driver.get(url)
            time.sleep(1)
                
driver.quit()


# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2022/Y706mj8R0/raadyr?kommuneId=217

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2021/nR8ZkL4LY/raadyr?kommuneId=201

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2020/jYn5Yl70R/raadyr?kommuneId=201

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2019/PjYgj4mpl/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2018/x6l86DPp9/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2017/Dq06q5pVK/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2016/369E65omM/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2015/57WV75JJA/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2014/w0k20BOAm/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2013/pZzBZ0EQQ/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2012/x6l86DKXr/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2011/w0k20BWZg/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2010/79AY954YO/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2009/WP8pPD4j4/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2008/A6mW654Q1/raadyr?kommuneId=

# https://api.vildtudbytte.ecoscience.dk/download/detaljer/2007/BrnOr54nn/raadyr?kommuneId=