import os
from xu_ly_am_thanh.audio_info import AudioInfo
import pandas as pd

def build_database(folder_path, output_csv):
    all_features = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".flac"):
                file_path = os.path.join(root, file)
                try:
                    ai = AudioInfo(file_path)
                    all_features.append(ai.extract_features())
                    print(f"[✔] Đã xử lý: {file_path}")
                except Exception as e:
                    print(f"[✘] Lỗi khi xử lý {file_path}: {e}")

    if all_features:
        final_df = pd.concat(all_features, ignore_index=True)
        final_df.to_csv(output_csv, index=False)
        print(f"[✔] Đã lưu CSDL vào {output_csv}")
    else:
        print("[✘] Không có dữ liệu hợp lệ để lưu.")

