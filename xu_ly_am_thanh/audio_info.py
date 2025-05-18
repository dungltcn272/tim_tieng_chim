import numpy as np
import pandas as pd
import librosa

class AudioInfo:
    def __init__(self, file_path):
        self.file_path = file_path
        self.y, self.sr = librosa.load(file_path)
    
    def extract_features(self):
        features = {
            'file_path': self.file_path,
            'zcr': np.mean(librosa.feature.zero_crossing_rate(self.y)),
            'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=self.y, sr=self.sr)),
            'spectral_rolloff': np.mean(librosa.feature.spectral_rolloff(y=self.y, sr=self.sr))
        }

        mfccs = librosa.feature.mfcc(y=self.y, sr=self.sr, n_mfcc=13)
        for i, mfcc in enumerate(mfccs):
            features[f'mfcc_{i}'] = np.mean(mfcc)

        chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr)
        for i, c in enumerate(chroma):
            features[f'chroma_{i}'] = np.mean(c)

        return pd.DataFrame([features])
