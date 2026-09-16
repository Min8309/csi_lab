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

OUTPUT = PROCESSED_DIR / "region_crime_final_1994_2024.csv"



# =========================================================
# 1994~2010 지역 구조
# =========================================================

CITY_REGIONS_OLD = {

    "서울특별시": [
        "종로", "중구", "용산", "성동", "광진",
        "동대문", "중랑", "성북", "강북", "도봉",
        "노원", "은평", "서대문", "마포", "양천",
        "강서", "구로", "금천", "영등포", "동작",
        "관악", "서초", "강남", "송파", "강동"
    ],

    "부산광역시": [
        "중구", "서구", "동구", "영도",
        "부산진", "동래", "남구", "북구",
        "해운대", "사하", "금정", "강서",
        "연제", "수영", "사상", "기장군"
    ],

    "대구광역시": [
        "중구", "동구", "서구", "남구",
        "북구", "수성", "달서", "달성군"
    ],

    "인천광역시": [
        "중구", "동구", "서구", "미추홀",
        "연수", "남동", "부평", "계양",
        "강화군", "옹진군"
    ],

    "광주광역시": [
        "동구", "서구", "남구", "북구", "광산"
    ],

    "대전광역시": [
        "중구", "동구", "서구", "유성", "대덕"
    ],

    "울산광역시": [
        "중구", "동구", "남구", "북구", "울주군"
    ],
}


# =========================================================
# 2011~2024 지역 구조
# 군위군 추가
# =========================================================

CITY_REGIONS_NEW = {

    "서울특별시": [
        "종로", "중구", "용산", "성동", "광진",
        "동대문", "중랑", "성북", "강북", "도봉",
        "노원", "은평", "서대문", "마포", "양천",
        "강서", "구로", "금천", "영등포", "동작",
        "관악", "서초", "강남", "송파", "강동"
    ],

    "부산광역시": [
        "중구", "서구", "동구", "영도",
        "부산진", "동래", "남구", "북구",
        "해운대", "사하", "금정", "강서",
        "연제", "수영", "사상", "기장군"
    ],

    "대구광역시": [
        "중구", "동구", "서구", "남구",
        "북구", "수성", "달서", "달성군",
        "군위군"
    ],

    "인천광역시": [
        "중구", "동구", "서구", "미추홀",
        "연수", "남동", "부평", "계양",
        "강화군", "옹진군"
    ],

    "광주광역시": [
        "동구", "서구", "남구", "북구", "광산"
    ],

    "대전광역시": [
        "중구", "동구", "서구", "유성", "대덕"
    ],

    "울산광역시": [
        "중구", "동구", "남구", "북구", "울주군"
    ],
}


# =========================================================
# CSV 읽기
# =========================================================

def read_csv_auto(path):

    for encoding in [
        "utf-8-sig",
        "utf-8",
        "cp949",
        "euc-kr"
    ]:

        try:
            return pd.read_csv(
                path,
                encoding=encoding
            )

        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"읽기 실패: {path.name}"
    )


# =========================================================
# 연도 컬럼
# =========================================================

def get_year_columns(df):

    result = {}

    for col in df.columns:

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
# 지역 → 도시 복원
# =========================================================

def build_region_lookup(city_regions):

    lookup = []

    position = 0

    for city, regions in city_regions.items():

        for region in regions:

            lookup.append({
                "region_position": position,
                "city": city,
                "region_original_expected": region
            })

            position += 1

    return pd.DataFrame(lookup)





# =========================================================
# 파일 처리
# =========================================================
frames = []


for file_name in FILES:

    path = RAW_DIR / file_name

    df = read_csv_auto(path)

    year_map = get_year_columns(df)

    # =====================================================
    # 기간별 지역 구조 선택 ← 새로 추가
    # =====================================================

    if min(year_map.values()) >= 2011:

        city_regions = CITY_REGIONS_NEW
        region_version = "2011~2024"

    else:

        city_regions = CITY_REGIONS_OLD
        region_version = "1994~2010"

    # 해당 기간에 맞는 지역 lookup 생성
    region_lookup = build_region_lookup(
        city_regions
    )

    print("\n" + "=" * 80)
    print("파일:", file_name)
    print("연도:", sorted(year_map.values()))
    print("지역 구조:", region_version)
    print("예상 지역 수:", len(region_lookup))


    # -----------------------------------------------------
    # 범죄별 원본 행 순서를 이용해 지역 위치 계산
    # -----------------------------------------------------

    df = df.copy()

    df["crime_type_original"] = (
        df["범죄별"]
        .astype(str)
        .str.strip()
    )

    df["region_original"] = (
        df["발생지별"]
        .astype(str)
        .str.strip()
    )


    # =====================================================
# 범죄별 실제 지역 구조를 이용해서 도시 복원
# =====================================================

def assign_region_structure(group):

    group = group.copy().reset_index(drop=True)

    # 실제 범죄별 지역 목록
    actual_regions = (
        group["region_original"]
        .astype(str)
        .str.strip()
        .tolist()
    )

    # OLD 구조
    old_lookup = build_region_lookup(
        CITY_REGIONS_OLD
    )

    old_regions = (
        old_lookup["region_original_expected"]
        .tolist()
    )

    # NEW 구조
    new_lookup = build_region_lookup(
        CITY_REGIONS_NEW
    )

    new_regions = (
        new_lookup["region_original_expected"]
        .tolist()
    )

    # -----------------------------------------
    # 실제 지역 목록과 정확하게 일치하는 구조 선택
    # -----------------------------------------

    if actual_regions == new_regions:

        selected_lookup = new_lookup
        structure_used = "75지역_군위군포함"

    elif actual_regions == old_regions:

        selected_lookup = old_lookup
        structure_used = "74지역_군위군없음"

    else:

        # 정확하게 맞지 않는 경우
        # 잘못 매핑하지 않고 검증 대상으로 남김
        group["region_position"] = range(
            len(group)
        )

        group["city"] = pd.NA
        group["region_original_expected"] = pd.NA
        group["region_match"] = False
        group["structure_used"] = "미확인"

        return group

    # -----------------------------------------
    # 정상 구조
    # -----------------------------------------

    group["region_position"] = range(
        len(group)
    )

    group["city"] = (
        selected_lookup["city"]
        .tolist()
    )

    group["region_original_expected"] = (
        selected_lookup[
            "region_original_expected"
        ]
        .tolist()
    )

    group["region_match"] = (
        group["region_original"]
        ==
        group["region_original_expected"]
    )

    group["structure_used"] = structure_used

    return group


# =====================================================
# 범죄별 지역 구조 적용
# pandas groupby.apply를 사용하지 않는 안전한 방식
# =====================================================

processed_groups = []

for crime_name in df["crime_type_original"].unique():

    crime_group = df[
        df["crime_type_original"] == crime_name
    ].copy()

    crime_group = assign_region_structure(
        crime_group
    )

    processed_groups.append(
        crime_group
    )


df = pd.concat(
    processed_groups,
    ignore_index=True
)
   

mismatch = df[
        ~df["region_match"]
    ]


print("지역 순서 불일치 행:")
print(len(mismatch))

if not mismatch.empty:

        print(
            mismatch[
                [
                    "crime_type_original",
                    "region_position",
                    "region_original",
                    "region_original_expected",
                    "city"
                ]
            ]
            .head(30)
            .to_string(index=False)
        )


    # -----------------------------------------------------
    # Long format
    # -----------------------------------------------------

id_columns = [
    "crime_type_original",
    "region_original",
    "region_position",
    "city",
    "region_match",
    "structure_used"
]


temp = df[
        id_columns
        + list(year_map.keys())
    ].melt(

        id_vars=id_columns,

        value_vars=list(
            year_map.keys()
        ),

        var_name="year_column",

        value_name="occurrence_count"
    )


temp["year"] = (
        temp["year_column"]
        .map(year_map)
    )


temp["occurrence_count"] = (
        pd.to_numeric(
            temp["occurrence_count"],
            errors="coerce"
        )
    )


temp["source_file"] = file_name
temp["region_version"] = region_version

temp = temp.drop(
        columns="year_column"
    )


frames.append(temp)


# =========================================================
# 통합
# =========================================================

result = pd.concat(
    frames,
    ignore_index=True
)


# =========================================================
# 지역명 표시용
# =========================================================

def make_district_name(region):

    region = str(region)

    if region.endswith("군"):
        return region

    return region + "구"


result["district"] = (
    result["region_original"]
    .apply(make_district_name)
)


result["region_full"] = (
    result["city"]
    + " "
    + result["district"]
)


# =========================================================
# 최종 KEY 중복 검사
# =========================================================

KEY = [
    "year",
    "city",
    "district",
    "crime_type_original"
]


result["duplicate_final_key"] = (
    result.duplicated(
        subset=KEY,
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
            "city",
            "district",
            "crime_type_original",
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
# 결과
# =========================================================

print("\n" + "=" * 80)
print("CSI LAB 최종 지역 데이터")
print("=" * 80)

print("\n데이터 크기:")
print(result.shape)

print("\n연도:")
print(
    result["year"].min(),
    "~",
    result["year"].max()
)

print("\n도시:")
print(
    result["city"]
    .dropna()
    .unique()
)

print("\n도시 수:")
print(
    result["city"]
    .nunique()
)

print("\n표준 지역 수:")
print(
    result["region_full"]
    .nunique()
)

print("\n지역 순서 불일치:")
print(
    (~result["region_match"])
    .sum()
)

print("\n최종 KEY 중복:")
print(
    result["duplicate_final_key"]
    .sum()
)


# =========================================================
# 강서 확인
# =========================================================

print("\n" + "=" * 80)
print("강서 지역 분리 확인")
print("=" * 80)

gangseo = result[
    (
        result["district"] == "강서구"
    )
    &
    (
        result["crime_type_original"] == "절도"
    )
    &
    (
        result["year"] == 2004
    )
][
    [
        "year",
        "city",
        "district",
        "crime_type_original",
        "occurrence_count"
    ]
]

print(
    gangseo.to_string(
        index=False
    )
)


# =========================================================
# 용산 확인
# =========================================================

print("\n" + "=" * 80)
print("서울특별시 용산구 × 절도")
print("=" * 80)

yongsan = result[
    (
        result["city"] == "서울특별시"
    )
    &
    (
        result["district"] == "용산구"
    )
    &
    (
        result["crime_type_original"] == "절도"
    )
][
    [
        "year",
        "occurrence_count"
    ]
]

print(
    yongsan.to_string(
        index=False
    )
)


print("\n저장 완료:")
print(OUTPUT)