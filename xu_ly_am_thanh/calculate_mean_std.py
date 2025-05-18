import pandas as pd


# tính toán trung bình  + độ lệch chuẩn
def calculate_mean_std(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    numeric_df = df.select_dtypes(include="number")
    mean_std_df = pd.DataFrame({
        'column_name': numeric_df.columns,
        'mean': numeric_df.mean().values,
        'std': numeric_df.std().values
    })
    mean_std_df.to_csv(output_csv, index=False)
