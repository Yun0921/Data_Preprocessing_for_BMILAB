import os
import pandas as pd
import json
from PIL import Image

# 設定資料來源資料夾
base_input_folder = '.'  # 搜尋當前目錄下所有符合條件的資料夾
base_output_folder = 'process_data'  # 統一輸出資料夾
os.makedirs(base_output_folder, exist_ok=True)

# 找出所有符合 frames_XXXX_XX 命名規則的資料夾
for folder_name in os.listdir(base_input_folder):
    if folder_name.startswith('frames_') and os.path.isdir(folder_name):
        suffix = folder_name.replace('frames_', '')
        csv_file = f'{folder_name}_final_data.csv'
        image_folder = folder_name
        output_folder = os.path.join(base_output_folder, f'data_{suffix}')
        output_json_path = os.path.join(output_folder, 'transitions_dataset.json')

        # 確保輸出資料夾存在
        folders = ['ft1', 'ft2']
        for folder in folders:
            output_path = os.path.join(output_folder, folder)
            os.makedirs(output_path, exist_ok=True)

        # 檢查 CSV 檔案是否存在
        if not os.path.exists(csv_file):
            print(f"找不到對應的 CSV 檔案: {csv_file}，跳過 {folder_name}")
            continue

        # 讀取 CSV 檔案
        df = pd.read_csv(csv_file)
        df['Filename'] = df['Filename'].str.strip()
        frame_data = {row['Filename']: row for _, row in df.iterrows()}

        # 讀取影像檔案列表
        image_files = sorted([f for f in os.listdir(image_folder) if f.endswith('.png')])
        if not image_files:
            print(f"資料夾 {image_folder} 中找不到影像檔案，跳過")
            continue

        # 確認最後一個時間點的座標資料
        last_time_point = image_files[-1]
        last_coord = frame_data.get(last_time_point)
        if last_coord is None:
            print(f"找不到 {last_time_point} 對應的座標資料，跳過 {folder_name}")
            continue

        # 準備儲存資料的列表
        data_entries = []

        # 處理資料
        for i in range(0, len(image_files) - 3, 3):
            img_file_t1 = image_files[i]
            img_file_t2 = image_files[i + 3]

            # 儲存影像
            img_t1_path = os.path.join(image_folder, img_file_t1)
            img_t2_path = os.path.join(image_folder, img_file_t2)

            if not os.path.exists(img_t1_path) or not os.path.exists(img_t2_path):
                continue

            img_t1 = Image.open(img_t1_path).resize((224, 224))
            img_t2 = Image.open(img_t2_path).resize((224, 224))
            img_t1.save(os.path.join(output_folder, 'ft1', img_file_t1))
            img_t2.save(os.path.join(output_folder, 'ft2', img_file_t2))

            # 座標資料
            coord_t1 = frame_data.get(img_file_t1)
            coord_t2 = frame_data.get(img_file_t2)

            if coord_t1 is not None and coord_t2 is not None:
                at1 = [coord_t1['X (mm)'] - last_coord['X (mm)'],
                       coord_t1['Y (mm)'] - last_coord['Y (mm)'],
                       coord_t1['Z (mm)'] - last_coord['Z (mm)'],
                       coord_t1['Roll (deg)'] - last_coord['Roll (deg)'],
                       coord_t1['Pitch (deg)'] - last_coord['Pitch (deg)'],
                       coord_t1['Yaw (deg)'] - last_coord['Yaw (deg)']]

                at2 = [coord_t2['X (mm)'] - last_coord['X (mm)'],
                       coord_t2['Y (mm)'] - last_coord['Y (mm)'],
                       coord_t2['Z (mm)'] - last_coord['Z (mm)'],
                       coord_t2['Roll (deg)'] - last_coord['Roll (deg)'],
                       coord_t2['Pitch (deg)'] - last_coord['Pitch (deg)'],
                       coord_t2['Yaw (deg)'] - last_coord['Yaw (deg)']]

                delta = [at2[i] - at1[i] for i in range(6)]

                entry = {
                    "frame_t1": os.path.splitext(img_file_t1)[0],
                    "frame_t2": os.path.splitext(img_file_t2)[0],
                    "ft1_image_path": f"ft1\\{img_file_t1}",
                    "ft2_image_path": f"ft2\\{img_file_t2}",
                    "at1_6dof": at1,
                    "action_change_6dof": delta,
                    "at2_6dof": at2
                }
                data_entries.append(entry)

        # 儲存為 JSON 檔案
        with open(output_json_path, 'w') as f:
            json.dump(data_entries, f, indent=2)

        print(f"已儲存 JSON 檔案到 {output_json_path}")
