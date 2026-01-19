#!/usr/bin/env python
# coding: utf-8
"""
RIVM Data Fetcher
Fetches raw COVID-19 data from RIVM APIs and saves to raw-data directory.
This script handles all network I/O and should be run periodically.
"""

from datetime import date
from pathlib import Path

import pandas as pd
import requests
import ssl
import urllib.request

# Bypass SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# URLs for RIVM data
URL_cumu = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv"
URL_daily = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv"
URL_desc = "https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv"
URL_repro = "https://data.rivm.nl/covid-19/COVID-19_reproductiegetal.json"
URL_contagious = "https://data.rivm.nl/covid-19/COVID-19_prevalentie.json"

RAWPATH = Path.cwd().parent / 'raw-data'


def export_csv(df, name):
    """Export dataframe to raw-data directory"""
    path = RAWPATH / f'{name}.csv'
    df.to_csv(path)
    print(f"✓ {name} saved to {path}")


# Fetch cumulative data
print("Fetching cumulative data...")
df_cumu = pd.read_csv(URL_cumu, sep=";")
export_csv(df_cumu, "cumulative_raw")

# Fetch daily data
print("Fetching daily data...")
df_daily = pd.read_csv(URL_daily, sep=";")
export_csv(df_daily, "daily_raw")

# Fetch descriptive data
print("Fetching descriptive data...")
df_desc = pd.read_csv(URL_desc, sep=";")
export_csv(df_desc, "descriptive_raw")

# Fetch reproduction data
print("Fetching reproduction data...")
df_repro = pd.read_json(URL_repro)
export_csv(df_repro, "reproduction_raw")

# Fetch contagious data
print("Fetching contagious data...")
df_contagious = pd.read_json(URL_contagious)
export_csv(df_contagious, "contagious_raw")

print("\n✓ All raw data files updated successfully!")
