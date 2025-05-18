import os
import threading
import customtkinter as ctk
import pygame
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from xu_ly_am_thanh import audio_info, normalize_feature, calculate_mean_std
from csdl_dac_trung import build_feature_database
from tim_kiem_tuong_dong import similarity_search

pygame.mixer.init()

DATASET_CSV = "dataset.csv"
MEAN_STD_CSV = "mean_std.csv"
BIRD_FOLDER = "birdsounds"

def find_most_similar(query_file, top_k=3):
    if not os.path.exists(DATASET_CSV) or not os.path.exists(MEAN_STD_CSV):
        print("Chưa có dataset.csv hoặc mean_std.csv.")
        return []
    ai = audio_info.AudioInfo(query_file)
    df_query = ai.extract_features()
    df_mean_std = normalize_feature.load_mean_std(MEAN_STD_CSV)
    df_query_z = normalize_feature.normalize_features(df_query, df_mean_std)
    df_dataset = pd.read_csv(DATASET_CSV)
    df_dataset_z = normalize_feature.normalize_features(df_dataset, df_mean_std)
    result_df = similarity_search.search_similar("result.csv", df_dataset_z, df_mean_std, df_query_z)
    result_df = result_df[result_df['file_path'] != query_file]
    top_k_results = result_df.head(top_k).to_dict('records')
    return [(r['file_path'], r['distance']) for r in top_k_results]

class BirdSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bird Sound Finder")
        self.root.geometry("900x800")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.current_file = None
        self.result_files = {}
        self.query_playing = False
        self.feature_canvas = None

        self.build_button = ctk.CTkButton(self.root, text="Xây dựng CSDL từ birdsounds", command=self.build_database, width=300, height=40)
        self.build_button.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.root, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()

        self.drop_frame = ctk.CTkFrame(self.root, height=120, fg_color="#2A2D3E", corner_radius=10)
        self.drop_frame.pack(pady=20, padx=20, fill="x")
        self.drop_frame.drop_target_register(DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self.drop_file)

        self.label_drop = ctk.CTkLabel(self.drop_frame, text="Kéo và thả file .mp3, .wav hoặc .flac hoặc nhấn để chọn", font=("Arial", 18, "bold"), text_color="#40C4FF")
        self.label_drop.pack(pady=40)
        self.label_drop.bind("<Button-1>", self.browse_file)

        self.play_button = ctk.CTkButton(self.root, text="Play", command=self.toggle_play_query, state="disabled", width=120, height=40)
        self.play_button.pack(pady=15)

        self.feature_button = ctk.CTkButton(self.root, text="Xem đặc trưng file", command=self.show_features, state="disabled", width=200, height=40)
        self.feature_button.pack(pady=5)

        self.file_label = ctk.CTkLabel(self.root, text="Chưa có file", font=("Arial", 16), text_color="#B0BEC5", fg_color="#2A2D3E", corner_radius=8, width=400, height=40)
        self.file_label.pack(pady=10)

        self.loading_label = ctk.CTkLabel(self.root, text="", font=("Arial", 14), text_color="#28A9FF")
        self.loading_label.pack(pady=10)

        self.result_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.result_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def build_database(self):
        self.loading_label.configure(text="Đang xây dựng CSDL từ birdsounds...")
        threading.Thread(target=self._build_database_thread, daemon=True).start()

    def _build_database_thread(self):
        if os.path.exists(DATASET_CSV) and os.path.exists(MEAN_STD_CSV):
            self.loading_label.configure(text="CSDL đã tồn tại. Xóa hoặc đổi tên file trước khi tạo lại.")
            return
        try:
            self.root.after(0, lambda: self.progress_bar.pack(pady=10))
            self.root.after(0, lambda: self.progress_bar.set(0.3))
            build_feature_database.build_database(BIRD_FOLDER, DATASET_CSV)
            self.root.after(0, lambda: self.progress_bar.set(0.7))
            calculate_mean_std.calculate_mean_std(DATASET_CSV, MEAN_STD_CSV)
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            self.root.after(0, lambda: self.progress_bar.pack_forget())
            self.loading_label.configure(text="Đã xây dựng xong CSDL.")
        except Exception as e:
            self.root.after(0, lambda: self.progress_bar.pack_forget())
            self.loading_label.configure(text=f"Lỗi: {e}")

    def browse_file(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.wav *.flac")])
        if file_path:
            self.process_file(file_path)

    def drop_file(self, event):
        file_path = event.data.strip("{}")
        if file_path.endswith((".mp3", ".wav", ".flac")):
            self.process_file(file_path)

    def process_file(self, file_path):
        self.current_file = file_path
        self.file_label.configure(text=f"File: {os.path.basename(file_path)}")
        self.play_button.configure(state="normal")
        self.feature_button.configure(state="normal")
        self.loading_label.configure(text="Đang tìm kiếm...")
        self.clear_results()
        threading.Thread(target=self.search_bird, args=(file_path,), daemon=True).start()

    def search_bird(self, file_path):
        results = find_most_similar(file_path, top_k=3)
        self.root.after(0, self.display_results, results)

    def display_results(self, results):
        self.loading_label.configure(text="")
        self.clear_results()
        if not results:
            ctk.CTkLabel(self.result_frame, text="Không tìm thấy kết quả", font=("Arial", 16), text_color="#FF5252").pack(pady=20)
            return
        for i, (file_path, distance) in enumerate(results):
            frame = ctk.CTkFrame(self.result_frame, fg_color="#2A2D3E", corner_radius=10)
            frame.pack(pady=10, padx=10, fill="x")
            label = ctk.CTkLabel(frame, text=f"Kết quả {i+1}: {file_path} (Khoảng cách: {distance:.4f})", font=("Arial", 14), text_color="#B0BEC5")
            label.pack(side="left", padx=10, pady=10)
            play_button = ctk.CTkButton(frame, text="Play", width=100, height=36, command=lambda f=file_path: self.toggle_play_result(f, play_button))
            play_button.pack(side="right", padx=10)
            self.result_files[file_path] = {"button": play_button, "playing": False}

    def show_features(self):
        if not self.current_file:
            return

        ai = audio_info.AudioInfo(self.current_file)
        features = ai.extract_features().iloc[0].drop("file_path").to_dict()

        # Tạo cửa sổ mới (toplevel window)
        feature_window = ctk.CTkToplevel(self.root)
        feature_window.title("Đặc trưng âm thanh")
        feature_window.geometry("800x400")

        fig, ax = plt.subplots(figsize=(8, 4), facecolor="#f9f9f9")
        ax.bar(features.keys(), features.values(), color="#4CAF50", width=0.5)

        ax.set_title("Đặc trưng của file", fontsize=14, fontweight='bold')
        ax.set_facecolor("#f9f9f9")
        ax.tick_params(axis='x', rotation=45, labelsize=8)
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=feature_window)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)


    def toggle_play_result(self, file_path, button):
        current_playing = self.result_files[file_path]["playing"]
        pygame.mixer.music.stop()
        if current_playing:
            self.result_files[file_path]["button"].configure(text="Play")
            self.result_files[file_path]["playing"] = False
        else:
            self.play_button.configure(text="Play")
            self.query_playing = False
            for fp, info in self.result_files.items():
                info["button"].configure(text="Play")
                info["playing"] = False
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()
                self.result_files[file_path]["button"].configure(text="Pause")
                self.result_files[file_path]["playing"] = True
            except Exception as e:
                print(f"Lỗi: {e}")

    def toggle_play_query(self):
        if not self.current_file:
            return
        if self.query_playing:
            pygame.mixer.music.pause()
            self.play_button.configure(text="Play")
            self.query_playing = False
        else:
            pygame.mixer.music.stop()
            for fp, info in self.result_files.items():
                info["button"].configure(text="Play")
                info["playing"] = False
            pygame.mixer.music.load(self.current_file)
            pygame.mixer.music.play()
            self.play_button.configure(text="Pause")
            self.query_playing = True

    def clear_results(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        if self.feature_canvas:
            self.feature_canvas.get_tk_widget().destroy()
            self.feature_canvas = None
        self.result_files = {}
        pygame.mixer.music.stop()
        self.play_button.configure(text="Play")
        self.query_playing = False

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = BirdSearchApp(root)
    root.mainloop()
