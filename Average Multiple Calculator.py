import numpy as np
import glob
import re
import os

def get_folders(directory):
    """
    指定したディレクトリ内のすべてのフォルダパスを取得。
    """
    return [os.path.join(directory, d) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

def get_txt_files(directory):
    """
    指定されたフォルダ内のすべての .txt ファイルを取得する。
    """
    return glob.glob(os.path.join(directory, "*.txt"))

def extract_pattern(file_name):
    """
    ファイル名から共通部分と連番部分を抽出する。
    """
    match = re.match(r"(.+?)(\d{6})\.txt", os.path.basename(file_name))
    if match:
        return match.group(1), int(match.group(2))
    return None, None

def read_data(file_path):
    """
    指定されたファイルのデータを読み込む。
    左2列は文字データ、それ以降は数値データとして処理する。
    """
    left_cols = []
    numeric_data = []
    
    with open(file_path, 'r') as file:
        for line in file:
            values = line.split()
            if len(values) > 2:
                left_cols.append(values[:2])
                numeric_data.append([float(v) for v in values[2:]])
    
    return left_cols, np.array(numeric_data)

def process_files(input_dir, output_dir):
    """
    指定されたディレクトリ内のファイルを処理し、
    同じパターンのファイルを平均化してoutput_dirに保存する。
    """
    all_files = get_txt_files(input_dir)
    if not all_files:
        return  # ファイルがない場合はスキップ
    
    file_groups = {}
    
    for file in all_files:
        prefix, number = extract_pattern(file)
        if prefix:
            if prefix not in file_groups:
                file_groups[prefix] = []
            file_groups[prefix].append((number, file))
    
    for prefix, files in file_groups.items():
        files.sort()
        file_paths = [f[1] for f in files]
        
        if len(file_paths) < 2:
            continue  # ファイルが1つしかない場合はスキップ
        
        base_left_cols, base_data = read_data(file_paths[0])
        num_files = len(file_paths)
        sum_data = np.zeros_like(base_data)
        
        for file_path in file_paths:
            left_cols, data = read_data(file_path)
            if data.shape != base_data.shape or left_cols != base_left_cols:
                print(f"エラー: {file_path} のデータ構造が異なります。")
                continue
            sum_data += data
        
        averaged_data = sum_data / num_files
        output_path = os.path.join(output_dir, f"{prefix}_averaged.txt")
        
        with open(output_path, 'w') as file:
            for left, avg_row in zip(base_left_cols, averaged_data):
                file.write("  ".join(left) + "  " + "  ".join(f"{v:.8e}" for v in avg_row) + "\n")
        
        print(f"{num_files} 個のファイルを平均化し、{output_path} に保存しました。")

if __name__ == "__main__":
    Apass = input("処理する親フォルダ(Apass)のパスを入力してください: ").strip()
    savefolder_pass = input("保存先フォルダ(savefolder_pass)のパスを入力してください: ").strip()
    
    if not os.path.isdir(Apass):
        print("エラー: 指定された親フォルダが見つかりません。")
        exit()
    
    if not os.path.isdir(savefolder_pass):
        print("エラー: 指定された保存先フォルダが見つかりません。")
        exit()
    
    Bpass_list = get_folders(Apass)
    Bpass_list = [b for b in Bpass_list if get_txt_files(b)]  # txtファイルがあるフォルダのみ処理
    
    for Bpass in Bpass_list:
        print(f"処理中: {Bpass}")
        process_files(Bpass, savefolder_pass)
    
    print("処理完了。")