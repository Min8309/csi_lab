from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "crime"

FILE1 = RAW_DIR / "135_TX_13501_A048_20260915163340.csv"
FILE2 = RAW_DIR / "135_TX_13501_A048_20260915163423.csv"


def read_csv_auto(path):

    for encoding in [
        "utf-8-sig",
        "utf-8",
        "cp949",
        "euc-kr"
    ]:
        try:
            return pd.read_csv(
                path,
                encoding=encoding
            )
        except UnicodeDecodeError:
            continue

    raise ValueError(f"읽기 실패: {path.name}")


df1 = read_csv_auto(FILE1)
df2 = read_csv_auto(FILE2)


regions1 = (
    df1["발생지별"]
    .dropna()
    .astype(str)
    .str.strip()
    .drop_duplicates()
    .tolist()
)

regions2 = (
    df2["발생지별"]
    .dropna()
    .astype(str)
    .str.strip()
    .drop_duplicates()
    .tolist()
)


print("=" * 80)
print("파일 1")
print("=" * 80)

print("지역 수:", len(regions1))

for i, region in enumerate(regions1, start=1):
    print(f"{i:02d}. {region}")


print("\n" + "=" * 80)
print("파일 2")
print("=" * 80)

print("지역 수:", len(regions2))

for i, region in enumerate(regions2, start=1):
    print(f"{i:02d}. {region}")


set1 = set(regions1)
set2 = set(regions2)


print("\n" + "=" * 80)
print("두 파일 비교")
print("=" * 80)

print("\n파일 1에만 있는 지역:")
print(sorted(set1 - set2))

print("\n파일 2에만 있는 지역:")
print(sorted(set2 - set1))

print("\n두 파일 공통 지역 수:")
print(len(set1 & set2))


print("\n" + "=" * 80)
print("범죄 종류 비교")
print("=" * 80)

crimes1 = set(
    df1["범죄별"]
    .dropna()
    .astype(str)
    .str.strip()
)

crimes2 = set(
    df2["범죄별"]
    .dropna()
    .astype(str)
    .str.strip()
)

print("파일 1 범죄 수:", len(crimes1))
print("파일 2 범죄 수:", len(crimes2))

print("\n파일 1에만 있는 범죄:")
print(sorted(crimes1 - crimes2))

print("\n파일 2에만 있는 범죄:")
print(sorted(crimes2 - crimes1))