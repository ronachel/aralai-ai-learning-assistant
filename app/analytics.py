import pandas as pd

def load_data(path):
    return pd.read_csv(path)

def analyze_performance(df):
    return df.groupby("subject")["score"].mean()

def weakest_subject(df):
    return df.groupby("subject")["score"].mean().idxmin()