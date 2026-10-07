# -*- coding: utf-8 -*-
import os, json, pandas as pd

# 1. 自動產生 etl/etl.py
os.makedirs('etl', exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('docs', exist_ok=True)

with open('etl/etl.py', 'w', encoding='utf-8') as f:
    f.write('''# -*- coding: utf-8 -*-
import os, pandas as pd

def run():
    os.makedirs('output', exist_ok=True)
    # 處理分區人口
    csv_p = 'Data/補充資料/全國人口資料庫統計地圖.csv'
    if not os.path.exists(csv_p): csv_p = 'Data/補充資料/全國人口資料庫統計地圖_2.csv'
    df_csv = pd.read_csv(csv_p, encoding='utf-8')
    df_csv['15-64歲總計'] = df_csv['15-64歲總計'].astype(str).str.replace(',', '').str.strip().astype(int)
    df_csv['65歲以上總計'] = df_csv['65歲以上總計'].astype(str).str.replace(',', '').str.strip().astype(int)
    districts = df_csv[df_csv['區域別'] != '總計'].copy()
    districts['15歲以上總人口'] = districts['15-64歲總計'] + districts['65歲以上總計']
    districts['高齡人口比例(%)'] = (districts['65歲以上總計'] / districts['15歲以上總人口'] * 100).round(2)
    districts.to_csv('output/cleaned_taipei_districts.csv', index=False, encoding='utf-8-sig')

    # 處理婚姻狀況
    xls_p = 'Data/十五歲以上人口婚姻狀況(63).xls'
    if not os.path.exists(xls_p): xls_p = 'Data/十五歲以上人口婚姻狀況(63)_2.xls'
    df_xls = pd.read_excel(xls_p)
    records, yr = [], None
    for _, row in df_xls.iterrows():
        v0 = str(row.iloc[0])
        if '民國' in v0: yr = v0.strip()
        g = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
        if g == '計' and yr:
            r_num = int(yr.replace('民國', '').replace('年', ''))
            records.append({'ROC_Year': yr, 'AD_Year': r_num + 1911, 'Total_Population': int(row.iloc[3]),
                            'Unmarried': int(row.iloc[4]), 'Married': int(row.iloc[5]),
                            'Divorced': int(row.iloc[8]), 'Widowed': int(row.iloc[11])})
    pd.DataFrame(records).to_csv('output/cleaned_marital_trends.csv', index=False, encoding='utf-8-sig')

if __name__ == '__main__': run()
''')

# 2. 自動產生 etl/validate.py
with open('etl/validate.py', 'w', encoding='utf-8') as f:
    f.write('''# -*- coding: utf-8 -*-
import pandas as pd

def run():
    df_d = pd.read_csv('output/cleaned_taipei_districts.csv')
    s15 = df_d['15-64歲總計'].sum()
    s65 = df_d['65歲以上總計'].sum()
    df_m = pd.read_csv('output/cleaned_marital_trends.csv')
    df_m['Calc'] = df_m['Unmarried'] + df_m['Married'] + df_m['Divorced'] + df_m['Widowed']
    m_pass = (df_m['Total_Population'] == df_m['Calc']).all()
    
    log = [
        "=== Checksum Validation Log ===",
        f"15-64加總核對: {s15} -> {'PASS' if s15==1609966 else 'FAIL'}",
        f"65以上加總核對: {s65} -> {'PASS' if s65==576507 else 'FAIL'}",
        f"婚姻狀況明細核對: -> {'PASS' if m_pass else 'FAIL'}"
    ]
    with open('etl/validation_log.txt', 'w', encoding='utf-8') as l_f:
        l_f.write('\\n'.join(log))

if __name__ == '__main__': run()
''')

# 3. 自動產生 etl/build_data.py
with open('etl/build_data.py', 'w', encoding='utf-8') as f:
    f.write('''# -*- coding: utf-8 -*-
import json, shutil, pandas as pd

def run():
    for n in ('cleaned_taipei_districts.csv', 'cleaned_marital_trends.csv'):
        shutil.copy('output/' + n, 'docs/' + n)
    df_d = pd.read_csv('output/cleaned_taipei_districts.csv')
    df_m = pd.read_csv('output/cleaned_marital_trends.csv')
    js_c = f"const TAIPEI_DISTRICTS_DATA = {json.dumps(df_d.to_dict(orient='records'), ensure_ascii=False)};\\n"
    js_c += f"const MARITAL_TRENDS_DATA = {json.dumps(df_m.to_dict(orient='records'), ensure_ascii=False)};\\n"
    with open('docs/data.js', 'w', encoding='utf-8') as j_f:
        j_f.write(js_c)

if __name__ == '__main__': run()
''')

# 4. 自動產生 README.md
with open('README.md', 'w', encoding='utf-8') as f:
    f.write('''# 臺北市人口結構與 15 歲以上人口婚姻狀況統計儀表板

👉 **線上展示網站**：[https://411332032-ops.github.io/ch2-HW/](https://411332032-ops.github.io/ch2-HW/)

## 📂 專案結構
- `Data/`: 原始資料檔與參考圖片
- `docs/`: 網頁呈現與轉檔數據 (`index.html`, `data.js`)
- `etl/`: 資料清理、自動驗證與轉檔腳本
- `output/`: 清理後匯出之 CSV 數據
''')

# 5. 立即執行產生的腳本
import etl.etl as e, etl.validate as v, etl.build_data as b
e.run()
v.run()
b.run()

print("所有檔案、程式碼、資料夾架構已全部自動產生完畢！")