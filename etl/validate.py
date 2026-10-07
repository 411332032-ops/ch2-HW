# -*- coding: utf-8 -*-
import pandas as pd

def run():
    df_d = pd.read_csv('output/cleaned_taipei_districts.csv')
    s15 = df_d['15-64歲總計'].sum()
    s65 = df_d['65歲以上總計'].sum()
    
    df_m = pd.read_csv('output/cleaned_marital_trends.csv')
    df_m['Calc'] = df_m['Unmarried'] + df_m['Married'] + df_m['Divorced'] + df_m['Widowed']
    m_pass = (df_m['Total_Population'] == df_m['Calc']).all()
    
    # 抽查：核對民國63年總計是否為 10,159,777
    row_63 = df_m[df_m['ROC_Year'] == '民國63年']
    val_63 = row_63['Total_Population'].values[0] if not row_63.empty else 0
    spot_check_63 = (val_63 == 10159777)
    
    log = [
        "=== Checksum Validation Log ===",
        f"15-64加總核對: {s15:,} -> {'PASS' if s15==1609966 else 'FAIL'}",
        f"65以上加總核對: {s65:,} -> {'PASS' if s65==576507 else 'FAIL'}",
        f"婚姻狀況明細核對: -> {'PASS' if m_pass else 'FAIL'}",
        f"抽查民國63年總計 ({val_63:,}): -> {'PASS' if spot_check_63 else 'FAIL'}"
    ]
    
    with open('etl/validation_log.txt', 'w', encoding='utf-8') as l_f:
        l_f.write('\n'.join(log))
    print("✅ validate.py 執行成功，抽查紀錄已寫入 etl/validation_log.txt")

if __name__ == '__main__':
    run()