
import pandas as pd
import streamlit as st
from ultralytics import YOLO
from pathlib import Path
from PIL import Image

import base64

@st.cache_resource
def load_yolo_model():
    return YOLO("yolo11n.pt")

yolo_model = load_yolo_model()

YOLO_KR_NAMES = {
    "person": "사람",
    "backpack": "가방",
    "handbag": "손가방",
    "suitcase": "여행가방",
    "cell phone": "휴대전화",
    "laptop": "노트북",
    "cup": "컵",
    "bottle": "병",
    "chair": "의자",
    "couch": "소파",
    "tv": "TV",
    "remote": "리모컨",
    "book": "책",
    "potted plant": "화분",
    "car": "자동차",
    "motorcycle": "오토바이",
    "bus": "버스",
    "truck": "트럭",
    "bicycle": "자전거"
}


BASE_DIR = Path(__file__).resolve().parent

PROCESSED_DIR = BASE_DIR / "processed"

REGION_DATA_PATH = (
    PROCESSED_DIR
    / "region_crime_final_1994_2024.csv"
)
# =========================================================
# 기본 설정
# =========================================================




# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="CSI LAB",
    page_icon="🔎",
    layout="wide"
)
# =========================================================
# CSI LAB UI THEME
# poster.png 배경 + Dark Investigation Style
# =========================================================

BACKGROUND_IMAGE = BASE_DIR / "img" / "poster.png"

if BACKGROUND_IMAGE.exists():

    with open(BACKGROUND_IMAGE, "rb") as image_file:
        encoded_image = base64.b64encode(
            image_file.read()
        ).decode()

    st.markdown(
        f"""
        <style>

        /* ================================================
           1. STREAMLIT 기본 여백
           ================================================ */

        .block-container {{
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 4rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }}


        /* ================================================
           2. 전체 배경 - 기존 poster.png 유지
           ================================================ */

        [data-testid="stAppViewContainer"] {{
            background-image:
                linear-gradient(
                    rgba(2, 8, 15, 0.58),
                    rgba(2, 8, 15, 0.88)
                ),
                url("data:image/png;base64,{encoded_image}");

            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}


        /* ================================================
           3. Streamlit 상단 헤더
           ================================================ */

        [data-testid="stHeader"] {{
            background: rgba(0, 0, 0, 0);
        }}


        /* ================================================
           4. 메인 콘텐츠 영역
           기존 흰색 박스 제거
           ================================================ */

        [data-testid="stMainBlockContainer"] {{
            background: rgba(2, 8, 15, 0.42);

            border: 1px solid rgba(94, 183, 230, 0.12);

            border-radius: 4px;

            padding: 2.5rem 3rem 4rem 3rem;

            margin-top: 1rem;
            margin-bottom: 3rem;

            box-shadow:
                0 20px 60px rgba(0, 0, 0, 0.45);

            backdrop-filter: blur(3px);
        }}


        /* ================================================
           5. 기본 글씨
           ================================================ */

        [data-testid="stMainBlockContainer"] p {{
            color: #c9d4df;
            font-weight: 400;
        }}


        /* ================================================
           6. 제목
           ================================================ */

        [data-testid="stMainBlockContainer"] h1 {{
            color: #f4f8fb;
            font-weight: 800;
            letter-spacing: 5px;
        }}

        [data-testid="stMainBlockContainer"] h2 {{
            color: #eef7fc;
            font-weight: 700;
            letter-spacing: 2px;
        }}

        [data-testid="stMainBlockContainer"] h3 {{
            color: #e8f4fa;
            font-weight: 650;
        }}


        /* ================================================
           7. Caption
           ================================================ */

        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] p {{
            color: #8fa8ba !important;
            opacity: 1 !important;
            font-weight: 500 !important;
            letter-spacing: 0.5px;
        }}


        /* ================================================
           8. 입력창 라벨
           ================================================ */

        [data-testid="stWidgetLabel"] p {{
            color: #c8d7e2 !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }}


                /* ================================================
           9. Selectbox
           ================================================ */

        /* 닫힌 선택창 */
        div[data-baseweb="select"] > div {{
            background-color: #f4f6f8 !important;
            border: 1px solid rgba(91, 190, 238, 0.55) !important;
        }}

        /* 선택된 값 - 핵심 */
        div[data-baseweb="select"] div[aria-selected="true"] {{
            color: #07131e !important;
        }}

        div[data-baseweb="select"] div[aria-selected="true"] * {{
            color: #07131e !important;
        }}

        /* Streamlit Selectbox 선택값 */
        div[data-baseweb="select"] > div > div {{
            color: #07131e !important;
            -webkit-text-fill-color: #07131e !important;
            opacity: 1 !important;
        }}

        div[data-baseweb="select"] > div > div > div {{
            color: #07131e !important;
            -webkit-text-fill-color: #07131e !important;
            opacity: 1 !important;
        }}

        /* input이 사용되는 Streamlit 버전 대응 */
        div[data-baseweb="select"] input {{
            color: #07131e !important;
            -webkit-text-fill-color: #07131e !important;
            opacity: 1 !important;
        }}

        /* 화살표 */
        div[data-baseweb="select"] svg {{
            fill: #123247 !important;
            color: #123247 !important;
        }}

        /* 펼쳐진 메뉴 */
        [data-baseweb="popover"] {{
            background-color: #07131e !important;
        }}

        [role="listbox"] {{
            background-color: #07131e !important;
        }}

        [role="option"] {{
            background-color: #07131e !important;
            color: #ffffff !important;
        }}

        [role="option"] * {{
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }}

        [role="option"]:hover {{
            background-color: #123247 !important;
        }}

      

        /* ================================================
           10. CASE / EVIDENCE 카드
           ================================================ */

        [data-testid="stVerticalBlockBorderWrapper"] {{
            background:
                linear-gradient(
                    180deg,
                    rgba(7, 18, 29, 0.88),
                    rgba(3, 9, 16, 0.95)
                );

            border:
                1px solid rgba(105, 176, 214, 0.25) !important;

            border-radius: 3px;

            padding: 14px;

            box-shadow:
                0 12px 30px rgba(0, 0, 0, 0.40);

            transition:
                transform 0.25s ease,
                border 0.25s ease,
                box-shadow 0.25s ease;
        }}


        /* CASE 카드 Hover */

        [data-testid="stVerticalBlockBorderWrapper"]:hover {{
            transform: translateY(-6px);

            border:
                1px solid rgba(91, 200, 255, 0.85) !important;

            box-shadow:
                0 0 22px rgba(62, 177, 235, 0.20),
                0 18px 40px rgba(0, 0, 0, 0.55);
        }}


        /* ================================================
           11. 카드 안 글씨
           ================================================ */

        [data-testid="stVerticalBlockBorderWrapper"] p {{
            color: #b9c9d4 !important;
        }}

        [data-testid="stVerticalBlockBorderWrapper"] h3 {{
            color: #ffffff !important;
        }}


        /* ================================================
           12. 버튼
           ================================================ */

        [data-testid="stButton"] button {{
            background: rgba(5, 15, 24, 0.90);

            color: #d9f2ff;

            border:
                1px solid rgba(102, 192, 235, 0.55);

            border-radius: 2px;

            min-height: 44px;

            font-weight: 650;

            letter-spacing: 1px;

            transition: all 0.20s ease;
        }}


        [data-testid="stButton"] button:hover {{
            background: rgba(20, 91, 125, 0.40);

            color: #ffffff;

            border-color: #63c8f5;

            box-shadow:
                0 0 18px rgba(75, 190, 240, 0.30);
        }}


        /* ================================================
           13. Metric
           ================================================ */

        [data-testid="stMetric"] {{
            background: rgba(4, 14, 23, 0.82);

            border:
                1px solid rgba(88, 170, 210, 0.20);

            padding: 15px;

            border-radius: 3px;
        }}

        [data-testid="stMetricLabel"] {{
            color: #8ca8b9;
        }}

        [data-testid="stMetricValue"] {{
            color: #edf8ff;
        }}


        /* ================================================
           14. 구분선
           ================================================ */

        hr {{
            border-color:
                rgba(91, 176, 220, 0.18) !important;
        }}


        /* ================================================
           15. 입력창
           ================================================ */

        textarea,
        input {{
            color: #edf7fc !important;
        }}


        /* ================================================
           16. Alert / Info
           ================================================ */

        [data-testid="stAlert"] {{
            background:
                rgba(6, 22, 34, 0.88);

            color: #d7e8f2;

            border:
                1px solid rgba(91, 176, 220, 0.20);
        }}


        /* ================================================
           17. 모바일
           ================================================ */

        @media (max-width: 900px) {{

            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}

            [data-testid="stMainBlockContainer"] {{
                padding: 1.5rem;
            }}
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 데이터 경로
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "processed"

# 기존 30Y Time Machine 데이터
DATA_FILE = (
    PROCESSED_DIR
    / "csi_time_machine_1990_2022.csv"
)

# 지역 범죄 데이터
REGION_DATA_PATH = (
    PROCESSED_DIR
    / "region_crime_final_1994_2024.csv"
)


# =========================================================
# 기존 30Y Time Machine 데이터 로딩
# =========================================================

@st.cache_data
def load_data():

    return pd.read_csv(
        DATA_FILE,
        encoding="utf-8-sig"
    )


df = load_data()

core_df = df[
    df["core_time_machine"] == True
].copy()


# =========================================================
# 지역 범죄 데이터 로딩
# =========================================================

@st.cache_data
def load_region_data():

    region_data = pd.read_csv(
        REGION_DATA_PATH,
        encoding="utf-8-sig"
    )

    region_data["year"] = pd.to_numeric(
        region_data["year"],
        errors="coerce"
    )

    region_data["occurrence_count"] = pd.to_numeric(
        region_data["occurrence_count"],
        errors="coerce"
    )

    return region_data


region_df = load_region_data()
# =========================================================
# CASE 정보
# =========================================================

CASE_INFO = {
    "CASE-BURGLARY": {
        "title": "심야의 침입자",
        "crime": "야간주거침입절도",
        "description": (
            "새벽 시간 발생한 침입 사건. "
            "현장에 남겨진 단서를 조사하세요."
        ),
        "region_crime": "절도",
        "cctv_image": "cctv_burglary.png"
    },

    "CASE-ROBBERY": {
        "title": "사라진 가방",
        "crime": "강도",
        "description": (
            "피해자의 가방이 사라졌습니다. "
            "현장의 단서와 실제 데이터를 비교하세요."
            
        ),
        "region_crime": "강도",
        "cctv_image": "cctv_robbery.png"
    },

    "CASE-ARSON": {
        "title": "불길 속의 흔적",
        "crime": "방화",
        "description": (
            "화재 현장에 남은 흔적을 조사하고 "
            "관련 범죄 데이터를 확인하세요."
        ),
        "region_crime": "방화",
        "cctv_image": "cctv_arson.png"
    },

    "CASE-FRAUD": {
        "title": "의문의 거래",
        "crime": "사기",
        "description": (
            "수상한 거래 기록이 발견되었습니다. "
            "데이터 속 패턴을 추적하세요."
        ),
        "region_crime": "사기",
        "cctv_image": "cctv_fraud.png"
    }
}
WITNESS_DATA = {
    "CASE-BURGLARY": {
        "intro": "늦은 시간에 현장 근처에서 누군가 빠르게 이동하는 모습을 봤습니다.",
        "time": "정확하지는 않지만 자정 무렵이었던 것 같습니다.",
        "object": "한쪽 어깨에 어두운색 가방을 메고 있었던 것 같습니다.",
        "direction": "건물 뒤편 골목 방향으로 빠르게 이동했습니다."
    },

    "CASE-ROBBERY": {
        "intro": "현장 근처에서 한 사람이 급하게 뛰어가는 모습을 봤습니다.",
        "time": "밤 10시쯤이었던 것으로 기억합니다.",
        "object": "가방처럼 보이는 물건을 들고 있었습니다.",
        "direction": "대로변 쪽으로 뛰어갔습니다."
    },

    "CASE-ARSON": {
        "intro": "연기가 보이기 전에 건물 근처에서 사람 한 명을 봤습니다.",
        "time": "불이 보이기 약 10분 전쯤이었던 것 같습니다.",
        "object": "손에 작은 가방 같은 것이 있었지만 정확히 보지는 못했습니다.",
        "direction": "건물 뒤쪽으로 이동했습니다."
    },

    "CASE-FRAUD": {
        "intro": "건물 근처에서 누군가 서류를 들고 이동하는 모습을 봤습니다.",
        "time": "점심시간이 지난 오후였던 것 같습니다.",
        "object": "서류봉투 같은 것을 들고 있었습니다.",
        "direction": "건물 출입구 쪽으로 이동했습니다."
    }
}
# =========================================================
# 🛡 SAFETY LAB 예방 행동 가이드
# =========================================================

SAFETY_GUIDE = {
    "절도": [
        "외출 전 출입문과 창문의 잠금 상태를 확인하세요.",
        "귀중품은 외부에서 쉽게 보이지 않도록 보관하세요.",
        "공동출입구의 문이 열린 채 방치되지 않도록 확인하세요.",
        "의심스러운 상황에서는 직접 대응하기보다 안전한 장소에서 신고하세요."
    ],

    "강도": [
        "늦은 시간에는 주변이 잘 보이고 통행이 있는 경로를 이용하세요.",
        "귀중품을 외부에 과도하게 노출하지 않도록 주의하세요.",
        "위협 상황에서는 물건을 지키기 위해 무리하게 대응하지 마세요.",
        "안전한 장소로 이동한 뒤 필요한 경우 경찰에 신고하세요."
    ],

    "방화": [
        "건물의 비상구와 대피 경로를 미리 확인하세요.",
        "화재를 발견하면 주변에 알리고 안전한 장소로 우선 대피하세요.",
        "직접 진압하기 어려운 화재에는 무리하게 접근하지 마세요.",
        "화재 발생 시 안전한 장소에서 119에 신고하세요."
    ],

    "사기": [
        "금전이나 개인정보를 요구하는 연락은 발신자를 다시 확인하세요.",
        "의심스러운 링크나 첨부파일을 바로 열지 마세요.",
        "송금 전 상대방과 거래 정보를 별도의 방법으로 확인하세요.",
        "피해가 의심되면 관련 금융기관이나 신고기관에 신속히 문의하세요."
    ]
}
# =========================================================
# 게임 페이지 상태
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_case" not in st.session_state:
    st.session_state.selected_case = None

if "investigation_started" not in st.session_state:
    st.session_state.investigation_started = False


# =========================================================
# 기존 게임 상태
# =========================================================

if "evidence_found" not in st.session_state:
    st.session_state.evidence_found = False

if "investigation_view" not in st.session_state:
    st.session_state.investigation_view = None

if "collected_evidence" not in st.session_state:
    st.session_state.collected_evidence = []

    
if "hypothesis" not in st.session_state:
    st.session_state.hypothesis = ""

if "final_deduction" not in st.session_state:
    st.session_state.final_deduction = ""

if "case_submitted" not in st.session_state:
    st.session_state.case_submitted = False

if "evidence_comparison_found" not in st.session_state:
    st.session_state.evidence_comparison_found = False
# =========================================================
# 게임 페이지 이동 함수
# =========================================================

def open_case(case_code):
    st.session_state.selected_case = case_code
    st.session_state.page = "case_setup"
    st.session_state.investigation_started = False
    st.session_state.investigation_view = None
    st.session_state.collected_evidence = []


def go_home():
    st.session_state.page = "home"
    st.session_state.selected_case = None
    st.session_state.investigation_started = False
    st.session_state.evidence_found = False
    st.session_state.investigation_view = None
    st.session_state.collected_evidence = []
    st.session_state.evidence_comparison_found = False



# =========================================================
# HOME — CSI LAB CASE FILES
# =========================================================

if st.session_state.page == "home":

    # =====================================================
    # HERO
    # =====================================================

    hero_html = (
        '<div style="text-align:center; padding:55px 10px 40px 10px;">'
        '<div style="color:#72b9dd; font-size:13px; letter-spacing:8px; margin-bottom:18px;">'
        'CRIME · DATA · SOLUTION'
        '</div>'
        '<div style="color:#ffffff; font-size:64px; font-weight:800; letter-spacing:9px; line-height:1;">'
        'CSI LAB'
        '</div>'
        '<div style="width:90px; height:2px; margin:26px auto; background:#55b9e8;"></div>'
        '<div style="color:#d7e2e9; font-size:17px; letter-spacing:2px; line-height:1.8;">'
        '데이터 속 단서를 찾아,<br>더 안전한 세상을 만들어가세요.'
        '</div>'
        '</div>'
    )

    st.markdown(
        hero_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # CASE FILES TITLE
    # =====================================================
    case_title_html = (
        '<div style="text-align:center; margin:20px 0 35px 0;">'
        '<div style="color:#789bad; font-size:11px; letter-spacing:6px; margin-bottom:10px;">'
        'SELECT YOUR INVESTIGATION'
        '</div>'
        '<div style="color:#ffffff; font-size:27px; font-weight:700; letter-spacing:6px;">'
        'CASE FILES'
        '</div>'
        '<div style="color:#8fa5b2; font-size:13px; margin-top:12px;">'
        '4개의 사건 중 하나를 선택해 수사를 시작하세요.'
        '</div>'
        '</div>'
    )

    st.markdown(
        case_title_html,
        unsafe_allow_html=True
    )

    # =====================================================
    # 4 CASE CARDS
    # =====================================================

    cols = st.columns(
        4,
        gap="medium"
    )

    for case_number, (
        col,
        (case_id, info)
    ) in enumerate(
        zip(
            cols,
            CASE_INFO.items()
        ),
        start=1
    ):

        with col:

            with st.container(
                border=True
            ):

                # CASE 번호
                st.markdown(
                    f"""
<div style="
    color:#64c8f5;
    font-size:11px;
    letter-spacing:3px;
    margin-bottom:12px;">
    CASE {case_number:02d}
</div>
""",
                    unsafe_allow_html=True
                )

                # 사건 제목
                st.markdown(
                    f"""
<div style="
    color:#ffffff;
    font-size:22px;
    font-weight:700;
    min-height:62px;
    line-height:1.4;">
    {info["title"]}
</div>
""",
                    unsafe_allow_html=True
                )

                # 범죄 유형
                st.markdown(
                    f"""
<div style="
    color:#66b8df;
    font-size:11px;
    letter-spacing:1px;
    margin:4px 0 17px 0;">
    {info["crime"]}
</div>
""",
                    unsafe_allow_html=True
                )

                # 사건 설명
                st.markdown(
                    f"""
<div style="
    color:#b4c1c9;
    font-size:13px;
    line-height:1.8;
    min-height:100px;">
    {info["description"]}
</div>
""",
                    unsafe_allow_html=True
                )

                # 카드 장식선
                st.markdown(
                    """
<div style="
    height:1px;
    margin:14px 0 17px 0;
    background:linear-gradient(
        90deg,
        rgba(80,190,240,0.7),
        rgba(80,190,240,0.03)
    );">
</div>
""",
                    unsafe_allow_html=True
                )

                # CASE START
                if st.button(
                    "CASE START  →",
                    key=f"start_{case_id}",
                    use_container_width=True
                ):
                    open_case(case_id)
                    st.rerun()

    # =====================================================
    # FOOTER
    # =====================================================
    footer_html = (
        '<div style="text-align:center; margin-top:55px; padding-top:25px; '
        'padding-bottom:10px; border-top:1px solid rgba(100,190,230,0.15);">'
        '<span style="color:#7893a3; font-size:10px; letter-spacing:4px;">'
        'REAL DATA · REAL CASE ANALYSIS · SAFER TOMORROW'
        '</span>'
        '</div>'
    )

    st.markdown(
        footer_html,
        unsafe_allow_html=True
    )
# =========================================================
# 선택된 사건
# =========================================================

if (
    st.session_state.page == "case_setup"
    and st.session_state.selected_case
):
    if st.button(
        "← CASE 목록으로",
        key="back_to_home"
    ):
        go_home()
        st.rerun()

    case_id = st.session_state.selected_case

    case = CASE_INFO[case_id]

    crime_name = case["crime"]

    st.divider()

    st.subheader(
        f"📁 CASE FILE — {case['title']}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "CASE CODE",
        case_id
    )

    col2.metric(
        "분석 범죄",
        crime_name
    )

    col3.metric(
        "데이터 기간",
        "1990–2022"
    )
         # =====================================================
    # 사건 발생 지역 선택
    # =====================================================

    st.divider()

    st.subheader("📍 사건 발생 지역 선택")

    st.write(
        "이번 사건이 발생한 지역을 선택하세요."
    )

    city_list = sorted(
        region_df["city"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_city = st.selectbox(
        "도시 선택",
        city_list,
        index=(
            city_list.index("서울특별시")
            if "서울특별시" in city_list
            else 0
        ),
        key="setup_city"
    )

    city_df = region_df[
        region_df["city"] == selected_city
    ].copy()

    district_list = sorted(
        city_df["district"]
        .dropna()
        .unique()
        .tolist()
    )

    default_district = (
        "용산구"
        if selected_city == "서울특별시"
        and "용산구" in district_list
        else district_list[0]
    )

    selected_district = st.selectbox(
        "구·군 선택",
        district_list,
        index=district_list.index(
            default_district
        ),
        key="setup_district"
    )

    region_crime = case["region_crime"]

    st.info(
        f"이번 CASE의 실제 데이터 분석 범죄: "
        f"**{region_crime}**"
    )

    # =====================================================
    # 선택한 사건 지역 저장
    # =====================================================

    if st.button(
        "🚨 사건 시작",
        type="primary",
        use_container_width=True,
        key="start_investigation"
    ):

        st.session_state.case_city = selected_city
        st.session_state.case_district = selected_district

        st.session_state.investigation_started = True
        st.session_state.page = "investigation"

        st.session_state.evidence_found = False
        st.session_state.investigation_view = None
        st.session_state.collected_evidence = []

        st.rerun()
# =========================================================
# INVESTIGATION PAGE
# =========================================================

if (
    st.session_state.page == "investigation"
    and st.session_state.selected_case
):

    case_id = st.session_state.selected_case
    case = CASE_INFO[case_id]

    crime_name = case["crime"]
    region_crime = case["region_crime"]

    case_city = st.session_state.get(
        "case_city",
        "지역 미선택"
    )

    case_district = st.session_state.get(
        "case_district",
        "지역 미선택"
    )

    # -----------------------------------------------------
    # 상단 네비게이션
    # -----------------------------------------------------

    if st.button(
        "← CASE 설정으로",
        key="back_to_case_setup"
    ):
        st.session_state.page = "case_setup"
        st.session_state.investigation_started = False
        st.rerun()

    st.divider()

    # -----------------------------------------------------
    # 사건 발생
    # -----------------------------------------------------

    st.header(
        f"🚨 CASE INVESTIGATION — {case['title']}"
    )

    st.success(
        f"사건이 시작되었습니다. "
        f"현장: {case_city} {case_district}"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "CASE CODE",
        case_id
    )

    col2.metric(
        "사건 유형",
        crime_name
    )

    col3.metric(
        "사건 지역",
        f"{case_city} {case_district}"
    )

    st.info(
        f"📊 이 사건과 연결되는 실제 지역 통계 범죄: "
        f"**{region_crime}**"
    )
    # =====================================================
    # Evidence LAB
    # =====================================================

    st.subheader(
        "🔎 Evidence LAB"
    )

    st.info(
        "현장 증거를 조사하세요. "
        "현재 버전은 샘플 Evidence입니다. "
        "다음 단계에서 YOLO 객체 탐지를 연결합니다."
    )

    e1, e2, e3 = st.columns(3)

    with e1:

        st.markdown("### 📷 CCTV")

        st.write(
            "사건 발생 시간대의 "
            "CCTV 기록을 조사합니다."
        )

        if st.button(
            "CCTV 조사",
            key="investigate_cctv",
            use_container_width=True
        ):
            st.session_state.investigation_view = "cctv"
            st.rerun()


    with e2:

        st.markdown("### 🎒 현장 물체")

        st.write(
            "현장에서 발견된 "
            "물체를 확인합니다."
        )

        if st.button(
            "물체 조사",
             key="investigate_object",
             use_container_width=True
        ):
            st.session_state.investigation_view = "object"
            st.rerun()

    with e3:

        st.markdown("### 🕒 사건 시간")

        st.write(
            "사건 발생 시간과 "
            "관련 기록을 조사합니다."
        )

        if st.button(
            "시간 조사",
            key="investigate_time",
            use_container_width=True
        ):
            st.session_state.investigation_view = "time"
            st.rerun()

        st.write("")

    col4, col5, col6 = st.columns(3)

    with col4:

        st.markdown("### 📝 목격자")

        st.write(
            "사건 당시 목격자의 진술을 확인합니다."
        )

        if st.button(
            "목격자 조사",
            key="investigate_witness",
            use_container_width=True
        ):
            st.session_state.investigation_view = "witness"
            st.rerun()


    with col5:

        st.markdown("### 📊 지역 DATA")

        st.write(
            "사건 지역의 실제 범죄 통계를 조사합니다."
        )

        if st.button(
            "지역 데이터 조사",
            key="investigate_region",
            use_container_width=True
        ):
            st.session_state.investigation_view = "region"
            st.rerun()


    with col6:

        st.markdown("### 📁 과거 사건기록")

        st.write(
            "관련 범죄의 과거 기록을 조사합니다."
        )

        if st.button(
            "과거 기록 조사",
            key="investigate_history",
            use_container_width=True
        ):
            st.session_state.investigation_view = "history"
            st.rerun()
    # =====================================================
    # 🕒 사건 시간 조사 결과
    # =====================================================

    if st.session_state.investigation_view == "time":

        st.divider()

        st.subheader("🕒 TIME EVIDENCE LAB")

        st.caption(
                "※ 아래 사건 시간은 CSI LAB 게임을 위한 "
                "가상화된 사건 정보입니다."
            )

        st.info(
                f"{case_city} {case_district} 사건의 "
                "발생 추정 시간대를 조사합니다."
            )

        st.markdown("### ⏱ 사건 발생 추정 시간")

        col_start, col_end = st.columns(2)

        with col_start:
            start_time = st.time_input(
                "시작 시간",
                key="case_start_time"
            )

        with col_end:
            end_time = st.time_input(
                "종료 시간",
                key="case_end_time"
            )

        # 사용자가 선택한 시간을 문자열로 변환
        time_text = (
            f"{start_time.strftime('%H:%M')} ~ "
            f"{end_time.strftime('%H:%M')}"
        )

        # 현재 선택한 시간에 맞는 증거 이름 생성
        current_time_evidence = (
            f"시간 단서: {time_text}"
        )

        st.info(
            f"🕒 현재 설정한 사건 발생 추정 시간: "
            f"**{time_text}**"
        )

        st.caption(
            "※ 이 시간은 실제 범죄 발생 기록이 아니라 "
            "CSI LAB 가상 CASE에서 사용자가 설정한 추정 시간입니다."
        )

        if st.button(
            "🧩 시간 단서 수집",
            key="collect_time_evidence",
            use_container_width=True
        ):

            if (
                current_time_evidence
                not in st.session_state.collected_evidence
            ):
                st.session_state.collected_evidence.append(
                    current_time_evidence
                )

            st.rerun()

        if (
            current_time_evidence
            in st.session_state.collected_evidence
        ):

            st.success(
                "✅ 사건 시간 단서를 수집했습니다."
            )

            st.markdown(
                f"""
                **수집된 단서**

                - 발생 추정 시간: {time_text}
                - 사용자가 설정한 CASE 사건 시간
                - 다른 증거와 비교 분석 필요
                """
            )
       # =====================================================
    # 📷 CCTV 조사 결과
    # =====================================================

    if st.session_state.investigation_view == "cctv":

        st.divider()

        st.subheader("📷 CCTV EVIDENCE")

        st.caption(
            "※ 아래 CCTV 이미지와 내용은 CSI LAB 게임을 위한 "
            "가상화된 사건 증거입니다."
        )

        st.info(
            f"{case_city} {case_district} 사건 현장 주변의 "
            "CCTV 기록을 분석합니다."
        )

        st.markdown("### 🎞 CCTV 기록 #01")

        # -------------------------------------------------
        # 현재 CASE에 연결된 CCTV 이미지
        # -------------------------------------------------

        cctv_filename = case["cctv_image"]

        cctv_path = (
            BASE_DIR
            / "img"
            / cctv_filename
        )

        if cctv_path.exists():

            st.image(
                str(cctv_path),
                caption=(
                    f"{case['title']} · "
                    "가상 CCTV 조사 화면"
                ),
                use_container_width=True
            )

        else:

            st.warning(
                f"CCTV 이미지 파일을 찾을 수 없습니다: "
                f"{cctv_filename}"
            )

        st.write(
            "사건 발생 추정 시간대에 현장 주변을 지나가는 "
            "인물과 물체가 기록되어 있습니다."
        )

        st.write(
            "영상 속에서 사건과 관련될 가능성이 있는 "
            "시각적 단서를 확인하세요."
        )
                # -------------------------------------------------
        # 🔬 YOLO CCTV 분석
        # -------------------------------------------------

        st.markdown("### 🔬 AI CCTV OBJECT ANALYSIS")

        st.caption(
            "YOLO는 영상 속에서 관찰 가능한 객체만 탐지합니다. "
            "탐지된 객체가 사건과 관련 있다는 의미는 아닙니다."
        )

        if st.button(
            "🔬 YOLO CCTV 분석",
            key=f"analyze_cctv_yolo_{case_id}",
            use_container_width=True
        ):

            if cctv_path.exists():

                with st.spinner(
                    "CCTV 프레임에서 객체를 탐지하고 있습니다..."
                ):

                    results = yolo_model(
                        str(cctv_path)
                    )

                    result = results[0]

                    # YOLO 박스가 그려진 이미지
                    annotated_image = result.plot()

                    # BGR → RGB
                    annotated_image = annotated_image[:, :, ::-1]

                    # 탐지 객체 저장
                    detected_objects = []

                    for box in result.boxes:

                        class_id = int(
                            box.cls[0].item()
                        )

                        confidence = float(
                            box.conf[0].item()
                        )

                        object_name = result.names[
                            class_id
                        ]

                        object_name_kr = YOLO_KR_NAMES.get(
                            object_name,
                            object_name
                        )

                        detected_objects.append({
                            "name": object_name,
                            "name_kr": object_name_kr,
                            "confidence": confidence
                        })

                    st.session_state.cctv_yolo_image = (
                        annotated_image
                    )

                    st.session_state.cctv_yolo_objects = (
                        detected_objects
                    )

            st.rerun()
                # -------------------------------------------------
        # YOLO 분석 결과 표시
        # -------------------------------------------------

        if "cctv_yolo_image" in st.session_state:

            st.success(
                "✅ CCTV 객체 탐지가 완료되었습니다."
            )

            st.image(
                st.session_state.cctv_yolo_image,
                caption="YOLO CCTV 객체 탐지 결과",
                use_container_width=True
            )

            detected_objects = (
                st.session_state.get(
                    "cctv_yolo_objects",
                    []
                )
            )

            if detected_objects:

                st.markdown("#### 🔎 탐지된 객체")

                                # 같은 종류의 객체끼리 묶기
                grouped_objects = {}

                for obj in detected_objects:

                    object_name = obj["name"]

                    if object_name not in grouped_objects:
                        grouped_objects[object_name] = {
                            "name": object_name,
                            "name_kr": obj["name_kr"],
                            "count": 0,
                            "max_confidence": 0
                        }

                    grouped_objects[object_name]["count"] += 1

                    grouped_objects[object_name]["max_confidence"] = max(
                        grouped_objects[object_name]["max_confidence"],
                        obj["confidence"]
                    )

                # 묶은 객체 표시
                for object_name, obj in grouped_objects.items():

                    st.markdown(
                        f"**🔎 {obj['name_kr']} "
                        f"({obj['name']})**"
                    )

                    st.write(
                        f"탐지 수: {obj['count']}개 · "
                        f"최고 신뢰도: "
                        f"{obj['max_confidence']:.0%}"
                    )

                    evidence_name = (
                        f"CCTV YOLO 탐지: "
                        f"{obj['name_kr']} "
                        f"({obj['count']}개)"
                    )

                    if st.button(
                        f"🧩 {obj['name_kr']} 증거 후보 수집",
                        key=(
                            f"collect_cctv_yolo_"
                            f"{case_id}_{object_name}"
                        ),
                        use_container_width=True
                    ):

                        if (
                            evidence_name
                            not in
                            st.session_state.collected_evidence
                        ):
                            st.session_state.collected_evidence.append(
                                evidence_name
                            )

                        st.rerun()

                    if (
                        evidence_name
                        in st.session_state.collected_evidence
                    ):
                        st.success(
                            f"✅ {obj['name_kr']}을 "
                            "시각 증거 후보로 수집했습니다."
                        )

                st.caption(
                    "※ YOLO 객체 탐지는 화면에서 관찰 가능한 "
                    "객체만 식별합니다. 탐지 결과만으로 사건 관련성, "
                    "인물의 역할 또는 범죄 여부를 판단하지 않습니다."
                )

            else:

                st.info(
                    "YOLO가 탐지한 객체가 없습니다."
                )

        # -------------------------------------------------
        # CCTV 기록 수집
        # -------------------------------------------------

        cctv_evidence = (
            f"CCTV 기록: {case['title']} 현장 주변 영상"
        )

        if st.button(
            "🔎 CCTV 단서 발견",
            key="find_cctv_evidence",
            use_container_width=True
        ):

            st.session_state.evidence_found = True

            if (
                cctv_evidence
                not in st.session_state.collected_evidence
            ):
                st.session_state.collected_evidence.append(
                    cctv_evidence
                )

            st.rerun()

        # -------------------------------------------------
        # 수집 완료 표시
        # -------------------------------------------------

        if (
            cctv_evidence
            in st.session_state.collected_evidence
        ):

            st.success(
                "✅ CCTV 기록을 시각 증거로 수집했습니다."
            )

            st.markdown(
                """
                **수집된 단서**

                - 사건 발생 추정 시간대의 CCTV 기록
                - 현장 주변의 인물 또는 물체가 포함된 시각 자료
                - 다른 증거와 비교 분석이 필요한 후보 단서
                """
            )

    if st.session_state.investigation_view == "witness":

        st.divider()
        st.subheader("📝 WITNESS INTERVIEW")

        st.caption(
            "※ 아래 목격자와 진술은 CSI LAB 게임을 위한 "
            "가상화된 사건 정보입니다."
        )

        st.info(
            f"{case_city} {case_district} 사건과 관련된 "
            "목격자 진술을 조사합니다."
        )

        witness = WITNESS_DATA[case_id]

        st.markdown("### 👤 목격자 A")

        st.write(
            f'“{witness["intro"]}”'
        )

        question = st.radio(
            "어떤 질문을 하시겠습니까?",
            [
                "몇 시쯤 목격했나요?",
                "무엇을 들고 있었나요?",
                "어느 방향으로 이동했나요?"
            ],
            key="witness_question"
        )

        if question == "몇 시쯤 목격했나요?":

            answer = witness["time"]

            evidence_name = (
                f"목격자 진술(시간): {answer}"
            )

        elif question == "무엇을 들고 있었나요?":

            answer = witness["object"]

            evidence_name = (
                f"목격자 진술(물체): {answer}"
            )

        else:

            answer = witness["direction"]

            evidence_name = (
                f"목격자 진술(이동): {answer}"
            )

        st.info(
            f"👤 목격자: {answer}"
        )

        if st.button(
            "🧩 현재 진술 수집",
            key="collect_witness_evidence",
            use_container_width=True
        ):

            if (
                evidence_name
                not in st.session_state.collected_evidence
            ):
                st.session_state.collected_evidence.append(
                    evidence_name
                )

            st.rerun()

        if (
            evidence_name
            in st.session_state.collected_evidence
        ):

            st.success(
                "✅ 이 목격자 진술을 증거로 수집했습니다."
            ) 
    # =====================================================
    # 🎒 현장 물체 조사 결과
    # =====================================================

    if st.session_state.investigation_view == "object":

        st.divider()

        st.subheader("🎒 OBJECT EVIDENCE LAB")

        st.caption(
                "※ 아래 내용은 CSI LAB 게임을 위한 "
                "가상화된 사건 증거입니다."
            )

        st.info(
                f"{case_city} {case_district} 사건 현장에서 "
                "발견된 물체를 조사합니다."
            )

        st.markdown("### 🔎 현장 탐색 #01")
        st.write(
                "사건 현장에 남겨진 물체 중 "
                "조사가 필요한 단서를 찾아보세요."
            )
            
            # 🖼 현장 이미지 선택 / 업로드
            # =====================================================

        st.markdown("### 🖼 현장 이미지")

        uploaded_image = st.file_uploader(
                "분석할 현장 이미지를 업로드하세요.",
                type=["jpg", "jpeg", "png"],
                key="object_scene_uploader"
            )

        if uploaded_image is not None:

                # Streamlit UploadedFile → PIL Image 변환
                scene_image = Image.open(
                    uploaded_image
                ).convert("RGB")

                st.image(
                    scene_image,
                    caption="사용자가 업로드한 분석 이미지",
                    use_container_width=True
                )

        else:

                # 기본 CASE 이미지
                scene_image_path = (
                    BASE_DIR / "img" / "object_scene.png"
                )

                scene_image = Image.open(
                    scene_image_path
                ).convert("RGB")

                st.image(
                    scene_image,
                    caption="기본 CASE 현장 이미지 — 가상화된 사건 현장",
                    use_container_width=True
                )

        st.markdown("### 🤖 YOLO Visual Evidence Detector")

        st.caption(
                "이미지에 보이는 일반 객체를 탐지합니다. "
                "YOLO는 범죄 여부나 범인을 판단하지 않습니다."
            )

        if st.button(
                "🤖 YOLO 객체 탐지 시작",
                key="run_yolo_detection",
                use_container_width=True
            ):

                with st.spinner("현장 이미지를 분석하고 있습니다..."):

                    yolo_model = load_yolo_model()

                    results = yolo_model(
                        scene_image,
                        conf=0.25
                    )

                    st.session_state.yolo_result_image = (
                        results[0].plot()
                    )

                    detected_objects = []

                    for box in results[0].boxes:

                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])

                        object_name = (
                            results[0].names[class_id]
                        )

                        detected_objects.append(
                            {
                                "name": object_name,
                                "confidence": confidence
                            }
                        )

                    st.session_state.yolo_objects = (
                        detected_objects
                    )

                st.rerun()

        if "yolo_result_image" in st.session_state:

                st.success(
                    "✅ YOLO 객체 탐지가 완료되었습니다."
                )

                st.image(
                    st.session_state.yolo_result_image,
                    caption="YOLO 객체 탐지 결과",
                    use_container_width=True
                )

                st.markdown("### 🔎 탐지된 객체")

                yolo_objects = st.session_state.get(
                    "yolo_objects",
                    []
                )

                if len(yolo_objects) == 0:

                    st.info(
                        "현재 설정에서 탐지된 객체가 없습니다."
                    )

                else:

                    for number, obj in enumerate(
                        yolo_objects,
                        start=1
                    ):

                        object_name = obj["name"]
                        confidence = obj["confidence"]
                        object_name_kr = YOLO_KR_NAMES.get(
                        object_name,
                        object_name
                    )

                        col_name, col_button = st.columns(
                            [3, 1]
                        )

                        with col_name:

                            st.write(
                                f"**{number}. {object_name_kr}** "
                                f"({object_name}) "
                                f"— 신뢰도 {confidence:.1%}"
                            )

                        with col_button:

                            if st.button(
                                "증거 수집",
                                key=f"collect_yolo_{number}_{object_name}",
                                use_container_width=True
                            ):

                                evidence_name = (
                                    f"YOLO 탐지: {object_name_kr}"
                                )

                                if (
                                    evidence_name
                                    not in
                                    st.session_state.collected_evidence
                                ):
                                    st.session_state.collected_evidence.append(
                                        evidence_name
                                    )

                                st.rerun()

        if st.button(
                "🔎 현장 물체 발견",
                key="find_object_evidence",
                use_container_width=True
            ):

                if "현장 물체" not in st.session_state.collected_evidence:
                    st.session_state.collected_evidence.append(
                        "현장 물체"
                    )

                st.session_state.evidence_found = True
                st.rerun()

        if "현장 물체" in st.session_state.collected_evidence:

                st.success(
                    "✅ 현장에서 조사할 물체를 발견했습니다."
                )

                st.markdown(
                    """
                    **수집된 단서**

                    - 사건 현장에서 발견된 물체
                    - 추가 확인이 필요한 시각적 단서
                    - YOLO 객체 탐지 분석 예정
                    """
                )           
        # =====================================================
    # 🧰 EVIDENCE BOX
    # =====================================================
if  st.session_state.page == "investigation":
    st.divider()

    st.subheader("🧰 EVIDENCE BOX")

    if len(st.session_state.collected_evidence) == 0:

        st.info(
                "아직 수집된 증거가 없습니다. "
                "현장을 조사해 증거를 찾아보세요."
            )

    else:

        st.success(
                f"현재 {len(st.session_state.collected_evidence)}개의 "
                "증거를 수집했습니다."
            )

        for number, evidence in enumerate(
            st.session_state.collected_evidence,
            start=1
            ):

            st.write(
                f"**EVIDENCE {number:02d}** — {evidence}"
            )
    # =====================================================
    # 🔗 EVIDENCE COMPARISON
    # CCTV YOLO ↔ 목격자 진술
    # =====================================================

    st.divider()

    st.subheader("🔗 EVIDENCE COMPARISON")

    st.caption(
        "수집한 CCTV 객체 정보와 목격자 진술을 비교합니다."
    )

    collected = st.session_state.collected_evidence

    # CCTV YOLO 증거
    cctv_yolo_evidence = [
        item for item in collected
        if item.startswith("CCTV YOLO 탐지:")
    ]

    # 목격자 진술 증거
    witness_evidence = [
        item for item in collected
        if item.startswith("목격자 진술")
    ]

    if not cctv_yolo_evidence or not witness_evidence:

        st.info(
            "💡 CCTV YOLO 증거와 목격자 진술을 각각 "
            "1개 이상 수집하면 비교할 수 있습니다."
        )

    else:

        col_compare1, col_compare2 = st.columns(2)

        with col_compare1:

            st.markdown("#### 📷 CCTV 객체")

            for evidence in cctv_yolo_evidence:
                st.write(f"• {evidence}")

        with col_compare2:

            st.markdown("#### 👤 목격자 진술")

            for evidence in witness_evidence:
                st.write(f"• {evidence}")

        if st.button(
            "🔍 두 증거 비교",
            key="compare_cctv_witness",
            use_container_width=True
        ):

            st.session_state.evidence_comparison_found = True
            st.rerun()


    if st.session_state.evidence_comparison_found:

        st.markdown("### 🧠 비교 분석 결과")

        matches = []

        # 가방 관련
        cctv_has_bag = any(
            (
                "가방" in item
                or "backpack" in item
                or "handbag" in item
            )
            for item in cctv_yolo_evidence
        )

        witness_has_bag = any(
            (
                "가방" in item
                or "backpack" in item
                or "handbag" in item
            )
            for item in witness_evidence
        )

        if cctv_has_bag and witness_has_bag:
            matches.append("가방")

        # 자동차 관련
        cctv_has_car = any(
            (
                "자동차" in item
                or "car" in item
            )
            for item in cctv_yolo_evidence
        )

        witness_has_car = any(
            (
                "자동차" in item
                or "차량" in item
                or "car" in item
            )
            for item in witness_evidence
        )

        if cctv_has_car and witness_has_car:
            matches.append("자동차")

        # 오토바이 관련
        cctv_has_motorcycle = any(
            (
                "오토바이" in item
                or "motorcycle" in item
            )
            for item in cctv_yolo_evidence
        )

        witness_has_motorcycle = any(
            (
                "오토바이" in item
                or "motorcycle" in item
            )
            for item in witness_evidence
        )

        if cctv_has_motorcycle and witness_has_motorcycle:
            matches.append("오토바이")

        if matches:

            st.success(
                "🔎 두 조사 결과에서 공통으로 언급되거나 "
                "관찰된 정보가 발견되었습니다."
            )

            for match in matches:
                st.write(f"🔗 공통 관찰 정보: **{match}**")

        else:

            st.warning(
                "현재 수집된 CCTV 객체와 목격자 진술에서 "
                "명확한 공통 관찰 정보는 확인되지 않았습니다."
            )

        st.caption(
            "※ 이 결과는 수집된 단서의 단순 비교입니다. "
            "공통 정보가 사건 관련성, 인물의 역할 또는 "
            "범죄 사실을 입증하지 않습니다."
        )

        # =====================================================
    # 🧠 가설 세우기
    # =====================================================

    st.divider()
    st.subheader("🧠 INVESTIGATION HYPOTHESIS")

    evidence_count = len(
        st.session_state.collected_evidence
    )

    if evidence_count < 3:

        st.info(
            "가설을 세우려면 최소 3개의 증거를 "
            "먼저 수집하세요."
        )

    else:

        st.success(
            f"현재 {evidence_count}개의 증거를 바탕으로 "
            "사건 가설을 세울 수 있습니다."
        )

        hypothesis_input = st.text_area(
            "수집한 증거를 바탕으로 사건에 대한 가설을 작성하세요.",
            value=st.session_state.hypothesis,
            placeholder=(
                "예: 사건은 심야 시간대에 발생했고, "
                "현장에서 발견된 가방과 노트북이 "
                "목격자 진술과 관련되어 있을 가능성이 있다."
            ),
            key="hypothesis_input"
        )

        if st.button(
            "🧠 가설 저장",
            key="save_hypothesis",
            use_container_width=True
        ):

            if hypothesis_input.strip() == "":

                st.warning(
                    "가설 내용을 먼저 작성해주세요."
                )

            else:

                st.session_state.hypothesis = (
                    hypothesis_input.strip()
                )

                st.rerun()

        if st.session_state.hypothesis:

            st.success(
                "✅ 사건 가설이 저장되었습니다."
            )

            st.markdown("#### 📌 현재 가설")

            st.write(
                st.session_state.hypothesis
            )

        # =====================================================
    # 🔐 FINAL DEDUCTION
    # =====================================================

    st.divider()
    st.subheader("🔐 FINAL DEDUCTION")

    if not st.session_state.hypothesis:

        st.info(
            "먼저 수집한 증거를 바탕으로 "
            "사건 가설을 작성하고 저장하세요."
        )

    else:

        st.success(
            "가설이 준비되었습니다. "
            "수집한 증거를 검토하고 최종 추리를 작성하세요."
        )

        st.markdown("### 🧰 수집 증거 검토")

        for number, evidence in enumerate(
            st.session_state.collected_evidence,
            start=1
        ):
            st.write(
                f"**EVIDENCE {number:02d}** — {evidence}"
            )

        st.markdown("### 🧠 저장된 가설")

        st.info(
            st.session_state.hypothesis
        )

        final_input = st.text_area(
            "이 사건에 대한 최종 추리를 작성하세요.",
            value=st.session_state.final_deduction,
            placeholder=(
                "수집한 증거들이 어떻게 연결되는지 설명하고 "
                "사건에 대한 최종 결론을 작성하세요."
            ),
            key="final_deduction_input"
        )

        if st.button(
            "🔐 최종 추리 제출",
            key="submit_final_deduction",
            type="primary",
            use_container_width=True
        ):

            if final_input.strip() == "":

                st.warning(
                    "최종 추리 내용을 먼저 작성해주세요."
                )

            else:

                st.session_state.final_deduction = (
                    final_input.strip()
                )

                st.session_state.case_submitted = True

                st.rerun() 
                    # =====================================================
        # 🎉 CASE SOLVED
        # =====================================================

        if st.session_state.case_submitted:

            st.divider()

            st.success("🎉 CASE SOLVED")

            st.subheader("🏆 CASE SCORE")

            # ---------------------------------------------
            # 수사 진행도 점수 계산
            # ---------------------------------------------

            evidence_count = len(
                st.session_state.collected_evidence
            )

            evidence_score = min(
                evidence_count * 10,
                50
            )

            hypothesis_score = (
                20
                if st.session_state.hypothesis
                else 0
            )

            deduction_score = (
                30
                if st.session_state.final_deduction
                else 0
            )

            total_score = (
                evidence_score
                + hypothesis_score
                + deduction_score
            )

            col_score1, col_score2, col_score3 = st.columns(3)

            col_score1.metric(
                "증거 수집",
                f"{evidence_score} / 50"
            )

            col_score2.metric(
                "가설 작성",
                f"{hypothesis_score} / 20"
            )

            col_score3.metric(
                "최종 추리",
                f"{deduction_score} / 30"
            )

            st.metric(
                "🎯 TOTAL SCORE",
                f"{total_score} / 100"
            )

            st.progress(
                total_score / 100
            )       
                 # =================================================
            # CASE SCORE 안내
            # =================================================

            st.caption(
                "※ CASE SCORE는 수사 과정의 진행도를 나타내는 "
                "게임 점수입니다. 실제 범죄 사실이나 추리의 정확성을 "
                "판정하는 점수가 아닙니다."
            )

            # =================================================
            # 🔓 REAL DATA UNLOCKED
            # =================================================

            st.divider()

            st.subheader("🔓 REAL DATA UNLOCKED")

            st.success(
                "🎮 가상 CASE 수사가 완료되었습니다. "
                "이제 실제 범죄 통계 데이터를 확인할 수 있습니다."
            )

            st.caption(
                "※ 아래 데이터는 게임용 사건 정보가 아니라 "
                "공공 범죄 통계 데이터에서 가져온 실제 집계 자료입니다."
            )

            # CASE와 연결된 실제 지역 범죄 유형
            real_crime = case["region_crime"]

            real_case_df = region_df[
                (region_df["city"] == case_city)
                & (region_df["district"] == case_district)
                & (
                    region_df["crime_type_original"]
                    == real_crime
                )
            ].copy()

            if real_case_df.empty:

                st.warning(
                    "선택한 지역과 범죄 유형에 해당하는 "
                    "실제 통계 자료가 없습니다."
                )

            else:

                real_case_df = real_case_df.sort_values(
                    "year"
                )

                latest_row = (
                    real_case_df
                    .dropna(subset=["occurrence_count"])
                    .tail(1)
                )

                st.markdown(
                    "### 📊 실제 지역 범죄 데이터 발견"
                )

                col_real1, col_real2 = st.columns(2)

                with col_real1:
                    st.metric(
                        "지역",
                        f"{case_city} {case_district}"
                    )

                with col_real2:
                    st.metric(
                        "범죄 유형",
                        real_crime
                    )

                if not latest_row.empty:

                    latest_year = int(
                        latest_row.iloc[0]["year"]
                    )

                    latest_count = (
                        latest_row.iloc[0][
                            "occurrence_count"
                        ]
                    )

                    col_real3, col_real4 = st.columns(2)

                    with col_real3:
                        st.metric(
                            "최근 데이터 연도",
                            f"{latest_year}년"
                        )

                    with col_real4:
                        st.metric(
                            "발생건수",
                            f"{latest_count:,.0f}건"
                        )

                st.line_chart(
                    real_case_df.set_index("year")[
                        "occurrence_count"
                    ]
                )

                st.caption(
                    "※ 발생건수는 해당 지역의 절대 발생건수입니다. "
                    "인구·유동인구 등의 노출 규모를 보정하지 않았으므로 "
                    "이 수치만으로 지역의 안전·위험 순위를 판단하지 않습니다."
                )

            # =================================================
            # 🛡 SAFETY LAB
            # =================================================

            st.divider()

            st.subheader("🛡 SAFETY LAB")

            st.caption(
                "실제 지역 범죄 통계를 확인한 뒤 "
                "범죄 유형과 관련된 일반적인 예방 행동을 살펴봅니다."
            )

            st.info(
                f"📍 {case_city} {case_district} · "
                f"{real_crime}"
            )

            safety_items = SAFETY_GUIDE.get(
                real_crime,
                []
            )

            if safety_items:

                st.markdown(
                    "### 🛡 예방 행동 가이드"
                )

                for item in safety_items:
                    st.write(f"• {item}")

            else:

                st.info(
                    "현재 이 범죄 유형에 등록된 "
                    "예방 행동 가이드가 없습니다."
                )

            st.caption(
                "※ Safety LAB은 일반적인 범죄 예방 정보를 제공합니다. "
                "지역의 범죄 발생건수만으로 해당 지역의 "
                "안전 또는 위험 수준을 판정하지 않습니다."
            ) 
        # =====================================================
    # 📁 과거 사건기록 조사 결과
    # =====================================================

if st.session_state.investigation_view == "history":

    st.divider()

    st.subheader("📁 과거 사건기록")

    st.success(
            "🔎 사건과 관련된 과거 범죄 기록을 발견했습니다."
            )
        

    history_df = core_df[
        core_df["crime_type_original"] == crime_name
    ].copy()

    history_df = history_df.sort_values(
        "year"
    )

    if history_df.empty:

        st.warning(
             "이 CASE와 연결된 장기 범죄 기록을 "
            "찾지 못했습니다."
        )

    else:

        min_year = int(
            history_df["year"].min()
        )

        max_year = int(
             history_df["year"].max()
        )

        st.write(
            f"**관련 범죄:** {crime_name}"
        )

        st.write(
            f"**기록 기간:** "
            f"{min_year}–{max_year}"
        )

        st.subheader(
            "⏳ 30Y Crime Time Machine"
        )

        chart_df = history_df[
            [
                "year",
                "occurrence_count"
            ]
        ].dropna(
            subset=["occurrence_count"]
        ).copy()

        chart_df["year"] = (
            chart_df["year"]
            .astype(int)
        )

        chart_df = (
            chart_df
            .sort_values("year")
            .set_index("year")
        )

        st.line_chart(
            chart_df["occurrence_count"]
            )    
        # =====================================================
    # 📊 지역 DATA 조사 결과
    # =====================================================

if st.session_state.investigation_view == "region":

    st.divider()

    st.subheader("📊 지역 DATA EVIDENCE")

        # 현재 CASE에서 선택한 지역 + 관련 범죄 자동 연결
    case_region_df = region_df[
        (region_df["city"] == case_city)
        & (region_df["district"] == case_district)
        & (
            region_df["crime_type_original"]
            == region_crime
         )
    ].copy()

    case_region_df = case_region_df.sort_values(
            "year"
    )

    if case_region_df.empty:

        st.warning(
                "선택한 사건 지역과 범죄에 해당하는 "
                "실제 지역 통계 데이터를 찾지 못했습니다."
        )

    else:

            # 가장 최근 연도
        latest_year = int(
            case_region_df["year"]
            .dropna()
            .max()
        )

        latest_data = case_region_df[
                case_region_df["year"]
                == latest_year
            ]

        latest_occurrence = (
            latest_data["occurrence_count"]
            .iloc[0]
            )

        st.success(
                "🔎 실제 지역 범죄 DATA EVIDENCE를 발견했습니다."
            )

        col_a, col_b, col_c, col_d = st.columns(4)

        col_a.metric(
                "사건 지역",
                f"{case_city} {case_district}"
            )

        col_b.metric(
                "관련 범죄",
                region_crime
            )

        col_c.metric(
                "기준 연도",
                f"{latest_year}년"
            )

        if pd.isna(latest_occurrence):

                col_d.metric(
                    "발생건수",
                    "자료 없음"
                )

        else:

                col_d.metric(
                    "발생건수",
                    f"{int(latest_occurrence):,}건"
                )
                            # =============================================
            # Local Crime Time Machine
            # =============================================

        st.subheader(
                "⏳ Local Crime Time Machine"
            )

        st.caption(
                f"{case_city} {case_district} · "
                f"{region_crime} 연도별 발생건수"
            )

        local_chart_df = case_region_df[
                [
                    "year",
                    "occurrence_count"
                ]
            ].dropna(
                subset=["occurrence_count"]
            ).copy()

        if local_chart_df.empty:

                st.info(
                    "표시할 시계열 데이터가 없습니다."
                )

        else:

                local_chart_df["year"] = (
                    local_chart_df["year"]
                    .astype(int)
                )

                local_chart_df = (
                    local_chart_df
                    .sort_values("year")
                    .set_index("year")
                )

                st.line_chart(
                    local_chart_df[
                        "occurrence_count"
                    ]
                )

                  
    # =====================================================
    # REAL DATA Evidence
    # =====================================================

    if st.session_state.evidence_found:

        st.divider()

        st.subheader(
            "📊 REAL DATA EVIDENCE 발견!"
        )

        crime_data = core_df[
            core_df["crime_type_original"]
            == crime_name
        ].sort_values("year")


        if crime_data.empty:

            st.warning(
                "연결된 실제 통계가 없습니다."
            )

        else:

            latest = (
                crime_data
                .sort_values("year")
                .iloc[-1]
            )

            st.success(
                "현장 조사를 통해 사건과 관련된 "
                "실제 공개 통계를 발견했습니다."
            )

            c1, c2, c3 = st.columns(3)

            occurrence = (
                "자료 없음"
                if pd.isna(
                    latest["occurrence_count"]
                )
                else f"{int(latest['occurrence_count']):,}건"
            )

            arrest = (
                "자료 없음"
                if pd.isna(
                    latest["arrest_count"]
                )
                else f"{int(latest['arrest_count']):,}건"
            )

            rate = (
                "자료 없음"
                if pd.isna(
                    latest["clearance_rate"]
                )
                else f"{latest['clearance_rate']:.1f}%"
            )

            c1.metric(
                f"{int(latest['year'])} 발생",
                occurrence
            )

            c2.metric(
                f"{int(latest['year'])} 검거",
                arrest
            )

            c3.metric(
                "공표 검거율",
                rate
            )


            # =============================================
            # Time Machine
            # =============================================

            st.subheader(
                "⏳ 30Y Crime Time Machine"
            )

            st.write(
                f"**{crime_name}**의 "
                "1990~2022년 발생건수 변화입니다."
            )

            chart_data = (
                crime_data[
                    [
                        "year",
                        "occurrence_count"
                    ]
                ]
                .dropna()
                .set_index("year")
            )

            st.line_chart(
                chart_data
            )


            # =============================================
            # 연도 선택
            # =============================================

            selected_year = st.slider(
                "연도를 이동해 보세요",
                min_value=int(
                    crime_data["year"].min()
                ),
                max_value=int(
                    crime_data["year"].max()
                ),
                value=int(
                    crime_data["year"].max()
                )
            )

            year_data = crime_data[
                crime_data["year"]
                == selected_year
            ]

            if not year_data.empty:

                row = year_data.iloc[0]

                st.markdown(
                    f"### 🔬 {selected_year} DATA EVIDENCE"
                )

                a, b, c = st.columns(3)

                a.metric(
                    "발생건수",
                    (
                        "자료 없음"
                        if pd.isna(
                            row["occurrence_count"]
                        )
                        else
                        f"{int(row['occurrence_count']):,}건"
                    )
                )

                b.metric(
                    "검거건수",
                    (
                        "자료 없음"
                        if pd.isna(
                            row["arrest_count"]
                        )
                        else
                        f"{int(row['arrest_count']):,}건"
                    )
                )

                c.metric(
                    "공표 검거율",
                    (
                        "자료 없음"
                        if pd.isna(
                            row["clearance_rate"]
                        )
                        else
                        f"{row['clearance_rate']:.1f}%"
                    )
                )


                warning = row.get(
                    "data_warning",
                    ""
                )

                if (
                    pd.notna(warning)
                    and str(warning).strip()
                ):

                    st.warning(
                        f"데이터 주의: {warning}"
                    )


            st.caption(
                "※ 실제 공개 통계 기반 데이터입니다. "
                "장기간 비교 시 범죄 분류·집계 기준의 "
                "변화를 함께 고려해야 합니다."
            )

# =========================================================
# 🇰🇷 지역 범죄 탐색
# =========================================================
if st.session_state.page == "home":
    st.divider()

    st.header("🇰🇷 지역 범죄 탐색")

    st.caption(
    "실제 범죄 통계 데이터를 지역별로 탐색합니다. "
    "발생건수는 절대 건수이며 지역의 안전·위험 순위를 의미하지 않습니다."
    )


# =========================================================
# 도시 선택
# =========================================================

    city_list = sorted(
    region_df["city"]
    .dropna()
    .unique()
    .tolist()
)

    selected_city = st.selectbox(
    "도시 선택",
    city_list,
    index=(
        city_list.index("서울특별시")
        if "서울특별시" in city_list
        else 0
    ),
    key="region_city"
)


# =========================================================
# 구·군 선택
# =========================================================

    city_df = region_df[
    region_df["city"] == selected_city
].copy()

    district_list = sorted(
    city_df["district"]
    .dropna()
    .unique()
    .tolist()
    )

    default_district = (
    "용산구"
    if "용산구" in district_list
    else district_list[0]
    )

    selected_district = st.selectbox(
        "구·군 선택",
        district_list,
        index=district_list.index(default_district),
        key="region_district"
    )


# =========================================================
# 범죄 유형 선택
# =========================================================

    district_df = city_df[
        city_df["district"] == selected_district
    ].copy()

    crime_list = sorted(
        district_df["crime_type_original"]
        .dropna()
        .unique()
        .tolist()
    )

    default_crime = (
        "절도"
        if "절도" in crime_list
        else crime_list[0]
    )

    selected_crime = st.selectbox(
        "범죄 유형 선택",
        crime_list,
        index=crime_list.index(default_crime),
        key="region_crime"
    )


# =========================================================
# 선택 지역 + 범죄
# =========================================================

    local_df = region_df[
        (region_df["city"] == selected_city)
        & (region_df["district"] == selected_district)
        & (
            region_df["crime_type_original"]
            == selected_crime
        )
    ].copy()

    local_df = local_df.sort_values("year")


# =========================================================
# 연도 선택
# =========================================================

    available_years = sorted(
        local_df["year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    selected_year = st.select_slider(
        "연도 선택",
        options=available_years,
        value=available_years[-1],
        key="region_year"
    )


# =========================================================
# 선택 연도 데이터
# =========================================================

    year_data = local_df[
        local_df["year"] == selected_year
    ]

    if not year_data.empty:
        occurrence = year_data[
            "occurrence_count"
        ].iloc[0]
    else:
        occurrence = None


# =========================================================
# LOCAL DATA EVIDENCE
# =========================================================

    st.subheader("📊 LOCAL DATA EVIDENCE")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "지역",
            f"{selected_city} {selected_district}"
        )

    with col2:
        st.metric(
            "범죄",
            selected_crime
        )

    with col3:
        st.metric(
            "연도",
            f"{selected_year}년"
        )

    with col4:

        if occurrence is None or pd.isna(occurrence):
            st.metric(
                "발생건수",
                "자료 없음"
            )
        else:
            st.metric(
                "발생건수",
                f"{int(occurrence):,}건"
            )


    # =========================================================
    # DATA EVIDENCE 메시지
    # =========================================================

    if occurrence is None or pd.isna(occurrence):

        st.info(
            f"{selected_year}년 "
            f"{selected_city} {selected_district}의 "
            f"{selected_crime} 데이터는 "
            "원자료에서 값이 제공되지 않습니다."
        )

    else:

        st.success(
            f"🔎 DATA EVIDENCE 발견! "
            f"{selected_year}년 "
            f"{selected_city} {selected_district}의 "
            f"{selected_crime} 발생건수는 "
            f"{int(occurrence):,}건입니다."
        )


# =========================================================
# ⏳ LOCAL CRIME TIME MACHINE
# =========================================================
if st.session_state.page == "home":
    st.subheader("⏳ Local Crime Time Machine")

    st.caption(
        f"{selected_city} {selected_district} · "
        f"{selected_crime} 연도별 발생건수"
    )

    chart_df = local_df[
        ["year", "occurrence_count"]
    ].copy()

    chart_df = chart_df.dropna(
        subset=["occurrence_count"]
    )

    if chart_df.empty:

        st.warning(
            "표시할 시계열 데이터가 없습니다."
        )

    else:

        chart_df["year"] = (
            chart_df["year"].astype(int)
        )

        chart_df = (
            chart_df
            .sort_values("year")
            .set_index("year")
        )

        st.line_chart(
            chart_df["occurrence_count"]
        )


# =========================================================
# 데이터 해석 안내
# =========================================================

with st.expander(
    "ℹ️ 실제 범죄 데이터 해석 안내"
):

    st.write(
        """
        - 발생건수는 원자료에 기록된 절대 건수입니다.
        - 값이 없는 연도는 0건이 아니라 '자료 없음'입니다.
        - 발생건수만으로 지역의 안전·위험도를 판단하지 않습니다.
        - 인구수나 유동인구를 반영한 범죄율과는 다른 지표입니다.
        - 장기간 비교에서는 범죄 분류와 행정구역 변화에 주의해야 합니다.
        """
    )