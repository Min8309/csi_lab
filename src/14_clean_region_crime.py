from pathlib import Path
import pandas as pd
import re


# =========================================================
# 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "crime"
PROCESSED_DIR = BASE_DIR / "processed"

FILES = [
    "135_TX_13501_A048_20260915163340.csv",
    "135_TX_13501_A048_20260915163423.csv",
]

OUTPUT = (
    PROCESSED_DIR
    / "region_crime_long.csv"
)


# =========================================================
# CSV 자동 읽기
# =========================================================

def read_csv_auto(path):

    for encoding in [
        "utf-8-sig",
        "utf-8",
        "cp949",
        "euc-kr"
    ]:

        try:

            df = pd.read_csv(
                path,
                encoding=encoding
            )

            return df, encoding

        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"인코딩 실패: {path.name}"
    )


# =========================================================
# 연도 컬럼 찾기
# =========================================================

def get_year_columns(df):

    result = {}

    for col in df.columns:

        # "2011 년", "2017년" 모두 처리
        text = str(col).replace(" ", "")

        match = re.fullmatch(
            r"(\d{4})년",
            text
        )

        if match:

            result[col] = int(
                match.group(1)
            )

    return result


# =========================================================
# 파일별 정리
# =========================================================

frames = []

for file_name in FILES:

    path = RAW_DIR / file_name

    df, encoding = read_csv_auto(path)

    print("\n" + "=" * 80)
    print("파일:", file_name)
    print("인코딩:", encoding)
    print("원본 크기:", df.shape)

    year_map = get_year_columns(df)

    print(
        "연도:",
        sorted(year_map.values())
    )


    # -----------------------------------------------------
    # 필요한 컬럼 확인
    # -----------------------------------------------------

    required = [
        "범죄별",
        "발생지별"
    ]

    missing = [
        col
        for col in required
        if col not in df.columns
    ]

    if missing:

        print(
            "필수 컬럼 없음:",
            missing
        )

        continue


    # -----------------------------------------------------
    # Long Format
    # -----------------------------------------------------

    temp = df[
        [
            "범죄별",
            "발생지별"
        ]
        + list(year_map.keys())
    ].copy()


    temp = temp.melt(

        id_vars=[
            "범죄별",
            "발생지별"
        ],

        value_vars=list(
            year_map.keys()
        ),

        var_name="year_column",

        value_name="occurrence_count"
    )


    # -----------------------------------------------------
    # 실제 연도
    # -----------------------------------------------------

    temp["year"] = (
        temp["year_column"]
        .map(year_map)
    )


    # -----------------------------------------------------
    # 컬럼명 표준화
    # -----------------------------------------------------

    temp = temp.rename(
        columns={
            "범죄별":
            "crime_type_original",

            "발생지별":
            "region_original"
        }
    )


    # -----------------------------------------------------
    # 숫자 변환
    # -----------------------------------------------------

    temp["occurrence_count"] = (
        pd.to_numeric(
            temp["occurrence_count"],
            errors="coerce"
        )
    )


    # -----------------------------------------------------
    # 원본 출처
    # -----------------------------------------------------

    temp["source_file"] = file_name


    # -----------------------------------------------------
    # 원본 지역명 보존
    # -----------------------------------------------------

    temp["region_original"] = (
        temp["region_original"]
        .astype(str)
        .str.strip()
    )


    temp["crime_type_original"] = (
        temp["crime_type_original"]
        .astype(str)
        .str.strip()
    )


    # -----------------------------------------------------
    # 불필요 컬럼 제거
    # -----------------------------------------------------

    temp = temp.drop(
        columns=[
            "year_column"
        ]
    )


    frames.append(temp)


# =========================================================
# 통합
# =========================================================

region_df = pd.concat(
    frames,
    ignore_index=True
)


# =========================================================
# 완전 동일 레코드 확인
# =========================================================

key_columns = [
    "year",
    "region_original",
    "crime_type_original"
]

duplicate_mask = (
    region_df
    .duplicated(
        subset=key_columns,
        keep=False
    )
)

region_df["possible_duplicate"] = (
    duplicate_mask
)


# =========================================================
# 정렬
# =========================================================

region_df = (
    region_df
    .sort_values(
        [
            "year",
            "region_original",
            "crime_type_original"
        ]
    )
    .reset_index(drop=True)
)


# =========================================================
# 저장
# =========================================================

region_df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# 결과
# =========================================================

print("\n" + "=" * 80)
print("CSI LAB - 지역 범죄 데이터 변환 완료")
print("=" * 80)

print("\n통합 데이터 크기:")
print(region_df.shape)

print("\n연도 범위:")
print(
    region_df["year"].min(),
    "~",
    region_df["year"].max()
)

print("\n고유 지역 수:")
print(
    region_df["region_original"]
    .nunique()
)

print("\n고유 범죄 수:")
print(
    region_df["crime_type_original"]
    .nunique()
)

print("\n지역 전체 목록:")

regions = sorted(
    region_df[
        "region_original"
    ]
    .dropna()
    .unique()
)

print(regions)


print("\n중복 가능 행 수:")

print(
    region_df[
        "possible_duplicate"
    ].sum()
)


print("\n중복 가능 조합 예시:")

print(
    region_df.loc[
        region_df["possible_duplicate"],
        [
            "year",
            "region_original",
            "crime_type_original",
            "occurrence_count",
            "source_file"
        ]
    ]
    .head(30)
    .to_string(index=False)
)


print("\n샘플:")

print(
    region_df[
        [
            "year",
            "region_original",
            "crime_type_original",
            "occurrence_count"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


print("\n저장 완료:")
print(OUTPUT)