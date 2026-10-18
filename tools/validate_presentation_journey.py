import json
from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
import os
os.chdir(ROOT)
at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
steps=[]
def check(label):
 assert not at.exception,[e.message for e in at.exception]
 steps.append(label)
def click(key):
 at.button(key=key).click().run();check(key)
check('home');click('start_CASE-BURGLARY');click('start_investigation');click('investigate_cctv');click('analyze_cctv_yolo_CASE-BURGLARY')
keys=[b.key for b in at.button if b.key and b.key.startswith('collect_cctv_yolo_')]
assert keys
click(keys[0]);click('find_cctv_evidence');click('investigate_witness');click('collect_witness_evidence')
assert len(at.session_state.collected_evidence)>=3
at.text_area(key='hypothesis_input').set_value('시각 단서와 진술을 대조하고 실제 통계의 집계 범위를 확인해야 한다.').run();check('hypothesis input');click('save_hypothesis')
at.text_area(key='final_deduction_input').set_value('관찰된 물체는 증거 후보이며 범죄 사실을 단정할 수 없다. 지역 통계는 발생건수로 해석한다.').run();check('deduction input');click('submit_final_deduction')
assert at.session_state.case_submitted
texts='\n'.join(x.value for typ in ['subheader','caption','success','markdown'] for x in getattr(at,typ))
assert 'REAL DATA UNLOCKED' in texts and 'SAFETY LAB' in texts
print('Full journey passed',steps)
Path('docs/presentation/validation.json').write_text(json.dumps({'workflow':'Streamlit AppTest real button and text inputs','passed_steps':steps,'evidence_count':len(at.session_state.collected_evidence),'real_data_unlocked':True,'safety_lab_rendered':True,'limitations':['One representative burglary case, not all cases or all states','No education-effect or YOLO accuracy benchmark']},ensure_ascii=False,indent=2)+'\n')
