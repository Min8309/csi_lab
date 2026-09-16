from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"

INPUT = PROCESSED_DIR / "crime_analysis_1990_2022.csv"
OUTPUT = PROCESSED_DIR / "crime_analysis_grouped_1990_2022.csv"

df = pd.read_csv(INPUT, encoding="utf-8-sig")


# =========================================================
# CSI LAB 분석용 범죄군
# =========================================================

def classify_crime(name):

    name = str(name).replace(" ", "")

    # 순서 중요
    if any(x in name for x in [
        "살인", "영아살해", "존속살해"
    ]):
        return "살인"

    if "강도" in name:
        return "강도"

    if any(x in name for x in [
        "강간",
        "강제추행",
        "유사강간",
        "성폭력",
        "성매매",
        "음란",
        "간음",
        "추행"
    ]):
        return "성범죄"

    if any(x in name for x in [
        "절도",
        "도둑"
    ]):
        return "절도"

    if any(x in name for x in [
        "폭행",
        "상해",
        "폭력",
        "협박"
    ]):
        return "폭력"

    if any(x in name for x in [
        "사기",
        "횡령",
        "배임"
    ]):
        return "사기"

    if "방화" in name:
        return "방화"

    if any(x in name for x in [
        "마약",
        "대마",
        "향정"
    ]):
        return "마약"

    if any(x in name for x in [
        "도로교통",
        "교통사고",
        "교통사범"
    ]):
        return "교통"

    return "기타"


df["crime_group_standard"] = (
    df["crime_type"]
    .apply(classify_crime)
)


# =========================================================
# 원본 명칭임을 명확하게 표시
# =========================================================

df = df.rename(
    columns={
        "crime_type": "crime_type_original"
    }
)


# =========================================================
# CSI LAB 활용 수준
# =========================================================

CORE_GROUPS = [
    "살인",
    "강도",
    "성범죄",
    "절도",
    "폭력",
    "사기",
    "방화",
    "마약"
]

df["csi_core_group"] = (
    df["crime_group_standard"]
    .isin(CORE_GROUPS)
)


# =========================================================
# 저장
# =========================================================

df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# 결과 출력
# =========================================================

print("=" * 80)
print("CSI LAB - 범죄군 표준화")
print("=" * 80)

print("\n데이터 크기:")
print(df.shape)

print("\n범죄군별 행 수:")
print(
    df["crime_group_standard"]
    .value_counts()
)

print("\n범죄군별 고유 원본 죄종 수:")
print(
    df.groupby("crime_group_standard")
      ["crime_type_original"]
      .nunique()
      .sort_values(ascending=False)
)

print("\nCSI 핵심 범죄군 행 수:")
print(
    df["csi_core_group"]
    .value_counts()
)

print("\n샘플:")
print(
    df[
        [
            "year",
            "crime_type_original",
            "crime_group_standard",
            "occurrence_count",
            "quality_flag"
        ]
    ]
    .head(30)
    .to_string(index=False)
)

print("\n저장 완료:")
print(OUTPUT)