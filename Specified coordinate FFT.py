import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from fractions import Fraction
import matplotlib

# 日本語フォント設定
matplotlib.rcParams['font.family'] = 'MS Gothic'  # Windows向け（MS Gothic）
# matplotlib.rcParams['font.family'] = 'TakaoGothic'  # Linux向け（TakaoGothic）
# matplotlib.rcParams['font.family'] = 'IPAexGothic'  # Mac向け（IPAexGothic）

def load_data_from_folder(folder_path, target_x, target_y):
    data_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    velocity_data = []
    
    for file in sorted(data_files):
        file_path = os.path.join(folder_path, file)
        data = np.loadtxt(file_path)
        
        # X, Y の位置が一致するデータを抽出
        matching_rows = data[(data[:, 0] == target_x) & (data[:, 1] == target_y)]
        if len(matching_rows) > 0:
            velocity_data.append(matching_rows[0, 4])  # 速さの列を取得
    
    return np.array(velocity_data)

def perform_fft(velocity_data, time_interval):
    N = len(velocity_data)
    T = time_interval  # データ間隔（秒）
    freq = np.fft.fftfreq(N, T)
    fft_values = fft(velocity_data)
    return freq[:N // 2], np.abs(fft_values)[:N // 2]

def main():
    folder_path = input("フォルダのパスを入力: ")
    target_x = float(input("X座標を入力: "))
    target_y = float(input("Y座標を入力: "))
    
    time_interval_input = input("データの時間間隔（秒）を入力 (例: 1/60 または 0.0166): ")
    try:
        time_interval = float(eval(time_interval_input))
    except Exception as e:
        print(f"入力エラー: {e}")
        return
    
    velocity_data = load_data_from_folder(folder_path, target_x, target_y)
    
    if len(velocity_data) == 0:
        print("指定した座標のデータが見つかりませんでした。")
        return
    
    freq, fft_values = perform_fft(velocity_data, time_interval)
    
    plt.figure(figsize=(12, 6))
    plt.plot(freq, fft_values)
    plt.xlabel("周波数 (Hz)", fontname='MS Gothic')
    plt.ylabel("振幅", fontname='MS Gothic')
    plt.title("速度データのFFT", fontname='MS Gothic')
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()
