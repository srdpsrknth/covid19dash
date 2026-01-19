#!/usr/bin/env python
# coding: utf-8
"""
RIVM Data Processor
Processes raw COVID-19 data from RIVM and outputs cleaned datasets.
This script handles all data transformation and cleaning.
"""

from pathlib import Path
import numpy as np
import pandas as pd


RAWPATH = Path.cwd().parent / 'raw-data'
CLEANPATH = Path.cwd().parent / 'clean-data'


def export_csv(df, name):
    """Export dataframe to clean-data directory"""
    path = CLEANPATH / f'{name}.csv'
    df.to_csv(path)
    print(f"✓ {name} saved to {path}")


def set_nat_cumu():
    """Process national cumulative data"""
    df_cumu = pd.read_csv(RAWPATH / 'cumulative_raw.csv', sep=',')
    if 'Unnamed: 0' in df_cumu.columns:
        df_cumu.drop('Unnamed: 0', axis=1, inplace=True)
    
    df_cumu['date'] = pd.to_datetime(df_cumu['Date_of_report']).dt.date
    df_cumu.drop(['Municipality_code','Municipality_name','Date_of_report'], inplace=True, axis=1)
    
    mapping = {
        'Total_reported':'total',
        'Hospital_admission':'admitted',
        'Deceased':'deaths'
    }
    
    df_cumu.rename(mapping, inplace=True, axis=1)
    df_cumu = df_cumu.groupby(['date'])[['total','admitted','deaths']].sum().reset_index()
    
    export_csv(df_cumu, "national_cumulative_clean")
    print("national_cumulative_clean exported to csv")


def set_province_cumu():
    """Process provincial cumulative data"""
    df_province = pd.read_csv(RAWPATH / 'cumulative_raw.csv', sep=',')
    if 'Unnamed: 0' in df_province.columns:
        df_province.drop('Unnamed: 0', axis=1, inplace=True)
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
    
    export_csv(df_province, "province_cumulative_clean")
    print("province_cumulative_clean exported to csv")


def set_nat_daily():
    """Process national daily data: sum by publication date (ignore version/report)"""
    df = pd.read_csv(RAWPATH / 'daily_raw.csv', sep=',')
    if 'Unnamed: 0' in df.columns:
        df.drop('Unnamed: 0', axis=1, inplace=True)

    df['date'] = pd.to_datetime(df['Date_of_publication']).dt.date

    mapping = {
        'Total_reported': 'total',
        'Deceased': 'deaths'
    }
    df.rename(mapping, inplace=True, axis=1)

    # Aggregate cases only; daily deaths are ignored due to unreliable source data
    df_nat = df.groupby('date')[['total']].sum().reset_index()
    df_nat['deaths'] = pd.NA

    export_csv(df_nat, "national_daily_clean")
    print("national_daily_clean exported to csv")


def set_province_daily():
    """Process provincial daily data: sum by publication date and province"""
    df = pd.read_csv(RAWPATH / 'daily_raw.csv', sep=',')
    if 'Unnamed: 0' in df.columns:
        df.drop('Unnamed: 0', axis=1, inplace=True)
    df['date'] = pd.to_datetime(df['Date_of_publication']).dt.date

    mapping = {
        'Total_reported': 'total',
        'Deceased': 'deaths',
        'Province': 'province'
    }
    df.rename(mapping, inplace=True, axis=1)

    # Aggregate cases only; daily deaths are ignored due to unreliable source data
    df_prov = df.groupby(['date', 'province'])[['total']].sum().reset_index()
    df_prov['deaths'] = pd.NA

    export_csv(df_prov, "province_daily_clean")
    print("province_daily_clean exported to csv")


def clean_desc_data():
    """Process descriptive/demographic data (uses comma separator)"""
    # Note: Descriptive data uses comma separator, not semicolon
    df = pd.read_csv(RAWPATH / 'descriptive_raw.csv', sep=",")
    
    # Drop the unnamed first column
    if 'Unnamed: 0' in df.columns:
        df.drop('Unnamed: 0', axis=1, inplace=True)
    
    df['date'] = pd.to_datetime(df['Date_statistics']).dt.date
    df.drop(['Date_file','Date_statistics','Week_of_death', 'Municipal_health_service'], 
            inplace=True, axis=1)
    
    mapping = {
        'Date_statistics_type':'stat_type',
        'Agegroup':'agegroup',
        'Sex':'sex',
        'Province':'province',
        'Deceased':'Death'
    }
    
    df.rename(mapping, inplace=True, axis=1)
    
    export_csv(df, "descriptive_clean")
    print("descriptive_clean exported to csv")


def clean_repro_data():
    """Process reproduction number data"""
    df = pd.read_csv(RAWPATH / 'reproduction_raw.csv', sep=',')
    
    if 'Unnamed: 0' in df.columns:
        df.drop('Unnamed: 0', axis=1, inplace=True)
    df['date'] = pd.to_datetime(df['Date']).dt.date
    df.drop(['Date','population'], inplace=True, axis=1)
    
    mapping = {
        'Rt_low':'R_min',
        'Rt_avg':'R_avg',
        'Rt_up':'R_high'
    }
    
    df.rename(mapping, inplace=True, axis=1)
    
    export_csv(df, "reproduction_clean")
    print("reproduction_clean exported to csv")


def clean_contagious_data():
    """Process contagious prevalence data"""
    df = pd.read_csv(RAWPATH / 'contagious_raw.csv', sep=',')
    
    if 'Unnamed: 0' in df.columns:
        df.drop('Unnamed: 0', axis=1, inplace=True)
    df['date'] = pd.to_datetime(df['Date']).dt.date
    df.drop(['Date','population'], inplace=True, axis=1)
    
    mapping = {
        'prev_low':'min',
        'prev_avg':'avg',
        'prev_up':'high'
    }
    
    df.rename(mapping, inplace=True, axis=1)
    
    export_csv(df, "contagious_clean")
    print("contagious_clean exported to csv")


if __name__ == "__main__":
    print("=" * 60)
    print("Processing COVID-19 Data from RIVM")
    print("=" * 60)
    
    print("\n[1/7] Processing national cumulative data...")
    set_nat_cumu()
    
    print("\n[2/7] Processing provincial cumulative data...")
    set_province_cumu()
    
    print("\n[3/7] Processing national daily data...")
    set_nat_daily()
    
    print("\n[4/7] Processing provincial daily data...")
    set_province_daily()
    
    print("\n[5/7] Processing descriptive data...")
    clean_desc_data()
    
    print("\n[6/7] Processing reproduction data...")
    clean_repro_data()
    
    print("\n[7/7] Processing contagious prevalence data...")
    clean_contagious_data()
    
    print("\n" + "=" * 60)
    print("✓ All data processing completed successfully!")
    print("=" * 60)
