from pathlib import Path
import pandas as pd

# =========================================================
# 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"

INPUT = (
    PROCESSED_DIR
    / "real_data_evidence_1990_2022.csv"
)

OUTPUT = (
    PROCESSED_DIR
    / "time_machine_1990_2022.csv"
)

SUMMARY_OUTPUT = (
    PROCESSED_DIR
    / "time_machine_crime_summary.csv"
)


# =========================================================
# 데이터 읽기
# =========================================================

df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)

print("=" * 80)
print("CSI LAB - 30Y Crime Time Machine 생성")
print("=" * 80)


# =========================================================
# 1. 분석 가능한 핵심 데이터
# =========================================================

tm = df[
    df["occurrence_count"].notna()
].copy()


# =========================================================
# 2. 원본 죄종별 시계열 정보
# =========================================================

summary = (
    tm
    .groupby(
        [
            "crime_type_original",
            "crime_group_refined"
        ],
        dropna=False
    )
    .agg(
        first_year=("year", "min"),
        last_year=("year", "max"),
        year_count=("year", "nunique"),
        observation_count=("year", "size")
    )
    .reset_index()
)


# =========================================================
# 3. 실제 기간(span)
# =========================================================

summary["year_span"] = (
    summary["last_year"]
    - summary["first_year"]
    + 1
)


# =========================================================
# 4. 기간 내 데이터 완성도
# =========================================================

summary["coverage_rate"] = (
    summary["year_count"]
    / summary["year_span"]
    * 100
)


# =========================================================
# 5. Time Machine 등급
# =========================================================

def make_time_grade(row):

    years = row["year_count"]
    coverage = row["coverage_rate"]

    if years >= 30 and coverage >= 90:
        return "30Y"

    if years >= 20 and coverage >= 80:
        return "20Y"

    if years >= 10 and coverage >= 70:
        return "10Y"

    return "SHORT"


summary["time_machine_grade"] = (
    summary.apply(
        make_time_grade,
        axis=1
    )
)


# =========================================================
# 6. 시계열 데이터에 요약정보 연결
# =========================================================

tm = tm.merge(
    summary[
        [
            "crime_type_original",
            "crime_group_refined",
            "first_year",
            "last_year",
            "year_count",
            "year_span",
            "coverage_rate",
            "time_machine_grade"
        ]
    ],
    on=[
        "crime_type_original",
        "crime_group_refined"
    ],
    how="left"
)


# =========================================================
# 7. 30Y 사용 가능 여부
# =========================================================

tm["thirty_year_ready"] = (
    tm["time_machine_grade"] == "30Y"
)


# =========================================================
# 8. 앱 표시용 추세 라벨
# =========================================================

def make_trend_label(row):

    if row["trend_direction"] == "증가":
        return "전년보다 증가"

    if row["trend_direction"] == "감소":
        return "전년보다 감소"

    if row["trend_direction"] == "유사":
        return "전년과 비슷"

    return "연속 비교 불가"


tm["trend_label"] = (
    tm.apply(
        make_trend_label,
        axis=1
    )
)


# =========================================================
# 9. 정렬
# =========================================================

tm = tm.sort_values(
    [
        "crime_group_refined",
        "crime_type_original",
        "year"
    ]
).reset_index(drop=True)


# =========================================================
# 10. 저장
# =========================================================

tm.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)

summary = summary.sort_values(
    [
        "time_machine_grade",
        "year_count"
    ],
    ascending=[
        True,
        False
    ]
)

summary.to_csv(
    SUMMARY_OUTPUT,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# 결과 확인
# =========================================================

print("\nTime Machine 데이터 행 수:")
print(len(tm))


print("\nTime Machine 등급별 죄종 수:")

print(
    summary["time_machine_grade"]
    .value_counts()
)


print("\n30Y 사용 가능 죄종 수:")

print(
    (
        summary["time_machine_grade"]
        == "30Y"
    ).sum()
)


print("\n30Y 범죄군별 죄종 수:")

thirty = summary[
    summary["time_machine_grade"] == "30Y"
]

print(
    thirty[
        "crime_group_refined"
    ]
    .value_counts()
)


print("\n30Y 사용 가능 죄종 예시:")

print(
    thirty[
        [
            "crime_type_original",
            "crime_group_refined",
            "first_year",
            "last_year",
            "year_count",
            "coverage_rate"
        ]
    ]
    .head(50)
    .to_string(index=False)
)


print("\n저장 완료:")
print(OUTPUT)

print("\n요약 저장:")
print(SUMMARY_OUTPUT)