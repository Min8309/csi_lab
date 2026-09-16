from pathlib import Path
import pandas as pd
import numpy as np

# =========================================================
# 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"

INPUT = (
    PROCESSED_DIR
    / "crime_analysis_refined_1990_2022.csv"
)

OUTPUT = (
    PROCESSED_DIR
    / "real_data_evidence_1990_2022.csv"
)


# =========================================================
# 데이터 읽기
# =========================================================

df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)

print("=" * 80)
print("CSI LAB - REAL DATA Evidence 생성")
print("=" * 80)


# =========================================================
# 1. 개별 분석 가능한 데이터
# =========================================================

evidence = df[
    df["include_detail_analysis"] == True
].copy()


# =========================================================
# 2. 기본 데이터 존재 여부
# =========================================================

evidence["has_real_stat"] = (
    evidence["occurrence_count"].notna()
    | evidence["arrest_count"].notna()
)

evidence = evidence[
    evidence["has_real_stat"]
].copy()


# =========================================================
# 3. 연도 정렬
# =========================================================

evidence = evidence.sort_values(
    [
        "crime_type_original",
        "year"
    ]
)


# =========================================================
# 4. 전년 발생건수
# =========================================================

evidence["previous_occurrence"] = (
    evidence
    .groupby("crime_type_original")
    ["occurrence_count"]
    .shift(1)
)


# =========================================================
# 5. 실제 이전 관측 연도
# =========================================================

evidence["previous_year"] = (
    evidence
    .groupby("crime_type_original")
    ["year"]
    .shift(1)
)


# =========================================================
# 6. 전년 대비 변화율
# =========================================================
# 반드시 직전 연도가 실제 존재할 때만 계산

valid_previous_year = (
    evidence["previous_year"]
    == evidence["year"] - 1
)

valid_previous_value = (
    evidence["previous_occurrence"].notna()
    & (evidence["previous_occurrence"] > 0)
)

valid_change = (
    valid_previous_year
    & valid_previous_value
    & evidence["occurrence_count"].notna()
)


evidence["yoy_change_rate"] = np.where(
    valid_change,

    (
        evidence["occurrence_count"]
        - evidence["previous_occurrence"]
    )
    / evidence["previous_occurrence"]
    * 100,

    np.nan
)


# =========================================================
# 7. 변화 방향
# =========================================================

def change_direction(value):

    if pd.isna(value):
        return "비교불가"

    if value > 1:
        return "증가"

    if value < -1:
        return "감소"

    return "유사"


evidence["trend_direction"] = (
    evidence["yoy_change_rate"]
    .apply(change_direction)
)


# =========================================================
# 8. 데이터 주의 표시
# =========================================================

def make_warning(row):

    warnings = []

    if pd.isna(row["occurrence_count"]):
        warnings.append("발생건수 없음")

    if pd.isna(row["arrest_count"]):
        warnings.append("검거건수 없음")

    if pd.isna(row["clearance_rate"]):
        warnings.append("공표 검거율 없음")

    if row.get("clearance_over_100", False) == True:
        warnings.append("검거율 100% 초과")

    if row.get("rate_mismatch", False) == True:
        warnings.append("검거율 원자료 확인 필요")

    if len(warnings) == 0:
        return ""

    return " | ".join(warnings)


evidence["data_warning"] = (
    evidence.apply(
        make_warning,
        axis=1
    )
)


# =========================================================
# 9. REAL DATA Evidence 카드용 설명
# =========================================================

def make_card_text(row):

    parts = []

    if pd.notna(row["occurrence_count"]):

        parts.append(
            f"발생 {int(row['occurrence_count']):,}건"
        )

    if pd.notna(row["arrest_count"]):

        parts.append(
            f"검거 {int(row['arrest_count']):,}건"
        )

    if pd.notna(row["clearance_rate"]):

        parts.append(
            f"공표 검거율 {row['clearance_rate']:.1f}%"
        )

    if pd.notna(row["yoy_change_rate"]):

        parts.append(
            f"전년 대비 {row['yoy_change_rate']:+.1f}%"
        )

    return " / ".join(parts)


evidence["evidence_card_text"] = (
    evidence.apply(
        make_card_text,
        axis=1
    )
)


# =========================================================
# 10. 게임 연결용 ID
# =========================================================

evidence = evidence.reset_index(drop=True)

evidence["evidence_id"] = [
    f"DATA-{i:06d}"
    for i in range(1, len(evidence) + 1)
]


# =========================================================
# 11. 화면 표시 가능 여부
# =========================================================
# 최소 발생 또는 검거 통계가 있어야 함

evidence["display_ready"] = (
    evidence["occurrence_count"].notna()
    | evidence["arrest_count"].notna()
)


# =========================================================
# 12. 필요한 컬럼 선택
# =========================================================

columns = [
    "evidence_id",
    "year",
    "region",

    "crime_type_original",
    "crime_group_refined",
    "related_groups",

    "occurrence_count",
    "arrest_count",
    "clearance_rate",

    "previous_occurrence",
    "yoy_change_rate",
    "trend_direction",

    "quality_flag",
    "data_warning",

    "evidence_card_text",

    "source_file",
    "display_ready"
]

evidence = evidence[
    [
        col for col in columns
        if col in evidence.columns
    ]
]


# =========================================================
# 13. 저장
# =========================================================

evidence.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# 결과 확인
# =========================================================

print("\nREAL DATA Evidence 행 수:")
print(len(evidence))

print("\n범죄군별 Evidence 수:")
print(
    evidence["crime_group_refined"]
    .value_counts()
)


print("\n추세 방향:")
print(
    evidence["trend_direction"]
    .value_counts()
)


print("\n주의 데이터 수:")
print(
    (evidence["data_warning"] != "").sum()
)


print("\nEvidence 카드 샘플:")

print(
    evidence[
        [
            "evidence_id",
            "year",
            "crime_type_original",
            "crime_group_refined",
            "evidence_card_text",
            "data_warning"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


print("\n저장 완료:")
print(OUTPUT)