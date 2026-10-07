# -*- coding: utf-8 -*-
import json, shutil, pandas as pd

def run():
    for n in ('cleaned_taipei_districts.csv', 'cleaned_marital_trends.csv'):
        shutil.copy('output/' + n, 'docs/' + n)
    df_d = pd.read_csv('output/cleaned_taipei_districts.csv')
    df_m = pd.read_csv('output/cleaned_marital_trends.csv')
    js_c = f"const TAIPEI_DISTRICTS_DATA = {json.dumps(df_d.to_dict(orient='records'), ensure_ascii=False)};\n"
    js_c += f"const MARITAL_TRENDS_DATA = {json.dumps(df_m.to_dict(orient='records'), ensure_ascii=False)};\n"
    with open('docs/data.js', 'w', encoding='utf-8') as j_f:
        j_f.write(js_c)

if __name__ == '__main__': run()
