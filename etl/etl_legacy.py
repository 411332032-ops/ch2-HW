# -*- coding: utf-8 -*-
"""
====================================================================
ETL Data Processing & Verification Script
專案名稱：臺北市人口結構與15歲以上婚姻狀況統計
評分對應：
1. 自動處理髒資料（千分號去除、去除空白、跨列標頭解析）
2. 數據核對驗證 (Checksum Validation)：驗證分區加總是否等於總計
====================================================================
"""
import pandas as pd
import json

def process_and_validate():
    print("=== [ETL Step 1] 讀取並處理臺北市行政區人口資料 ===")
    # 讀取原始 CSV (處理千分位逗號與空白)
    raw_csv = pd.read_csv('全國人口資料庫統計地圖.csv', encoding='utf-8')
    raw_csv['15-64歲總計'] = raw_csv['15-64歲總計'].astype(str).str.replace(',', '').str.strip().astype(int)
    raw_csv['65歲以上總計'] = raw_csv['65歲以上總計'].astype(str).str.replace(',', '').str.strip().astype(int)
    
    # 拆分行政區與宣告總計
    districts = raw_csv[raw_csv['區域別'] != '總計'].copy()
    reported_total = raw_csv[raw_csv['區域別'] == '總計'].iloc[0]
    
    # 數據加總核對驗證 (Checksum Verification)
    calc_15_64 = districts['15-64歲總計'].sum()
    calc_65_plus = districts['65歲以上總計'].sum()
    
    check_15_64 = (calc_15_64 == reported_total['15-64歲總計'])
    check_65_plus = (calc_65_plus == reported_total['65歲以上總計'])
    
    print(f"  > 15-64歲加總驗證: 計算值={calc_15_64:,} | 宣告值={reported_total['15-64歲總計']:,} -> {'[成功]' if check_15_64 else '[失敗]'}")
    print(f"  > 65歲以上加總驗證: 計算值={calc_65_plus:,} | 宣告值={reported_total['65歲以上總計']:,} -> {'[成功]' if check_65_plus else '[失敗]'}")
    
    # 計算衍生洞察指標：總人口、高齡人口比例(%)
    districts['15歲以上總人口'] = districts['15-64歲總計'] + districts['65歲以上總計']
    districts['高齡人口比例(%)'] = (districts['65歲以上總計'] / districts['15歲以上總人口'] * 100).round(2)
    
    # 匯出乾淨 CSV
    districts.to_csv('cleaned_taipei_districts.csv', index=False, encoding='utf-8-sig')
    print("  ✓ 已匯出 cleaned_taipei_districts.csv")

    print("\n=== [ETL Step 2] 讀取並處理歷年婚姻狀況 XLS 資料 ===")
    df_xls = pd.read_excel('十五歲以上人口婚姻狀況(63).xls')
    
    records = []
    current_roc_year = None
    
    for idx, row in df_xls.iterrows():
        val0 = str(row.iloc[0])
        if '民國' in val0:
            current_roc_year = val0.strip()
        
        gender = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
        if gender == '計' and current_roc_year:
            roc_num = int(current_roc_year.replace('民國', '').replace('年', ''))
            records.append({
                'ROC_Year': current_roc_year,
                'AD_Year': roc_num + 1911,
                'Total_Population': int(row.iloc[3]),
                'Unmarried': int(row.iloc[4]),
                'Married': int(row.iloc[5]),
                'Divorced': int(row.iloc[8]),
                'Widowed': int(row.iloc[11])
            })
            
    df_marital = pd.DataFrame(records)
    
    # 數據核對驗證：未婚+有偶+離婚+喪偶 == 總人口
    df_marital['Calculated_Total'] = df_marital['Unmarried'] + df_marital['Married'] + df_marital['Divorced'] + df_marital['Widowed']
    df_marital['Check_Passed'] = (df_marital['Total_Population'] == df_marital['Calculated_Total'])
    
    print(f"  > 歷年婚姻狀況明細加總核對: {'[全部符合]' if df_marital['Check_Passed'].all() else '[發現異常]'}")
    
    # 匯出乾淨 CSV
    df_marital.to_csv('cleaned_marital_trends.csv', index=False, encoding='utf-8-sig')
    print("  ✓ 已匯出 cleaned_marital_trends.csv")
    print("\n=== ETL 流程全部完成 ===")

if __name__ == '__main__':
    process_and_validate()