from pathlib import Path
import pandas as pd
import numpy as np

# =========================================================
# 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"

INPUT = PROCESSED_DIR / "occurrence_arrest_1990_2022.csv"
OUTPUT = PROCESSED_DIR / "crime_analysis_1990_2022.csv"


# =========================================================
# 데이터 읽기
# =========================================================

df = pd.read_csv(
    INPUT,
    encoding="utf-8-sig"
)

print("=" * 80)
print("CSI LAB - 분석용 데이터 생성")
print("=" * 80)

print("\n원본 크기:", df.shape)


# =========================================================
# 숫자형 변환
# =========================================================

numeric_columns = [
    "occurrence_count",
    "arrest_count",
    "clearance_rate"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# =========================================================
# 데이터 존재 여부
# =========================================================

df["has_occurrence"] = df["occurrence_count"].notna()
df["has_arrest"] = df["arrest_count"].notna()
df["has_clearance_rate"] = df["clearance_rate"].notna()


# =========================================================
# 계산 검거율
# =========================================================
# 주의:
# 원본 clearance_rate는 수정하지 않음

df["calculated_clearance_rate"] = np.where(
    (df["occurrence_count"].notna())
    & (df["arrest_count"].notna())
    & (df["occurrence_count"] > 0),

    df["arrest_count"]
    / df["occurrence_count"]
    * 100,

    np.nan
)


# =========================================================
# 원본 ↔ 계산 검거율 차이
# =========================================================

df["rate_difference"] = (
    df["clearance_rate"]
    - df["calculated_clearance_rate"]
).abs()


# =========================================================
# 검거율 100% 초과
# =========================================================

df["clearance_over_100"] = (
    df["clearance_rate"] > 100
)


# =========================================================
# 검거율 불일치
# =========================================================
# 0.2%p 초과 차이는 확인 대상으로 표시

df["rate_mismatch"] = (
    df["rate_difference"] > 0.2
)


# =========================================================
# Quality Flag
# =========================================================

def make_quality_flag(row):

    flags = []

    if not row["has_occurrence"]:
        flags.append("MISSING_OCCURRENCE")

    if not row["has_arrest"]:
        flags.append("MISSING_ARREST")

    if not row["has_clearance_rate"]:
        flags.append("MISSING_CLEARANCE_RATE")

    if row["clearance_over_100"]:
        flags.append("CLEARANCE_OVER_100")

    if row["rate_mismatch"]:
        flags.append("RATE_MISMATCH")

    if len(flags) == 0:
        return "OK"

    return "|".join(flags)


df["quality_flag"] = df.apply(
    make_quality_flag,
    axis=1
)


# =========================================================
# CSI LAB 역할
# =========================================================

df["real_data_evidence"] = True
df["crime_data_map"] = True
df["time_machine"] = True

# YOLO와 직접 연결되는 데이터는 아님
df["yolo_evidence"] = False


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

print("\n분석용 데이터 크기:")
print(df.shape)

print("\nQuality Flag 분포:")
print(
    df["quality_flag"]
    .value_counts()
    .head(20)
)

print("\n검거율 100% 초과:")
print(
    df["clearance_over_100"].sum()
)

print("\n검거율 불일치:")
print(
    df["rate_mismatch"].sum()
)

print("\n발생건수 결측:")
print(
    (~df["has_occurrence"]).sum()
)

print("\n검거건수 결측:")
print(
    (~df["has_arrest"]).sum()
)

print("\n검거율 결측:")
print(
    (~df["has_clearance_rate"]).sum()
)

print("\n저장 완료:")
print(OUTPUT)