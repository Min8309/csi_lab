from pathlib import Path
import pandas as pd
import re


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "crime"

FILE1 = RAW_DIR / "135_TX_13501_A048_20260915163340.csv"
FILE2 = RAW_DIR / "135_TX_13501_A048_20260915163423.csv"


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


def find_years(df):

    years = {}

    for col in df.columns:

        text = str(col).replace(" ", "")

        match = re.fullmatch(
            r"(\d{4})년",
            text
        )

        if match:
            years[int(match.group(1))] = col

    return years


df1 = read_csv_auto(FILE1)
df2 = read_csv_auto(FILE2)

years1 = find_years(df1)
years2 = find_years(df2)

print("=" * 80)
print("연도 비교")
print("=" * 80)

print("파일 1 연도:")
print(sorted(years1.keys()))

print("\n파일 2 연도:")
print(sorted(years2.keys()))

print("\n파일 1에만 있는 연도:")
print(sorted(set(years1) - set(years2)))

print("\n파일 2에만 있는 연도:")
print(sorted(set(years2) - set(years1)))


# =========================================================
# 공통 범죄 / 공통 지역
# =========================================================

common_regions = (
    set(df1["발생지별"].dropna().astype(str).str.strip())
    &
    set(df2["발생지별"].dropna().astype(str).str.strip())
)

common_crimes = (
    set(df1["범죄별"].dropna().astype(str).str.strip())
    &
    set(df2["범죄별"].dropna().astype(str).str.strip())
)

common_years = sorted(
    set(years1) & set(years2)
)


# =========================================================
# 공통 데이터 Long 변환
# =========================================================

def make_long(df, year_columns):

    temp = df.copy()

    temp["범죄별"] = (
        temp["범죄별"]
        .astype(str)
        .str.strip()
    )

    temp["발생지별"] = (
        temp["발생지별"]
        .astype(str)
        .str.strip()
    )

    rows = []

    for year in common_years:

        col = year_columns[year]

        part = temp[
            ["범죄별", "발생지별", col]
        ].copy()

        part["year"] = year

        part = part.rename(
            columns={
                col: "value"
            }
        )

        part["value"] = pd.to_numeric(
            part["value"],
            errors="coerce"
        )

        rows.append(part)

    return pd.concat(
        rows,
        ignore_index=True
    )


long1 = make_long(df1, years1)
long2 = make_long(df2, years2)


long1 = long1[
    long1["범죄별"].isin(common_crimes)
    &
    long1["발생지별"].isin(common_regions)
]

long2 = long2[
    long2["범죄별"].isin(common_crimes)
    &
    long2["발생지별"].isin(common_regions)
]


# =========================================================
# 비교
# =========================================================

merged = long1.merge(
    long2,
    on=[
        "범죄별",
        "발생지별",
        "year"
    ],
    how="inner",
    suffixes=("_file1", "_file2")
)


both_nan = (
    merged["value_file1"].isna()
    &
    merged["value_file2"].isna()
)

same_value = (
    merged["value_file1"]
    .eq(merged["value_file2"])
)

merged["same"] = (
    both_nan | same_value
)

different = merged[
    ~merged["same"]
].copy()


print("\n" + "=" * 80)
print("공통 데이터 값 비교")
print("=" * 80)

print("비교 셀 수:")
print(len(merged))

print("\n값이 같은 셀:")
print(merged["same"].sum())

print("\n값이 다른 셀:")
print(len(different))

print("\n일치율:")

if len(merged):

    print(
        round(
            merged["same"].mean() * 100,
            4
        ),
        "%"
    )


print("\n다른 값 예시:")

print(
    different[
        [
            "범죄별",
            "발생지별",
            "year",
            "value_file1",
            "value_file2"
        ]
    ]
    .head(30)
    .to_string(index=False)
)