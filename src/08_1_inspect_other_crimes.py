from pathlib import Path
import pandas as pd

# =========================================================
# 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"

INPUT = (
    PROCESSED_DIR
    / "crime_analysis_grouped_1990_2022.csv"
)

OUTPUT = (
    PROCESSED_DIR
    / "08_other_crime_types.csv"
)


# =========================================================
# 데이터 읽기
# =========================================================

df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)


# =========================================================
# 기타만 선택
# =========================================================

other = df[
    df["crime_group_standard"] == "기타"
].copy()


print("=" * 80)
print("CSI LAB - 기타 범죄 분석")
print("=" * 80)

print("\n기타 전체 행 수:")
print(len(other))

print("\n기타 고유 죄종 수:")
print(
    other["crime_type_original"].nunique()
)


# =========================================================
# 죄종별 등장 연도 수 / 행 수 / 발생건수
# =========================================================

summary = (
    other
    .groupby("crime_type_original")
    .agg(
        row_count=("year", "size"),

        year_count=("year", "nunique"),

        first_year=("year", "min"),

        last_year=("year", "max"),

        occurrence_total=(
            "occurrence_count",
            "sum"
        )
    )
    .reset_index()
)


# =========================================================
# 많이 등장하는 죄종부터 정렬
# =========================================================

summary = summary.sort_values(
    [
        "year_count",
        "row_count",
        "occurrence_total"
    ],
    ascending=[
        False,
        False,
        False
    ]
)


# =========================================================
# CSV 저장
# =========================================================

summary.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# 결과 출력
# =========================================================

print("\n[기타 죄종 TOP 100]")
print(
    summary
    .head(100)
    .to_string(index=False)
)


print("\n저장 완료:")
print(OUTPUT)