from pathlib import Path
import pandas as pd

# =========================================================
# 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"

INPUT = PROCESSED_DIR / "occurrence_arrest_1990_2022.csv"

df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)

print("=" * 80)
print("CSI LAB - 발생·검거 데이터 품질 검증")
print("=" * 80)


# =========================================================
# 1. 기본 정보
# =========================================================

print("\n[1] 기본 정보")

print("데이터 크기:", df.shape)

print(
    "연도 범위:",
    df["year"].min(),
    "~",
    df["year"].max()
)

print(
    "죄종 수:",
    df["crime_type"].nunique()
)


# =========================================================
# 2. 연도 누락 검사
# =========================================================

print("\n[2] 연도 연속성 검사")

expected_years = set(
    range(
        int(df["year"].min()),
        int(df["year"].max()) + 1
    )
)

actual_years = set(
    df["year"]
    .dropna()
    .astype(int)
    .unique()
)

missing_years = sorted(
    expected_years - actual_years
)

if len(missing_years) == 0:
    print("OK - 누락 연도 없음")
else:
    print("주의 - 누락 연도:", missing_years)


# =========================================================
# 3. 연도별 행 수
# =========================================================

print("\n[3] 연도별 데이터 행 수")

year_counts = (
    df.groupby("year")
    .size()
    .reset_index(name="row_count")
)

print(year_counts.to_string(index=False))


# =========================================================
# 4. 중복 검사
# =========================================================

print("\n[4] year + crime_type 중복 검사")

duplicates = df[
    df.duplicated(
        subset=["year", "crime_type"],
        keep=False
    )
].copy()

print("중복 행 수:", len(duplicates))

if len(duplicates) > 0:

    print(
        duplicates[
            [
                "year",
                "crime_type",
                "source_period",
                "source_file"
            ]
        ]
        .head(30)
        .to_string(index=False)
    )

else:

    print("OK - 중복 없음")


# =========================================================
# 5. 결측값 검사
# =========================================================

print("\n[5] 핵심 지표 결측값")

metrics = [
    "occurrence_count",
    "arrest_count",
    "clearance_rate"
]

for column in metrics:

    missing = df[column].isna().sum()

    rate = (
        missing / len(df) * 100
    )

    print(
        f"{column}: "
        f"{missing:,}개 "
        f"({rate:.2f}%)"
    )


# =========================================================
# 6. 음수값 검사
# =========================================================

print("\n[6] 음수값 검사")

for column in metrics:

    negative = (
        pd.to_numeric(
            df[column],
            errors="coerce"
        ) < 0
    ).sum()

    print(
        f"{column}: {negative}개"
    )


# =========================================================
# 7. 검거율 범위 검사
# =========================================================

print("\n[7] 검거율 검사")

rate = pd.to_numeric(
    df["clearance_rate"],
    errors="coerce"
)

print(
    "검거율 최소:",
    rate.min()
)

print(
    "검거율 최대:",
    rate.max()
)

over_100 = df[
    rate > 100
].copy()

print(
    "검거율 100% 초과:",
    len(over_100),
    "행"
)

if len(over_100) > 0:

    print("\n[100% 초과 예시]")

    print(
        over_100[
            [
                "year",
                "crime_type",
                "occurrence_count",
                "arrest_count",
                "clearance_rate"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


# =========================================================
# 8. 발생건수 0인데 검거건수가 있는 경우
# =========================================================

print("\n[8] 발생건수 0 + 검거건수 존재")

occurrence = pd.to_numeric(
    df["occurrence_count"],
    errors="coerce"
)

arrest = pd.to_numeric(
    df["arrest_count"],
    errors="coerce"
)

special = df[
    (occurrence == 0)
    & (arrest > 0)
]

print(
    "해당 행:",
    len(special)
)

if len(special) > 0:

    print(
        special[
            [
                "year",
                "crime_type",
                "occurrence_count",
                "arrest_count",
                "clearance_rate"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


# =========================================================
# 9. 검거율 재계산 비교
# =========================================================

print("\n[9] 원본 검거율 ↔ 계산 검거율 비교")

check = df.copy()

check["calculated_rate"] = (
    pd.to_numeric(
        check["arrest_count"],
        errors="coerce"
    )
    /
    pd.to_numeric(
        check["occurrence_count"],
        errors="coerce"
    )
    * 100
)

check["rate_difference"] = (
    pd.to_numeric(
        check["clearance_rate"],
        errors="coerce"
    )
    -
    check["calculated_rate"]
).abs()

different = check[
    check["rate_difference"] > 0.2
]

print(
    "0.2%p 이상 차이:",
    len(different),
    "행"
)

if len(different) > 0:

    print(
        different[
            [
                "year",
                "crime_type",
                "clearance_rate",
                "calculated_rate",
                "rate_difference"
            ]
        ]
        .head(20)
        .to_string(index=False)
    )


# =========================================================
# 10. 검증 결과 저장
# =========================================================

REPORT = PROCESSED_DIR / "06_validation_summary.csv"

summary = pd.DataFrame({
    "check": [
        "total_rows",
        "start_year",
        "end_year",
        "crime_type_count",
        "missing_year_count",
        "duplicate_count",
        "missing_occurrence",
        "missing_arrest",
        "missing_clearance_rate",
        "clearance_rate_over_100"
    ],
    "value": [
        len(df),
        df["year"].min(),
        df["year"].max(),
        df["crime_type"].nunique(),
        len(missing_years),
        len(duplicates),
        df["occurrence_count"].isna().sum(),
        df["arrest_count"].isna().sum(),
        df["clearance_rate"].isna().sum(),
        len(over_100)
    ]
})

summary.to_csv(
    REPORT,
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 80)
print("검증 완료")
print("=" * 80)

print("\n검증 요약 저장:")
print(REPORT)