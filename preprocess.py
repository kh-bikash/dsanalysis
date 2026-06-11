import pandas as pd
import numpy as np

def preprocess_and_merge():
    print("Loading data...")
    sentiment_df = pd.read_csv('fear_greed_index.csv')
    historical_df = pd.read_csv('historical_data.csv')
    
    print("Processing Fear & Greed dates...")
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    
    print("Processing Historical timestamps...")
    # Convert 'Timestamp IST' to datetime
    # Timestamp IST is in format DD-MM-YYYY HH:MM
    historical_df['Datetime_IST'] = pd.to_datetime(historical_df['Timestamp IST'], format='%d-%m-%Y %H:%M')
    
    # Localize to IST and convert to UTC
    historical_df['Datetime_UTC'] = historical_df['Datetime_IST'].dt.tz_localize('Asia/Kolkata').dt.tz_convert('UTC')
    
    # Extract UTC date for merging
    historical_df['date'] = historical_df['Datetime_UTC'].dt.normalize().dt.tz_localize(None)
    
    print("Merging datasets...")
    # Merge on the date
    merged_df = pd.merge(historical_df, sentiment_df, on='date', how='inner')
    
    print("Merged data shape:", merged_df.shape)
    print("Unique dates in merged data:", merged_df['date'].nunique())
    print("Check merged columns:")
    print(merged_df[['Timestamp IST', 'Datetime_UTC', 'date', 'value', 'classification']].head(5))
    
    # Save merged data
    output_file = 'merged_data.csv'
    print(f"Saving merged dataset to {output_file}...")
    merged_df.to_csv(output_file, index=False)
    print("Done!")

if __name__ == '__main__':
    preprocess_and_merge()
