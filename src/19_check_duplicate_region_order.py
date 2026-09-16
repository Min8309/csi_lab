from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "crime"

FILE = RAW_DIR / "135_TX_13501_A048_20260915163423.csv"

df = pd.read_csv(FILE, encoding="cp949")

# 절도만 선택하면 지역 순서를 보기 편함
test = df[
    df["범죄별"].astype(str).str.strip() == "절도"
].copy()

test = test.reset_index()

print("=" * 80)
print("절도 데이터의 발생지 원본 순서")
print("=" * 80)

print(
    test[
        ["index", "범죄별", "발생지별"]
    ].to_string(index=False)
)

print("\n" + "=" * 80)
print("'강서'가 등장하는 위치")
print("=" * 80)

gangseo = test[
    test["발생지별"].astype(str).str.strip() == "강서"
]

print(
    gangseo[
        ["index", "범죄별", "발생지별"]
    ].to_string(index=False)
)

print("\n강서 개수:", len(gangseo))