import pandas as pd
from tim_kiem_tuong_dong.distance_calculator import calculate_distance

def search_similar(output_csv, dataset_df, mean_std_df, query_df):
    results = []
    for _, row in dataset_df.iterrows():
        candidate_df = pd.DataFrame([row])
        dist = calculate_distance(candidate_df.select_dtypes(include="number"), query_df.select_dtypes(include="number"))
        results.append({'file_path': row['file_path'], 'distance': dist})

    result_df = pd.DataFrame(results).sort_values(by="distance")
    result_df.to_csv(output_csv, index=False)
    return result_df
