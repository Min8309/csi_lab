from pathlib import Path
import pandas as pd

# =========================================================
# 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"

INPUT = (
    PROCESSED_DIR
    / "time_machine_1990_2022.csv"
)

OUTPUT = (
    PROCESSED_DIR
    / "csi_time_machine_1990_2022.csv"
)


# =========================================================
# 데이터 읽기
# =========================================================

df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)

print("=" * 80)
print("CSI LAB - CORE Time Machine")
print("=" * 80)


# =========================================================
# CSI LAB 핵심 사건 유형
# =========================================================

CORE_CRIMES = {
    "살인",
    "강도",
    "강간",
    "방화",
    "사기",
    "특수절도",
    "야간주거침입절도",
    "상해",
    "협박",
    "공갈",
}


# =========================================================
# 활용 단계
# =========================================================

def make_game_level(row):

    crime = str(
        row["crime_type_original"]
    )

    grade = str(
        row["time_machine_grade"]
    )

    # 게임 핵심 + 장기 시계열
    if crime in CORE_CRIMES and grade == "30Y":
        return "CORE"

    # CSI 분석그룹이면서 장기 데이터
    if (
        grade == "30Y"
        and row["crime_group_refined"] != "기타"
    ):
        return "RELATED"

    return "REFERENCE"


df["game_data_level"] = (
    df.apply(
        make_game_level,
        axis=1
    )
)


# =========================================================
# CORE 여부
# =========================================================

df["core_time_machine"] = (
    df["game_data_level"] == "CORE"
)


# =========================================================
# 게임용 사건 코드
# =========================================================

CASE_CODES = {
    "살인": "CASE-MURDER",
    "강도": "CASE-ROBBERY",
    "강간": "CASE-SEXUAL",
    "방화": "CASE-ARSON",
    "사기": "CASE-FRAUD",
    "특수절도": "CASE-THEFT",
    "야간주거침입절도": "CASE-BURGLARY",
    "상해": "CASE-ASSAULT",
    "협박": "CASE-THREAT",
    "공갈": "CASE-EXTORTION",
}


df["case_code"] = (
    df["crime_type_original"]
    .map(CASE_CODES)
    .fillna("")
)


# =========================================================
# 1990 기준값
# =========================================================

core = df[
    df["core_time_machine"]
].copy()

baseline = (
    core[
        core["year"] == 1990
    ]
    [
        [
            "crime_type_original",
            "occurrence_count"
        ]
    ]
    .rename(
        columns={
            "occurrence_count":
            "baseline_1990"
        }
    )
)


df = df.merge(
    baseline,
    on="crime_type_original",
    how="left"
)


# =========================================================
# 1990 대비 변화율
# =========================================================

df["change_from_1990_pct"] = (
    (
        df["occurrence_count"]
        - df["baseline_1990"]
    )
    / df["baseline_1990"]
    * 100
)


# =========================================================
# 게임 표시 여부
# =========================================================

df["show_in_game"] = (
    df["game_data_level"]
    .isin(
        [
            "CORE",
            "RELATED"
        ]
    )
)


# =========================================================
# 정렬
# =========================================================

df = df.sort_values(
    [
        "game_data_level",
        "crime_type_original",
        "year"
    ]
).reset_index(drop=True)


# =========================================================
# 저장
# =========================================================

df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# 결과 확인
# =========================================================

print("\n게임 데이터 단계별 행 수:")

print(
    df["game_data_level"]
    .value_counts()
)


print("\nCORE 범죄:")

core_names = (
    df.loc[
        df["core_time_machine"],
        "crime_type_original"
    ]
    .drop_duplicates()
    .sort_values()
)

print(
    core_names.to_list()
)


print("\nCORE 범죄 수:")
print(
    core_names.nunique()
)


print("\nCORE 연도별 데이터 수:")

print(
    df[
        df["core_time_machine"]
    ]
    .groupby("crime_type_original")
    ["year"]
    .nunique()
)


print("\nCASE CODE:")

print(
    df[
        df["core_time_machine"]
    ]
    [
        [
            "crime_type_original",
            "case_code"
        ]
    ]
    .drop_duplicates()
    .to_string(index=False)
)


print("\n1990 → 2022 변화 예시:")

example = df[
    (
        df["core_time_machine"]
    )
    &
    (
        df["year"].isin(
            [1990, 2022]
        )
    )
][
    [
        "crime_type_original",
        "year",
        "occurrence_count",
        "clearance_rate",
        "change_from_1990_pct"
    ]
]

print(
    example.to_string(index=False)
)


print("\n저장 완료:")
print(OUTPUT)