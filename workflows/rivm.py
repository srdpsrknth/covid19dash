#!/usr/bin/env python
# coding: utf-8

# In[52]:


from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

import requests


# In[53]:


URL_cumu = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv"
URL_daily = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv"
URL_desc = "https://data.rivm.nl/covid-19/COVID-19_casus_landelijk.csv"
URL_repro = "https://data.rivm.nl/covid-19/COVID-19_reproductiegetal.json"
URL_contagious = "https://data.rivm.nl/covid-19/COVID-19_prevalentie.json"
RAWPATH = Path.cwd().parent / 'raw-data' 
CLEANPATH = Path.cwd().parent / 'clean-data' 


# In[54]:


def export_csv(df, name, raw=0):
    if raw:
        path = Path.cwd().parent / 'raw-data' / '{}.csv'.format(name)
    else:
        path = Path.cwd().parent / 'clean-data' / '{}.csv'.format(name)
        
    df.to_csv(path)


# In[55]:


def set_nat_cumu(url):
    df_cumu = pd.read_csv(url,sep=";")
    
    export_csv(df_cumu, "cumulative_raw", raw=1)
    print("cumulative_raw exported to csv")
    
    df_cumu['date'] = pd.to_datetime(df_cumu['Date_of_report']).dt.date
    df_cumu.drop(['Municipality_code','Municipality_name','Date_of_report'], inplace=True, axis=1)
    
    mapping = {
        'Total_reported':'total',
        'Hospital_admission':'admitted',
        'Deceased':'deaths'
    }
    
    df_cumu.rename(mapping, inplace=True, axis=1)
    
    df_cumu = df_cumu.groupby(['date'])[['total','admitted','deaths']].sum().reset_index()
    
    export_csv(df_cumu,"national_cumulative_clean")
    
    print("national_cumulative_clean exported to csv")


# In[56]:


def set_province_cumu(path):
    df_province = pd.read_csv(path /'cumulative_raw.csv', index_col=0)
    df_province['date'] = pd.to_datetime(df_province['Date_of_report']).dt.date
    df_province.drop(['Municipality_code','Municipality_name','Date_of_report'], inplace=True, axis=1)
    
    mapping = {
        'Total_reported':'total',
        'Hospital_admission':'admitted',
        'Deceased':'deaths',
        'Province':'province'
    }
    
    df_province.rename(mapping, inplace=True, axis=1)
    
    df_province = df_province.groupby(['date','province'])[['total','admitted','deaths']].sum().reset_index()
    
    export_csv(df_province,"province_cumulative_clean")
    
    print("province_cumulative_clean exported to csv")


# In[57]:


def set_nat_daily(url):
    df = pd.read_csv(url,sep=";")
    
    export_csv(df, "daily_raw", raw=1)
    print("daily_raw exported to csv")
    
    df['date'] = pd.to_datetime(df['Date_of_publication']).dt.date
    df.drop(['Municipality_code','Municipality_name','Date_of_publication','Date_of_report','Province','Security_region_code','Security_region_name', 'Municipal_health_service', 'ROAZ_region'], inplace=True, axis=1)
    
    mapping = {
        'Total_reported':'total',
        'Hospital_admission':'admitted',
        'Deceased':'deaths'
    }
    
    df.rename(mapping, inplace=True, axis=1)
    
    df = df.groupby(['date'])[['total','admitted','deaths']].sum().reset_index()
    
    export_csv(df,"national_daily_clean")
    
    print("national_daily_clean exported to csv")
    


# In[58]:


def set_province_daily(path):
    df = pd.read_csv(path /'daily_raw.csv', index_col=0)
    df['date'] = pd.to_datetime(df['Date_of_publication']).dt.date
    df.drop(['Municipality_code','Municipality_name','Date_of_publication','Date_of_report', 'Security_region_code','Security_region_name', 'Municipal_health_service', 'ROAZ_region'], inplace=True, axis=1)
        
    mapping = {
        'Total_reported':'total',
        'Hospital_admission':'admitted',
        'Deceased':'deaths',
        'Province':'province'
    }
    
    df.rename(mapping, inplace=True, axis=1)
    
    df = df.groupby(['date','province'])[['total','admitted','deaths']].sum().reset_index()
    
    export_csv(df,"province_daily_clean")
    
    print("province_daily_clean exported to csv")


# In[59]:


def clean_desc_data(url):
    df = pd.read_csv(url,sep=";")
    
    export_csv(df, "descriptive_raw", raw=1)
    print("descriptive_raw exported to csv")
    
    df['date'] = pd.to_datetime(df['Date_statistics']).dt.date
    df.drop(['Date_file','Date_statistics','Week_of_death', 'Municipal_health_service'], inplace=True, axis=1)
    
    mapping = {
        'Date_statistics_type':'stat_type',
        'Agegroup':'agegroup',
        'Sex':'sex',
        'Province':'province',
        'Hospital_admission':'admitted',
        'Deceased':'Death'
    }
    
    df.rename(mapping, inplace=True, axis=1)
    
    #df = df.groupby(['date'])[['total','admitted','deaths']].sum().reset_index()
    
    export_csv(df,"descriptive_clean")
    
    print("descriptive_clean exported to csv")


# In[60]:


def clean_repro_data(url):
    df = pd.read_json(url)
    
    export_csv(df, "reproduction_raw", raw=1)
    print("reproduction_raw exported to csv")
    
    df['date'] = pd.to_datetime(df['Date']).dt.date
    df.drop(['Date','population'], inplace=True, axis=1)
    
    mapping = {
        'Rt_low':'R_min',
        'Rt_avg':'R_avg',
        'Rt_up':'R_high'
    }
    
    df.rename(mapping, inplace=True, axis=1)
    
    export_csv(df,"reproduction_clean")
    print("reproduction_clean exported to csv")


# In[61]:


def clean_contagious_data(url):
    df = pd.read_json(url)
    
    export_csv(df, "contagious_raw", raw=1)
    print("contagious_raw exported to csv")
    
    df['date'] = pd.to_datetime(df['Date']).dt.date
    df.drop(['Date','population'], inplace=True, axis=1)
    
    mapping = {
        'prev_low':'min',
        'prev_avg':'avg',
        'prev_up':'high'
    }
    
    df.rename(mapping, inplace=True, axis=1)
    
    export_csv(df,"contagious_clean")
    print("contagious_clean exported to csv")


# In[62]:


set_nat_cumu(URL_cumu)
set_province_cumu(RAWPATH)


# In[63]:


set_nat_daily(URL_daily)
set_province_daily(RAWPATH)


# In[64]:


clean_desc_data(URL_desc)


# In[65]:


clean_repro_data(URL_repro)
clean_contagious_data(URL_repro)


# In[ ]:




