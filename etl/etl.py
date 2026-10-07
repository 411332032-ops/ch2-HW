# -*- coding: utf-8 -*-
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
