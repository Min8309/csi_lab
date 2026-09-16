from pathlib import Path
import pandas as pd
import hashlib


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "crime"
PROCESSED_DIR = BASE_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------
# 파일 SHA256
# ------------------------------------------

def get_sha256(path):
    sha = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)

            if not chunk:
                break

            sha.update(chunk)

    return sha.hexdigest()


# ------------------------------------------
# 파일 내용 일부 읽기
# ------------------------------------------

def read_preview(path):

    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]

    for encoding in encodings:
        try:
            df = pd.read_csv(
                path,
                encoding=encoding,
                low_memory=False
            )

            text = (
                " ".join(map(str, df.columns.tolist()))
                + " "
                + " ".join(
                    df.head(30)
                    .astype(str)
                    .fillna("")
                    .values
                    .flatten()
                )
            )

            return df, encoding, text

        except Exception:
            continue

    return None, None, ""


# ------------------------------------------
# 데이터 종류 분류
# ------------------------------------------

def classify_file(filename, text):

    # 공백과 일부 구분문자를 제거해서 비교
    combined = (filename + " " + text)
    normalized = (
        combined
        .replace(" ", "")
        .replace("_", "")
        .replace("·", "")
    )

    # --------------------------------------------------
    # 구체적인 데이터부터 먼저 판별
    # --------------------------------------------------

    # 절도 발생장소 × 수법
    if (
        "절도범죄의발생장소와수법" in normalized
        or ("절도" in normalized and
            "발생장소" in normalized and
            "수법" in normalized)
    ):
        return "절도_장소_수법"

    # 강도·절도·사기 수법
    if (
        "강도절도및사기수법" in normalized
        or (
            "강도" in normalized
            and "절도" in normalized
            and "사기" in normalized
            and "수법" in normalized
        )
    ):
        return "강도절도사기_수법"

    # 발생요일
    if "발생요일" in normalized:
        return "발생요일"

    # 발생시간
    if (
        "발생시간" in normalized
        or "범죄발생시간" in normalized
    ):
        return "발생시간"

    # 발생장소
    if "발생장소" in normalized:
        return "발생장소"

    # 발생 → 인지기간
    if (
        "인지까지의기간" in normalized
        or "인지기간" in normalized
    ):
        return "발생_인지기간"

    # 사건 처리기간
    if "처리기간" in normalized:
        return "사건처리기간"

    # 수사단서
    if "수사단서" in normalized:
        return "수사단서"

    # 검거단서
    if "검거단서" in normalized:
        return "검거단서"

    # 지역별 범죄발생
    if "발생지" in normalized:
        return "지역별_범죄발생"

    # 일반 발생·검거 통계
    if (
        "발생건수" in normalized
        and "검거건수" in normalized
    ):
        return "발생_검거"

    return "미분류"
# ------------------------------------------
# 전체 파일 검사
# ------------------------------------------

records = []

csv_files = sorted(RAW_DIR.glob("*.csv"))

print("=" * 75)
print("CSI LAB - DATA CLASSIFICATION")
print("=" * 75)
print(f"CSV 파일 수 : {len(csv_files)}")


for i, path in enumerate(csv_files, start=1):

    df, encoding, preview_text = read_preview(path)

    sha256 = get_sha256(path)

    if df is None:

        category = "읽기실패"
        rows = None
        cols = None

    else:

        category = classify_file(
            path.name,
            preview_text
        )

        rows = len(df)
        cols = len(df.columns)

    records.append({
        "파일명": path.name,
        "데이터분류": category,
        "인코딩": encoding,
        "행수": rows,
        "열수": cols,
        "SHA256": sha256
    })

    print(
        f"[{i:02d}/{len(csv_files):02d}] "
        f"{category:<18} "
        f"{path.name}"
    )


# ------------------------------------------
# DataFrame
# ------------------------------------------

result = pd.DataFrame(records)


# ------------------------------------------
# 중복 검사
# ------------------------------------------

result["중복여부"] = result.duplicated(
    subset=["SHA256"],
    keep=False
)

result["중복그룹"] = ""

duplicate_hashes = (
    result.loc[result["중복여부"], "SHA256"]
    .drop_duplicates()
    .tolist()
)

for number, sha in enumerate(duplicate_hashes, start=1):

    result.loc[
        result["SHA256"] == sha,
        "중복그룹"
    ] = f"DUP_{number:02d}"


# ------------------------------------------
# 저장
# ------------------------------------------

output = PROCESSED_DIR / "crime_file_classification.csv"

result.to_csv(
    output,
    index=False,
    encoding="utf-8-sig"
)


# ------------------------------------------
# 화면 출력
# ------------------------------------------

print("\n" + "=" * 75)
print("데이터 분류 결과")
print("=" * 75)

print(
    result[
        [
            "파일명",
            "데이터분류",
            "행수",
            "열수",
            "중복여부",
            "중복그룹"
        ]
    ].to_string(index=False)
)


print("\n" + "=" * 75)
print("분류별 파일 수")
print("=" * 75)

print(result["데이터분류"].value_counts())


print("\n" + "=" * 75)
print("중복 파일")
print("=" * 75)

duplicates = result[result["중복여부"]]

if len(duplicates) == 0:
    print("중복 파일 없음")
else:
    print(
        duplicates[
            ["파일명", "중복그룹"]
        ].to_string(index=False)
    )


print("\n저장 완료:")
print(output)