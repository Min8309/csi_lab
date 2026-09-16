from pathlib import Path
import pandas as pd
import re


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "crime"
PROCESSED_DIR = BASE_DIR / "processed"

FILES = [
    "135_TX_13501_A048_20260915163423.csv",  # 1994~2010
    "135_TX_13501_A048_20260915163340.csv",  # 2011~2024
]

OUTPUT = PROCESSED_DIR / "region_crime_1994_2024.csv"


def read_csv_auto(path):

    for encoding in [
        "utf-8-sig",
        "utf-8",
        "cp949",
        "euc-kr"
    ]:
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError(f"읽기 실패: {path.name}")


def get_year_columns(df):

    result = {}

    for col in df.columns:

        text = str(col).replace(" ", "")

        match = re.fullmatch(
            r"(\d{4})년",
            text
        )

        if match:
            result[col] = int(match.group(1))

    return result


frames = []


for file_name in FILES:

    path = RAW_DIR / file_name

    df = read_csv_auto(path)

    year_map = get_year_columns(df)

    print("\n" + "=" * 80)
    print("파일:", file_name)
    print("연도:", sorted(year_map.values()))

    temp = df[
        ["범죄별", "발생지별"]
        + list(year_map.keys())
    ].copy()

    temp = temp.melt(
        id_vars=[
            "범죄별",
            "발생지별"
        ],
        value_vars=list(year_map.keys()),
        var_name="year_column",
        value_name="occurrence_count"
    )

    temp["year"] = (
        temp["year_column"]
        .map(year_map)
    )

    temp = temp.rename(
        columns={
            "범죄별": "crime_type_original",
            "발생지별": "region_original"
        }
    )

    temp["crime_type_original"] = (
        temp["crime_type_original"]
        .astype(str)
        .str.strip()
    )

    temp["region_original"] = (
        temp["region_original"]
        .astype(str)
        .str.strip()
    )

    temp["occurrence_count"] = pd.to_numeric(
        temp["occurrence_count"],
        errors="coerce"
    )

    temp["source_file"] = file_name

    temp = temp.drop(
        columns="year_column"
    )

    frames.append(temp)


# =========================================================
# 두 기간 연결
# =========================================================

result = pd.concat(
    frames,
    ignore_index=True
)


# =========================================================
# 기본 검증
# =========================================================

result = result[
    result["crime_type_original"].ne("")
    &
    result["region_original"].ne("")
].copy()


# 동일 연도 + 지역 + 범죄 중복 검사
key = [
    "year",
    "region_original",
    "crime_type_original"
]

result["duplicate_key"] = (
    result.duplicated(
        subset=key,
        keep=False
    )
)


# =========================================================
# 정렬
# =========================================================

result = (
    result
    .sort_values(
        [
            "crime_type_original",
            "region_original",
            "year"
        ]
    )
    .reset_index(drop=True)
)


# =========================================================
# 저장
# =========================================================

result.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# 결과 확인
# =========================================================

print("\n" + "=" * 80)
print("CSI LAB 지역 범죄 데이터 완성")
print("=" * 80)

print("\n데이터 크기:")
print(result.shape)

print("\n연도 범위:")
print(
    result["year"].min(),
    "~",
    result["year"].max()
)

print("\n연도 개수:")
print(
    result["year"].nunique()
)

print("\n지역 수:")
print(
    result["region_original"].nunique()
)

print("\n범죄 종류 수:")
print(
    result["crime_type_original"].nunique()
)

print("\n중복 KEY 행:")
print(
    result["duplicate_key"].sum()
)


# =========================================================
# 연도 연속성
# =========================================================

years = sorted(
    result["year"]
    .dropna()
    .unique()
)

expected = list(
    range(
        int(min(years)),
        int(max(years)) + 1
    )
)

missing_years = sorted(
    set(expected) - set(years)
)

print("\n누락 연도:")
print(missing_years)


# =========================================================
# 주요 CSI 범죄 확인
# =========================================================

CORE = [
    "살인",
    "강도",
    "강간",
    "절도",
    "사기",
    "방화",
    "상해",
    "협박",
    "공갈"
]

print("\n" + "=" * 80)
print("CSI 주요 범죄 지역 시계열")
print("=" * 80)

for crime in CORE:

    sample = result[
        result["crime_type_original"] == crime
    ]

    if sample.empty:

        print(
            f"{crime:10s} : 데이터 없음"
        )

    else:

        print(
            f"{crime:10s} : "
            f"{sample['year'].min()}~"
            f"{sample['year'].max()} / "
            f"{sample['year'].nunique()}년 / "
            f"{sample['region_original'].nunique()}지역"
        )


# =========================================================
# 용산 절도 확인
# =========================================================

print("\n" + "=" * 80)
print("TEST : 용산 × 절도")
print("=" * 80)

test = result[
    (result["region_original"] == "용산")
    &
    (result["crime_type_original"] == "절도")
][
    [
        "year",
        "occurrence_count"
    ]
]

print(
    test.to_string(index=False)
)


print("\n저장 완료:")
print(OUTPUT)
