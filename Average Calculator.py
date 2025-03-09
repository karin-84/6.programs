import numpy as np
import glob
import re
import os

def get_txt_files(directory):
    """
    指定されたフォルダ内のすべての .txt ファイルを取得する。
    """
    search_pattern = os.path.join(directory, "*.txt")
    return glob.glob(search_pattern)

def extract_pattern(file_name):
    """
    ファイル名から共通部分と連番部分を抽出する。
    """
    match = re.match(r"(.+?)(\d{6})\.txt", os.path.basename(file_name))  # 例: test22lm_C001H001S000001.txt
    if match:
        return match.group(1), int(match.group(2))  # (共通部分, 連番部分)
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
                left_cols.append(values[:2])  # 左2列を保存
                numeric_data.append([float(v) for v in values[2:]])
    
    return left_cols, np.array(numeric_data)

def process_files(directory):
    """
    指定されたディレクトリ内のファイルを処理し、同じパターンのファイルを平均化する。
    """
    all_files = get_txt_files(directory)
    file_groups = {}
    
    for file in all_files:
        prefix, number = extract_pattern(file)
        if prefix:
            if prefix not in file_groups:
                file_groups[prefix] = []
            file_groups[prefix].append((number, file))
    
    for prefix, files in file_groups.items():
        files.sort()  # 数字部分でソート
        file_paths = [f[1] for f in files]
        
        print(f"処理対象: {len(file_paths)} 個のファイル ({prefix}...)\n")
        
        if len(file_paths) < 2:
            print("ファイルが1つしかないためスキップ\n")
            continue
        
        base_left_cols, base_data = read_data(file_paths[0])
        num_files = len(file_paths)
        sum_data = np.zeros_like(base_data)
        
        for file_path in file_paths:
            left_cols, data = read_data(file_path)
            
            if data.shape != base_data.shape or left_cols != base_left_cols:
                print(f"エラー: {file_path} のデータ構造が異なります。処理を中止します。\n")
                continue
            
            sum_data += data  # データを累積
        
        averaged_data = sum_data / num_files
        output_path = os.path.join(directory, f"{prefix}_averaged.txt")
        
        with open(output_path, 'w') as file:
            for left, avg_row in zip(base_left_cols, averaged_data):
                file.write("  ".join(left) + "  " + "  ".join(f"{v:.8e}" for v in avg_row) + "\n")
        
        print(f"{num_files} 個のファイルを平均化し、{output_path} に保存しました。\n")

if __name__ == "__main__":
    directory = input("処理するフォルダのパスを入力してください: ").strip()
    if os.path.isdir(directory):
        process_files(directory)
    else:
        print("エラー: 指定されたフォルダが見つかりません。\n")
