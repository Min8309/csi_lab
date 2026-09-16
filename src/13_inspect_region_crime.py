from pathlib import Path
import pandas as pd


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
    / "13_region_crime_structure.txt"
)


# =========================================================
# CSV 읽기
# =========================================================

def read_csv_auto(path):

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp949",
        "euc-kr"
    ]

    for encoding in encodings:

        try:

            df = pd.read_csv(
                path,
                encoding=encoding
            )

            return df, encoding

        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"인코딩 확인 실패: {path.name}"
    )


# =========================================================
# 결과 저장용
# =========================================================

lines = []

lines.append(
    "=" * 100
)

lines.append(
    "CSI LAB - 지역별 범죄 데이터 구조 확인"
)

lines.append(
    "=" * 100
)


# =========================================================
# 파일별 분석
# =========================================================

for file_name in FILES:

    path = RAW_DIR / file_name

    lines.append("")
    lines.append("=" * 100)
    lines.append(f"파일: {file_name}")
    lines.append("=" * 100)

    if not path.exists():

        lines.append("파일을 찾을 수 없습니다.")
        continue

    df, encoding = read_csv_auto(path)

    lines.append(
        f"인코딩: {encoding}"
    )

    lines.append(
        f"크기: {df.shape}"
    )

    lines.append("")
    lines.append("[컬럼 목록]")

    for i, col in enumerate(
        df.columns,
        start=1
    ):

        lines.append(
            f"{i:02d}. {col}"
        )


    # -----------------------------------------------------
    # 앞부분 데이터
    # -----------------------------------------------------

    lines.append("")
    lines.append("[앞 10행]")

    lines.append(
        df.head(10).to_string(
            index=False
        )
    )


    # -----------------------------------------------------
    # 각 컬럼의 고유값 일부 확인
    # -----------------------------------------------------

    lines.append("")
    lines.append(
        "[컬럼별 고유값 샘플]"
    )

    for col in df.columns:

        values = (
            df[col]
            .dropna()
            .astype(str)
            .unique()
        )

        lines.append("")
        lines.append(
            f"▶ {col}"
        )

        lines.append(
            f"고유값 수: {len(values)}"
        )

        sample = values[:30]

        lines.append(
            f"샘플: {sample.tolist()}"
        )


# =========================================================
# 저장
# =========================================================

text = "\n".join(lines)

OUTPUT.write_text(
    text,
    encoding="utf-8"
)


# =========================================================
# 터미널 출력
# =========================================================

print(text)

print("\n")
print("=" * 100)

print(
    "저장 완료:"
)

print(
    OUTPUT
)