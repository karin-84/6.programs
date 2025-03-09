import os
import glob
import re
import time
import subprocess
import keyboard
import pyautogui
import json
import uuid

RUNNING_INSTANCES_FILE = "running_instances.json"

def load_running_instances():
    """ 現在実行中のPIVインスタンスをロードする """
    if os.path.exists(RUNNING_INSTANCES_FILE):
        with open(RUNNING_INSTANCES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_running_instances(instances):
    """ 実行中のPIVインスタンス情報を保存する """
    with open(RUNNING_INSTANCES_FILE, "w") as f:
        json.dump(instances, f, indent=4)

def cleanup_finished_instances():
    """ すでに終了しているPIVインスタンスをリストから削除 """
    instances = load_running_instances()
    active_instances = {}
    
    for key, info in instances.items():
        pid = info.get("pid")
        if pid and is_process_running(pid):
            active_instances[key] = info
    
    save_running_instances(active_instances)

def is_process_running(pid):
    """ 指定したPIDのプロセスが実行中か確認 """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def get_unique_temp_folder():
    """ 既存の環境と被らないユニークなテンポラリフォルダを取得 """
    instances = load_running_instances()
    while True:
        temp_folder = os.path.join(os.environ['LOCALAPPDATA'], "Temp", f"PIV_{uuid.uuid4().hex}")
        if temp_folder not in instances.values():
            return temp_folder

def get_folders_with_bmp(base_path):
    """ 指定フォルダ内のフォルダを取得し、bmpファイルがあるフォルダのみ返す """
    folder_paths = [os.path.abspath(f) for f in glob.glob(os.path.join(base_path, '*')) if os.path.isdir(f)]
    valid_folders = []

    for folder in folder_paths:
        bmp_files = glob.glob(os.path.join(folder, '*.bmp'))
        if bmp_files:
            valid_folders.append(folder)

    return valid_folders

def extract_common_name_and_final_num(folder):
    """ フォルダ内のbmpファイルから共通名(name)と最終番号(final_num)を取得 """
    bmp_files = glob.glob(os.path.join(folder, '*.bmp'))
    if not bmp_files:
        return None, None

    pattern = re.compile(r'^(.*?)(\d{6})\.bmp$')
    file_info = []

    for file in bmp_files:
        filename = os.path.basename(file)
        match = pattern.match(filename)
        if match:
            base_name, number = match.groups()
            file_info.append((base_name, int(number)))

    if not file_info:
        return None, None

    file_info.sort(key=lambda x: x[1])
    final_num = file_info[-1][1]

    return file_info[0][0], final_num

def create_save_folder(savefolder_pass, bpass):
    """ Bpassの最終フォルダ名と同じフォルダを savefolder_pass に作成 """
    folder_name = os.path.basename(bpass)
    save_path = os.path.join(savefolder_pass, folder_name)
    os.makedirs(save_path, exist_ok=True)
    return save_path

def launch_piv_instance(bpass, name, final_num, b_savefolder_pass):
    """ PIVソフトを起動し、競合を防ぐ """
    cleanup_finished_instances()
    temp_folder = get_unique_temp_folder()
    os.makedirs(temp_folder, exist_ok=True)
    
    env = os.environ.copy()
    env["TEMP"] = temp_folder
    env["TMP"] = temp_folder

    user_profile = os.environ['USERPROFILE']
    shortcut_path = os.path.abspath(os.path.join(user_profile, r'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\PIV\PIV.lnk'))
    
    process = subprocess.Popen(['cmd', '/c', 'start', '', shortcut_path], shell=True, env=env)
    pid = process.pid
    
    instances = load_running_instances()
    instances[temp_folder] = {"pid": pid, "bpass": bpass, "name": name, "final_num": final_num, "b_savefolder_pass": b_savefolder_pass}
    save_running_instances(instances)
    
    time.sleep(3)
    print(f"PIV を {temp_folder} の環境で起動しました (PID: {pid})")
    
    # TABキー3回
    pyautogui.press('tab', presses=3)

    # Bpassを入力
    print(f"入力するBpass: {bpass}")
    keyboard.write(bpass)
    pyautogui.press('tab', presses=2)

    # nameを入力
    print(f"入力するName: {name}")
    keyboard.write(name)
    pyautogui.press('tab', presses=3)

    # first_numberを入力
    print(f"入力するfirst_number: {first_number}")
    keyboard.write(first_number)
    pyautogui.press('tab', presses=1)

    # final_num - 1 を入力
    final_input_num = str(final_num - 1)
    print(f"入力するFinalNum: {final_input_num}")
    keyboard.write(final_input_num)
    pyautogui.press('tab', presses=7)

    # B_savefolder_passを入力
    print(f"入力するB_savefolder_pass: {b_savefolder_pass}")
    keyboard.write(b_savefolder_pass)

    # ファイル読み込み
    pyautogui.press('tab', presses=3)
    pyautogui.press('enter')

    # ファイルの読み込みが終わるまで待機（状況によって調整が必要）
    time.sleep(3)

    #PIV開始
    pyautogui.press('tab', presses=4)
    pyautogui.press('enter')


if __name__ == '__main__':
    apass = input("フォルダパス(Apass)を入力してください: ").strip()
    savefolder_pass = input("保存先のフォルダパス(savefolder_pass)を入力してください: ").strip()
    first_number = input("1枚目番号(first_number)を入力してください:").strip()
    
    apass = os.path.abspath(apass)
    savefolder_pass = os.path.abspath(savefolder_pass)
    
    valid_folders = get_folders_with_bmp(apass)
    
    if not valid_folders:
        print("BMPファイルのあるフォルダが見つかりませんでした。")
    else:
        for bpass in valid_folders:
            bpass = os.path.abspath(bpass)
            b_savefolder_pass = create_save_folder(savefolder_pass, bpass)
            name, final_num = extract_common_name_and_final_num(bpass)
            
            if name and final_num:
                launch_piv_instance(bpass, name, final_num, b_savefolder_pass)