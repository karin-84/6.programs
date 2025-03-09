import os
import numpy as np
from scipy.fftpack import fft, ifft
from fractions import Fraction

# ==================================================

folder_path = "test_input"
save_path = "test_output"
time_interval = 1/60
cutoff_freq = 5


# ==================================================

def load_data_from_folder(folder_path):
    data_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    all_data = {}
    
    for file in sorted(data_files):
        file_path = os.path.join(folder_path, file)
        print(file_path)
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
    #filtered_fft[np.abs(freq) > cutoff] = 0  # 指定カットオフ周波数以上をゼロにする
    for index in range(len(fft_values)):
        if cutoff < abs(freq[index]):
            filtered_fft[index] = 0.0
    return filtered_fft

def extract_common_prefix(filenames):
    if not filenames:
        return "output"
    prefix = os.path.commonprefix(filenames)
    return prefix.rstrip("_-. ")

def main():
    
    all_data = load_data_from_folder(folder_path)
    
    common_prefix = extract_common_prefix(list(all_data.keys()))
    output_folder_name = f"{time_interval:.5f}sec_lp{cutoff_freq:.2f}Hz_{common_prefix}"
    output_folder_path = os.path.join(save_path, output_folder_name)
    os.makedirs(output_folder_path, exist_ok=True)

    data = list(all_data.items())
    data_size = len(data[0][1])
    
    for index in range(data_size):

        coordinate_data = []
        #print(len(coordinate_data))

        for i in range(len(all_data.items())):
            coordinate_data.append(data[i][1][4][index])

        print(coordinate_data)

        velocity_data = coordinate_data  # 速さデータを取得
        freq, fft_values = perform_fft(velocity_data, time_interval)
        filtered_fft = apply_lowpass_filter(freq, fft_values, cutoff_freq)
        processed_velocity = np.real(ifft(filtered_fft))
        
        data[:, 4] = processed_velocity  # 速さ部分を更新
        output_file_path = os.path.join(output_folder_path, f"{time_interval:.5f}sec_lp{cutoff_freq:.2f}Hz_{file}")
        np.savetxt(output_file_path, data, fmt='%g')
        print(f"保存完了: {output_file_path}")

if __name__ == "__main__":
    main()
