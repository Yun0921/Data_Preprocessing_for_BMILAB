import os
import pandas as pd
from PIL import Image

# 設定影像資料夾和 CSV 檔案的路徑
image_folder = 'frames_0506_1'  # 替換為你的影像資料夾路徑
csv_file = '0506_1_final_data.csv'  # 替換為你的 CSV 檔案路徑
output_folder = 'data_0506_1'  # 設定你希望保存輸出的資料夾路徑

# 確保輸出資料夾存在
folders = ['ft1', 'ft2', 'at1', 'at2', 'at1_to_at2']
for folder in folders:
    output_path = os.path.join(output_folder, folder)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

# 讀取 CSV 檔案
df = pd.read_csv(csv_file)
df['Filename'] = df['Filename'].str.strip()  # 去除可能的空白字元
frame_data = {row['Filename']: row for _, row in df.iterrows()}

# 讀取影像檔案列表
image_files = sorted([f for f in os.listdir(image_folder) if f.endswith('.png')])

# 確認最後一個時間點的座標資料
last_time_point = image_files[-1]
last_coord = frame_data[last_time_point]  # 取得最後一個時間點的座標

# 計算並保存資料
for i in range(0, len(image_files) - 3, 3):
    # 取 t1, t2 時的影像檔案
    img_file_t1 = image_files[i]
    img_file_t2 = image_files[i + 3]

    # 讀取影像
    img_t1 = Image.open(os.path.join(image_folder, img_file_t1))
    img_t2 = Image.open(os.path.join(image_folder, img_file_t2))

    # 存儲 ft1, ft2 影像
    img_t1.save(os.path.join(output_folder, 'ft1', img_file_t1))
    img_t2.save(os.path.join(output_folder, 'ft2', img_file_t2))

    # 取得 t1 和 t2 的座標資料
    coord_t1 = frame_data.get(img_file_t1, None)
    coord_t2 = frame_data.get(img_file_t2, None)

    if coord_t1 is not None and coord_t2 is not None:
        # 計算相對於最後一個時間點的座標 (原點)
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

        # 存儲 at1 和 at2 為 CSV 格式
        at1_df = pd.DataFrame([at1], columns=["X (mm)", "Y (mm)", "Z (mm)", "Roll (deg)", "Pitch (deg)", "Yaw (deg)"])
        at2_df = pd.DataFrame([at2], columns=["X (mm)", "Y (mm)", "Z (mm)", "Roll (deg)", "Pitch (deg)", "Yaw (deg)"])

        at1_df.to_csv(os.path.join(output_folder, 'at1', f'{img_file_t1}.csv'), index=False)
        at2_df.to_csv(os.path.join(output_folder, 'at2', f'{img_file_t2}.csv'), index=False)

        # 計算 at1 -> at2（相對變化）
        at1_to_at2 = [at2[i] - at1[i] for i in range(3)] + [at2[i] - at1[i] for i in range(3, 6)]

        # 存儲 at1 -> at2 為 CSV 格式
        at1_to_at2_df = pd.DataFrame([at1_to_at2], columns=["X Change (mm)", "Y Change (mm)", "Z Change (mm)", "Roll Change (deg)", "Pitch Change (deg)", "Yaw Change (deg)"])
        at1_to_at2_df.to_csv(os.path.join(output_folder, 'at1_to_at2', f'{img_file_t1}_to_{img_file_t2}.csv'), index=False)

print("資料處理完成，已生成對應的資料夾和 CSV 檔案。")
