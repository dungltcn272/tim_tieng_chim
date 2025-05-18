import pandas as pd

def load_mean_std(csv_path):
    return pd.read_csv(csv_path)


# chuẩn hóa Z-Score (-1 -> 1)
def normalize_features(df, mean_std_df):
    df_normalized = df.copy()
    for col in df.select_dtypes(include="number").columns:
        mean = mean_std_df.loc[mean_std_df['column_name'] == col, 'mean'].values[0]
        std = mean_std_df.loc[mean_std_df['column_name'] == col, 'std'].values[0]
        df_normalized[col] = (df_normalized[col] - mean) / std
    return df_normalized
