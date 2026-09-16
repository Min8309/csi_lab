
from pathlib import Path
import pandas as pd
import re

# =========================================================
# 경로 설정
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "crime"
PROCESSED_DIR = BASE_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# 사용할 파일
# =========================================================

FILES = [
    {
        "filename": "132_TX_132_2009_H1003_20260915164522.csv",
        "encoding": "cp949",
        "period": "1990-2010"
    },
    {
        "filename": "132_DT_13204_2011_N213_20260915163035.csv",
        "encoding": "cp949",
        "period": "2011-2022"
    }
]


# =========================================================
# 숫자 변환 함수
# =========================================================

def clean_number(value):

    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    if value in ["-", "", "nan", "NaN"]:
        return pd.NA

    value = value.replace(",", "")

    try:
        return float(value)

    except ValueError:
        return pd.NA


# =========================================================
# 항목 이름 표준화
# =========================================================

def standardize_item(item):

    item = str(item).replace(" ", "")

    if "발생건수" in item:
        return "occurrence_count"

    if "검거건수" in item:
        return "arrest_count"

    if "검거율" in item:
        return "clearance_rate"

    if "발생건수대비검거건수" in item:
        return "clearance_rate"

    return None


# =========================================================
# 파일 전처리 함수
# =========================================================

def process_file(info):

    path = RAW_DIR / info["filename"]

    print("\n" + "=" * 80)
    print("처리 중:", info["filename"])
    print("=" * 80)

    df = pd.read_csv(
        path,
        encoding=info["encoding"],
        low_memory=False
    )

    # Unnamed 컬럼 제거
    df = df.loc[
        :,
        ~df.columns.astype(str).str.startswith("Unnamed")
    ]

    # 분석에 필요한 항목만 선택
    df["metric"] = df["항목"].apply(standardize_item)

    df = df[df["metric"].notna()].copy()

    # 연도 컬럼 찾기
    year_columns = []

    for col in df.columns:

        match = re.search(r"(19|20)\d{2}", str(col))

        if match:
            year_columns.append(col)

    print("연도 컬럼 수:", len(year_columns))

    # Wide → Long
    long_df = df.melt(
        id_vars=["죄종별", "metric"],
        value_vars=year_columns,
        var_name="year_raw",
        value_name="value"
    )

    # 연도 추출
    long_df["year"] = (
        long_df["year_raw"]
        .astype(str)
        .str.extract(r"((?:19|20)\d{2})")[0]
    )

    long_df["year"] = pd.to_numeric(
        long_df["year"],
        errors="coerce"
    ).astype("Int64")

    # 숫자 정리
    long_df["value"] = long_df["value"].apply(clean_number)

    # 필요없는 행 제거
    long_df = long_df[
        long_df["year"].notna()
    ].copy()

    # 죄종명 정리
    long_df["crime_type"] = (
        long_df["죄종별"]
        .astype(str)
        .str.strip()
    )

    # Pivot
    result = long_df.pivot_table(
        index=[
            "year",
            "crime_type"
        ],
        columns="metric",
        values="value",
        aggfunc="first"
    ).reset_index()

    result.columns.name = None

    # 없는 컬럼 생성
    for col in [
        "occurrence_count",
        "arrest_count",
        "clearance_rate"
    ]:
        if col not in result.columns:
            result[col] = pd.NA

    # 출처 기록
    result["source_file"] = info["filename"]
    result["source_period"] = info["period"]

    return result


# =========================================================
# 전체 처리
# =========================================================

all_data = []

for info in FILES:

    result = process_file(info)

    all_data.append(result)


final = pd.concat(
    all_data,
    ignore_index=True
)


# =========================================================
# CSI LAB용 컬럼 추가
# =========================================================

final["region"] = "범위확인필요"

final["data_role"] = "TIME_MACHINE"


# =========================================================
# 컬럼 순서
# =========================================================

final = final[
    [
        "year",
        "region",
        "crime_type",
        "occurrence_count",
        "arrest_count",
        "clearance_rate",
        "source_period",
        "source_file",
        "data_role"
    ]
]


# =========================================================
# 정렬
# =========================================================

final = final.sort_values(
    ["year", "crime_type"]
).reset_index(drop=True)


# =========================================================
# 저장
# =========================================================

OUTPUT = (
    PROCESSED_DIR
    / "occurrence_arrest_1990_2022.csv"
)

final.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# 결과 확인
# =========================================================

print("\n" + "=" * 80)
print("CSI LAB - 발생·검거 표준화 완료")
print("=" * 80)

print("\n데이터 크기:")
print(final.shape)

print("\n연도 범위:")
print(
    final["year"].min(),
    "~",
    final["year"].max()
)

print("\n컬럼:")
print(final.columns.tolist())

print("\n앞 20행:")
print(final.head(20).to_string(index=False))

print("\n연도별 행 수:")
print(
    final.groupby("year")
    .size()
    .head(40)
)

print("\n저장 위치:")
print(OUTPUT)