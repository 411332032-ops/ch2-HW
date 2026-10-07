# -*- coding: utf-8 -*-
import os
import pandas as pd

def run():
    os.makedirs('output', exist_ok=True)
    
    # 1. 處理臺北市行政區人口數據
    csv_p = 'Data/補充資料/全國人口資料庫統計地圖.csv'
    if not os.path.exists(csv_p): 
        csv_p = 'Data/補充資料/全國人口資料庫統計地圖_2.csv'
        
    df_csv = pd.read_csv(csv_p, encoding='utf-8')
    df_csv['15-64歲總計'] = df_csv['15-64歲總計'].astype(str).str.replace(',', '').str.strip().astype(int)
    df_csv['65歲以上總計'] = df_csv['65歲以上總計'].astype(str).str.replace(',', '').str.strip().astype(int)
    
    districts = df_csv[df_csv['區域別'] != '總計'].copy()
    districts['15歲以上總人口'] = districts['15-64歲總計'] + districts['65歲以上總計']
    districts['高齡人口比例(%)'] = (districts['65歲以上總計'] / districts['15歲以上總人口'] * 100).round(2)
    districts.to_csv('output/cleaned_taipei_districts.csv', index=False, encoding='utf-8-sig')

    # 2. 處理歷年婚姻狀況數據 (使用 bfill 修正年份對齊)
    xls_p = 'Data/十五歲以上人口婚姻狀況(63).xls'
    if not os.path.exists(xls_p): 
        xls_p = 'Data/十五歲以上人口婚姻狀況(63)_2.xls'
        
    df_xls = pd.read_excel(xls_p)
    
    # 關鍵修正：使用 bfill 向向上填補年份，讓「計」列正確對齊下一列的年份文字
    df_xls['ROC_Year'] = df_xls.iloc[:, 0].bfill()
    df_xls['AD_Year'] = df_xls.iloc[:, 1].bfill()
    
    records = []
    for _, row in df_xls.iterrows():
        gender = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
        year_str = str(row['ROC_Year']).strip() if pd.notna(row['ROC_Year']) else ''
        
        if gender == '計' and '民國' in year_str:
            roc_num = int(year_str.replace('民國', '').replace('年', ''))
            records.append({
                'ROC_Year': year_str,
                'AD_Year': int(row['AD_Year']),
                'Total_Population': int(row.iloc[3]),
                'Unmarried': int(row.iloc[4]),
                'Married': int(row.iloc[5]),
                'Divorced': int(row.iloc[8]),
                'Widowed': int(row.iloc[11])
            })
            
    df_marital = pd.DataFrame(records)
    df_marital.to_csv('output/cleaned_marital_trends.csv', index=False, encoding='utf-8-sig')
    print("✅ etl.py 執行成功！")

if __name__ == '__main__':
    run()