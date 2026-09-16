from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "crime"
CLASS_FILE = BASE_DIR / "processed" / "crime_file_classification.csv"


def read_csv_auto(path):
    for enc in ["utf-8-sig", "utf-8", "cp949", "euc-kr"]:
        try:
            return pd.read_csv(
                path,
                encoding=enc,
                low_memory=False
            ), enc
        except Exception:
            continue

    return None, None


# 분류표 읽기
classification = pd.read_csv(
    CLASS_FILE,
    encoding="utf-8-sig"
)

targets = classification[
    classification["데이터분류"] == "발생_검거"
]

print("=" * 80)
print("CSI LAB - 발생·검거 데이터 구조 검사")
print("=" * 80)

print(f"\n대상 파일 수: {len(targets)}개")


for number, filename in enumerate(targets["파일명"], start=1):

    path = RAW_DIR / filename

    df, encoding = read_csv_auto(path)

    print("\n")
    print("=" * 80)
    print(f"[{number}] {filename}")
    print("=" * 80)

    if df is None:
        print("읽기 실패")
        continue

    print(f"인코딩 : {encoding}")
    print(f"크기   : {df.shape}")

    print("\n[전체 컬럼]")
    for i, col in enumerate(df.columns):
        print(f"{i:03d} : {col}")

    print("\n[앞 5행]")
    print(df.head(5).to_string(index=False))

    print("\n[뒤 3행]")
    print(df.tail(3).to_string(index=False))