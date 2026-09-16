from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "crime"

FILES = [
    "132_DT_13204_2011_N212_20260915162627.csv",
    "132_DT_13204_2011_N213_20260915163035.csv",
]

for filename in FILES:

    path = RAW_DIR / filename

    df = pd.read_csv(
        path,
        encoding="cp949",
        low_memory=False
    )

    print("\n" + "=" * 80)
    print(filename)
    print("=" * 80)

    # -----------------------------
    # 기본 정보
    # -----------------------------
    print(f"\n행 수 : {len(df)}")
    print(f"열 수 : {len(df.columns)}")

    # -----------------------------
    # 죄종별 확인
    # -----------------------------
    crime_values = (
        df["죄종별"]
        .dropna()
        .astype(str)
        .unique()
    )

    print("\n[죄종별 고유값 수]")
    print(len(crime_values))

    print("\n[죄종별 앞 100개]")
    for i, value in enumerate(crime_values[:100], start=1):
        print(f"{i:03d}: {value}")

    # -----------------------------
    # 항목 확인
    # -----------------------------
    item_values = (
        df["항목"]
        .dropna()
        .astype(str)
        .unique()
    )

    print("\n[항목]")
    for value in item_values:
        print("-", value)

    # -----------------------------
    # 총계만 확인
    # -----------------------------
    total = df[
        df["죄종별"].astype(str).str.contains(
            "총계|총범죄",
            na=False
        )
    ]

    print("\n[총계 관련 앞 15행]")
    print(total.head(15).to_string(index=False))