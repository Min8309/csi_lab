from pathlib import Path
import pandas as pd


# ==========================================
# 1. 경로 설정
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw" / "crime"
PROCESSED_DIR = BASE_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. CSV 자동 읽기
# ==========================================

def read_csv_auto(file_path):

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp949",
        "euc-kr"
    ]

    for encoding in encodings:

        try:

            df = pd.read_csv(
                file_path,
                encoding=encoding,
                low_memory=False
            )

            return df, encoding

        except UnicodeDecodeError:
            continue

        except Exception as e:
            print(f"  {encoding} 읽기 오류: {e}")
            continue

    return None, None


# ==========================================
# 3. CSV 파일 검색
# ==========================================

csv_files = sorted(RAW_DIR.glob("*.csv"))

print("=" * 70)
print("CSI LAB - RAW CRIME DATA CHECK")
print("=" * 70)

print(f"RAW 폴더 : {RAW_DIR}")
print(f"CSV 파일 수 : {len(csv_files)}개")


# ==========================================
# 4. 파일 검사
# ==========================================

results = []

for i, file_path in enumerate(csv_files, start=1):

    print("\n" + "=" * 70)
    print(f"[{i}/{len(csv_files)}] {file_path.name}")
    print("=" * 70)

    df, encoding = read_csv_auto(file_path)

    if df is None:

        print("❌ 읽기 실패")

        results.append({
            "파일명": file_path.name,
            "인코딩": "읽기 실패",
            "행수": None,
            "열수": None
        })

        continue

    print(f"인코딩 : {encoding}")
    print(f"크기   : {df.shape}")

    print("\n컬럼 앞 15개:")
    print(df.columns.tolist()[:15])

    print("\n앞 2행:")
    print(df.head(2).to_string())

    results.append({
        "파일명": file_path.name,
        "인코딩": encoding,
        "행수": len(df),
        "열수": len(df.columns)
    })


# ==========================================
# 5. 검사 결과 저장
# ==========================================

result_df = pd.DataFrame(results)

output_file = PROCESSED_DIR / "raw_file_inventory.csv"

result_df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 6. 최종 결과 출력
# ==========================================

print("\n")
print("=" * 70)
print("RAW 데이터 검사 완료")
print("=" * 70)

print(result_df.to_string(index=False))

print("\n검사 결과 저장 위치:")
print(output_file)