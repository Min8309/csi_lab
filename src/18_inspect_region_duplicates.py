from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"

INPUT = PROCESSED_DIR / "region_crime_1994_2024.csv"


df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)


KEY = [
    "year",
    "region_original",
    "crime_type_original"
]


# =========================================================
# 중복 데이터
# =========================================================

dup = df[
    df.duplicated(
        subset=KEY,
        keep=False
    )
].copy()


print("=" * 90)
print("CSI LAB 지역 데이터 중복 검사")
print("=" * 90)

print("\n전체 행:")
print(len(df))

print("\n중복 KEY 관련 행:")
print(len(dup))


# =========================================================
# 중복 조합 수
# =========================================================

dup_groups = (
    dup.groupby(KEY, dropna=False)
    .size()
    .reset_index(name="row_count")
    .sort_values(
        "row_count",
        ascending=False
    )
)


print("\n중복 KEY 조합 수:")
print(len(dup_groups))

print("\n중복 횟수 분포:")
print(
    dup_groups["row_count"]
    .value_counts()
    .sort_index()
)


# =========================================================
# 가장 많이 중복된 조합
# =========================================================

print("\n" + "=" * 90)
print("중복 조합 TOP 30")
print("=" * 90)

print(
    dup_groups
    .head(30)
    .to_string(index=False)
)


# =========================================================
# 실제 중복 행 확인
# =========================================================

print("\n" + "=" * 90)
print("실제 중복 행 예시")
print("=" * 90)

example_keys = (
    dup_groups
    .head(10)[KEY]
)

example = dup.merge(
    example_keys,
    on=KEY,
    how="inner"
)

print(
    example[
        [
            "year",
            "region_original",
            "crime_type_original",
            "occurrence_count",
            "source_file"
        ]
    ]
    .sort_values(KEY)
    .to_string(index=False)
)


# =========================================================
# 같은 KEY인데 값도 같은가?
# =========================================================

value_check = (
    dup.groupby(KEY)
    ["occurrence_count"]
    .nunique(dropna=False)
    .reset_index(
        name="different_value_count"
    )
)


same_value_groups = value_check[
    value_check["different_value_count"] == 1
].copy()

different_value_groups = value_check[
    value_check["different_value_count"] > 1
].copy()


print("\n" + "=" * 90)
print("중복 값 성격")
print("=" * 90)

print("\n같은 KEY + 같은 값:")
print(len(same_value_groups))

print("\n같은 KEY + 서로 다른 값:")
print(len(different_value_groups))


print("\n서로 다른 값이 있는 KEY 예시:")

different_examples = (
    different_value_groups
    .head(20)
)

if different_examples.empty:

    print("없음")

else:

    detail = dup.merge(
        different_examples[KEY],
        on=KEY,
        how="inner"
    )

    print(
        detail[
            [
                "year",
                "region_original",
                "crime_type_original",
                "occurrence_count",
                "source_file"
            ]
        ]
        .sort_values(KEY)
        .to_string(index=False)
    )


# =========================================================
# 특정 사례 확인
# =========================================================

print("\n" + "=" * 90)
print("용산 × 절도 확인")
print("=" * 90)

test = df[
    (df["region_original"] == "용산")
    &
    (df["crime_type_original"] == "절도")
][
    [
        "year",
        "occurrence_count",
        "source_file"
    ]
]

print(
    test
    .sort_values("year")
    .to_string(index=False)
)
