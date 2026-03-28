import pandas as pd

def load_data(file_path):
    return pd.read_csv(file_path)

def analyze_performance(df):
    return df.groupby("subject")["score"].mean()

def weakest_subject(df):
    avg = df.groupby("subject")["score"].mean()
    return avg.idxmin()