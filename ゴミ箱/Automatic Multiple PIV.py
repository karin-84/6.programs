import os
import glob
import re
import time
import subprocess
import pyautogui
import pyperclip  # クリップボード操作用

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

    # 最終番号を取得
    file_info.sort(key=lambda x: x[1])
    final_num = file_info[-1][1]

    return file_info[0][0], final_num

def create_save_folder(savefolder_pass, bpass):
    """ Bpassの最終フォルダ名と同じフォルダを savefolder_pass に作成 """
    folder_name = os.path.basename(bpass)  # Bpassの最終フォルダ名を取得
    save_path = os.path.join(savefolder_pass, folder_name)  # 保存先フォルダのパスを作成
    os.makedirs(save_path, exist_ok=True)  # フォルダがなければ作成
    return save_path  # 作成したフォルダのパスを返す

def wait_for_occ_log_access():
    """ OCC.log のアクセスが可能になるまで待機する """
    temp_path = os.path.join(os.environ['LOCALAPPDATA'], "Temp", "OCC.log")
    
    for _ in range(5):  # 最大5回リトライ
        if os.path.exists(temp_path):
            try:
                with open(temp_path, "a"):  # 書き込みモードで開く
                    print("OCC.log へのアクセスが可能になりました。")
                    return True
            except PermissionError:
                print("OCC.log へのアクセスが拒否されました。1秒待機...")
                time.sleep(1)
        else:
            print("OCC.log が存在しないため、スキップします。")
            return True
    
    print("OCC.log のアクセス待機を5回試行しましたが失敗しました。")
    return False

def launch_piv_instance(instance_id, bpass, name, final_num, b_savefolder_pass):
    """ PIVソフトを起動し、環境変数を変更して競合を防ぐ """

    # 各PIV用の一時フォルダを作成
    temp_folder = os.path.join(os.environ['LOCALAPPDATA'], "Temp", f"PIV_{instance_id}")
    os.makedirs(temp_folder, exist_ok=True)
    
    # 環境変数を変更
    env = os.environ.copy()
    env["TEMP"] = temp_folder
    env["TMP"] = temp_folder

    # PIVを起動（環境変数を変更して実行）
    user_profile = os.environ['USERPROFILE']
    shortcut_path = os.path.abspath(os.path.join(user_profile, r'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\PIV\PIV.lnk'))
    
    subprocess.Popen(['cmd', '/c', 'start', '', shortcut_path], shell=True, env=env)
    
    # PIVの起動待機
    time.sleep(5)

    print(f"PIV {instance_id} を {temp_folder} の環境で起動しました")

    # TABキー3回
    pyautogui.press('tab', presses=3)

    # Bpassを入力
    pyperclip.copy(bpass)
    print(f"入力するBpass: {bpass}")
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab', presses=2)

    # nameを入力
    print(f"入力するName: {name}")
    pyperclip.copy(name)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab', presses=3)

    # first_numberを入力
    print(f"入力するfirst_number: {first_number}")
    pyperclip.copy(first_number)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab', presses=1)

    # final_num - 1 を入力
    final_input_num = str(final_num - 1)
    print(f"入力するFinalNum: {final_input_num}")
    pyperclip.copy(final_input_num)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('tab', presses=7)

    # B_savefolder_passを入力
    print(f"入力するB_savefolder_pass: {b_savefolder_pass}")
    pyperclip.copy(b_savefolder_pass)
    pyautogui.hotkey('ctrl', 'v')
    

    # ファイル読み込み
    pyautogui.press('tab', presses=3)
    pyautogui.press('enter')

    # ファイルの読み込みが終わるまで待機（状況によって調整が必要）
    time.sleep(5)

    #PIV開始
    pyautogui.press('tab', presses=4)
    pyautogui.press('enter')

# メイン処理
if __name__ == '__main__':
    # ユーザーにフォルダパス(Apass)と保存先(savefolder_pass)を入力させる
    apass = input("フォルダパス(Apass)を入力してください: ").strip()
    savefolder_pass = input("保存先のフォルダパス(savefolder_pass)を入力してください: ").strip()
    first_number = input("1枚目番号(first_number)を入力してください:").strip()

    # パスを正規化
    apass = os.path.abspath(apass)
    savefolder_pass = os.path.abspath(savefolder_pass)
    print(f"正規化されたApass: {apass}")
    print(f"正規化されたSaveFolderPass: {savefolder_pass}")

    # Apass内の有効なフォルダ(Bpass)を取得
    valid_folders = get_folders_with_bmp(apass)

    if not valid_folders:
        print("BMPファイルのあるフォルダが見つかりませんでした。")
    else:
        for idx, bpass in enumerate(valid_folders):
            bpass = os.path.abspath(bpass)  # パスを正規化
            print(f"正規化されたBpass: {bpass}")

            # 保存先フォルダを作成
            b_savefolder_pass = create_save_folder(savefolder_pass, bpass)
            print(f"作成されたB_savefolder_pass: {b_savefolder_pass}")

            name, final_num = extract_common_name_and_final_num(bpass)
            if name and final_num:
                print(f"処理中: {bpass}")
                print(f"共通名: {name}, 最終番号: {final_num}")

                # PIVの起動
                launch_piv_instance(idx, bpass, name, final_num, b_savefolder_pass)
            else:
                print(f"{bpass} の処理をスキップしました。")
