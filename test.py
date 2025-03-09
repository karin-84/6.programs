import os
import numpy as np
from scipy.fftpack import fft, ifft
from fractions import Fraction

def load_data_from_folder(folder_path):
    data_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    all_data = {}
    
    for file in sorted(data_files):
        file_path = os.path.join(folder_path, file)
        data = np.loadtxt(file_path)
        all_data[file] = data
    
    return all_data

def perform_fft(velocity_data, time_interval):
    N = len(velocity_data)
    T = time_interval  # データ間隔（秒）
    freq = np.fft.fftfreq(N, T)
    fft_values = fft(velocity_data)
    return freq, fft_values

def apply_lowpass_filter(freq, fft_values, cutoff):
    filtered_fft = fft_values.copy()
    filtered_fft[np.abs(freq) > cutoff] = 0  # 指定カットオフ周波数以上をゼロにする
    return filtered_fft

def extract_common_prefix(filenames):
    if not filenames:
        return "output"
    prefix = os.path.commonprefix(filenames)
    return prefix.rstrip("_-. ")

def main():
    folder_path = input("フォルダのパスを入力: ")
    save_path = input("処理後のファイルを保存するフォルダのパスを入力: ")
    
    time_interval_input = input("データの時間間隔（秒）を入力 (例: 1/60 または 0.0166): ")
    try:
        time_interval = float(eval(time_interval_input))
    except Exception as e:
        print(f"入力エラー: {e}")
        return
    
    cutoff_freq = float(input("ローパスフィルタのカットオフ周波数(Hz)を入力: "))
    
    all_data = load_data_from_folder(folder_path)
    
    if not all_data:
        print("指定したフォルダには処理可能なファイルがありません。")
        return
    
    common_prefix = extract_common_prefix(list(all_data.keys()))
    output_folder_name = f"{time_interval:.5f}sec_lp{cutoff_freq:.2f}Hz_{common_prefix}"
    output_folder_path = os.path.join(save_path, output_folder_name)
    os.makedirs(output_folder_path, exist_ok=True)
    
    for file, data in all_data.items():
        if data.shape[1] < 5:
            print(f"ファイル {file} のデータ形式が不正です。")
            continue
        
        velocity_data = data[:, 4]  # 速さデータを取得
        freq, fft_values = perform_fft(velocity_data, time_interval)
        filtered_fft = apply_lowpass_filter(freq, fft_values, cutoff_freq)
        processed_velocity = np.real(ifft(filtered_fft))
        
        data[:, 4] = processed_velocity  # 速さ部分を更新
        output_file_path = os.path.join(output_folder_path, f"{time_interval:.5f}sec_lp{cutoff_freq:.2f}Hz_{file}")
        np.savetxt(output_file_path, data, fmt='%g')
        print(f"保存完了: {output_file_path}")

if __name__ == "__main__":
    main()
