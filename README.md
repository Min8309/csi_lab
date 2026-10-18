# CSI LAB

**범죄율을 올바르게 이해하고, 범죄 데이터의 패턴을 읽는 교육 프로젝트**

가상 사건을 조사하며 증거를 모으고, 실제 범죄 통계를 비교한 뒤 근거를 설명하는 경험을 제공합니다.

**CASE → EVIDENCE → AI → DATA → PREVENTION**

- 4개 CASE: 심야의 침입자 · 사라진 가방 · 불길 속의 흔적 · 의문의 거래
- 관찰과 추론: CCTV·물체·시간·목격자·지역 데이터·과거 기록 조사, 가설과 최종 추리 작성
- 실제 데이터: 지역·범죄·연도 선택과 장기 시계열 탐색
- Safety LAB: 범죄 유형별 일반 예방 행동 안내

서비스: https://csilab-kr.streamlit.app/
----
[CSI_LAB_교육프로젝트_전면개편.pptx](https://github.com/user-attachments/files/33614795/CSI_LAB_._.pptx)

## 새 발표 자료

첨부 참고자료는 구성과 설명 수준만 참고하고, 내용·수치·핵심 코드는 이 저장소에서 확인해 전면 개편했습니다.

- [편집 가능한 PPT · 42장](docs/presentation/CSI_LAB_교육프로젝트_전면개편.pptx)
- [PDF 미리보기](docs/presentation/CSI_LAB_교육프로젝트_전면개편.pdf)
- [발표 원고·핵심 코드 20곳·원본 근거](docs/presentation/발표원고_근거.md)
- [제작·검증·데이터 범위 안내](docs/presentation/README.md)


## 지표를 읽는 기준

현재 앱의 지역 지표는 **발생건수**입니다. 인구 보정 범죄율 계산은 아직 구현되어 있지 않습니다. 범죄율의 의미와 분모를 이해하는 것이 교육 목표이며, 발생건수만으로 지역의 안전·위험 순위를 판단하지 않습니다.

- YOLO는 이미지의 물체를 관찰합니다. 범인·범죄 여부를 판단하지 않습니다.
- CASE SCORE는 활동 진행도입니다. 추리의 정확성을 자동 평가하지 않습니다.
- 가상 사건 정보와 실제 집계 통계는 구분합니다.
- 장기 시계열은 1990–2022년, 지역 최종 CSV의 실제 보관 기간은 **2011–2024년**입니다. 지역 파일명에 포함된 1994–2024와 실제 범위가 다릅니다.
- 학습 효과·탐지 정확도·위험 예측 성능을 검증한 수치는 제시하지 않습니다.
-----------------------------------
<img width="1338" height="706" alt="image" src="https://github.com/user-attachments/assets/6d0c50e4-8fce-432e-9131-c6d2af45e64e" />
<img width="1346" height="685" alt="image" src="https://github.com/user-attachments/assets/b65e9101-3eb4-4d15-af53-691fdbf298da" />
<img width="1348" height="673" alt="image" src="https://github.com/user-attachments/assets/af91164a-14db-4094-9a8f-80987e00c96d" />
<img width="1328" height="677" alt="image" src="https://github.com/user-attachments/assets/bd4e76e0-2cf1-4518-9998-9440cd8772c2" />
<img width="1332" height="673" alt="image" src="https://github.com/user-attachments/assets/c34cd41d-31c9-4e33-93d7-a4ea800acfdb" />
<img width="1285" height="682" alt="image" src="https://github.com/user-attachments/assets/ad9237a4-6847-4993-8c99-42dca10bd169" />
<img width="1360" height="680" alt="image" src="https://github.com/user-attachments/assets/fcecccb2-bbd2-4303-9aa5-a5d44b4e4f7c" />
<img width="1334" height="663" alt="image" src="https://github.com/user-attachments/assets/886caf3b-025c-40ce-9d46-b8c98c3b2621" />





<img width="884" height="442" alt="image" src="https://github.com/user-attachments/assets/73ae8051-8d83-4718-ae57-66b90eaaed46" />



