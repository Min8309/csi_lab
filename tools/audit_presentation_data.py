import pandas as pd, json, hashlib, subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'docs/presentation'
a={'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'data':{},'observations':[]}
for fn in ['occurrence_arrest_1990_2022.csv','real_data_evidence_1990_2022.csv','csi_time_machine_1990_2022.csv','region_crime_final_1994_2024.csv']:
 p=root/'processed'/fn;d=pd.read_csv(p);x={'rows':len(d),'columns':len(d.columns),'year_min':int(d.year.min()),'year_max':int(d.year.max()),'year_count':d.year.nunique(),'missing_occurrence':int(d.occurrence_count.isna().sum()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 for c in ['city','region_full','crime_type_original']: 
  if c in d:x[c+'_unique']=d[c].nunique()
 if 'duplicate_final_key' in d:x.update({'duplicate_rows_actual':int(d.duplicated(['year','city','district','crime_type_original'],keep=False).sum()),'region_match_false':int((~d.region_match).sum()),'source_files':d.source_file.unique().tolist(),'suspect_district_labels':sorted(d.loc[d.district.str.endswith('구구'),'district'].unique().tolist())})
 if 'core_time_machine' in d:x.update({'core_rows':int(d.core_time_machine.sum()),'core_crimes':d.loc[d.core_time_machine,'crime_type_original'].nunique(),'core_years':d.loc[d.core_time_machine].groupby('crime_type_original').year.nunique().to_dict(),'region_labels':d.region.unique().tolist()})
 a['data'][fn]=x
r=pd.read_csv(root/'processed/region_crime_final_1994_2024.csv'); y=r[(r.city=='서울특별시')&(r.district=='용산구')&(r.crime_type_original=='절도')]; a['local_example']=y[['year','occurrence_count']].to_dict('records');a['local_2011_2024_change_pct']=(float(y.loc[y.year==2024,'occurrence_count'].iloc[0])/float(y.loc[y.year==2011,'occurrence_count'].iloc[0])-1)*100;a['local_2024_yoy_pct']=(1105/987-1)*100
a['observations']=['지역 최종 CSV의 실제 기간은 2011–2024. 파일명의 1994–2024와 다름.','20번 지역 생성 스크립트는 파일 루프 밖에서 후속 처리를 수행해 마지막 파일만 frames에 추가하는 구조. 재생성은 하지 않음.','지역 표기 중 중구구 등 구 접미사 중복 존재.','장기 시계열 region 값은 범위확인필요. 원문 집계 지역을 확정하지 않고 전국 통계로 호칭하지 않음.','인구 분모와 범죄율 계산은 현재 앱에 없음.','학습 효과, 탐지 정확도, 추리 정답률은 측정하지 않음.']
(out/'data_audit.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(a,ensure_ascii=False,indent=2))
