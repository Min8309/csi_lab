
import pandas as pd
import streamlit as st
from ultralytics import YOLO
from pathlib import Path
from PIL import Image

import base64

@st.cache_resource
def load_yolo_model():
    return YOLO("yolo11n.pt")


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
    "potted plant": "화분"
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
# CSI LAB 배경 이미지
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

    /* 전체 배경 */
    [data-testid="stAppViewContainer"] {{
        background-image:
            linear-gradient(
                rgba(255, 255, 255, 0.68),
                rgba(255, 255, 255, 0.68)
            ),
            url("data:image/png;base64,{encoded_image}");

        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* 상단 헤더 투명 */
    [data-testid="stHeader"] {{
        background: rgba(0, 0, 0, 0);
    }}

    /* 메인 콘텐츠 영역 */
    [data-testid="stMainBlockContainer"] {{
        background: rgba(255, 255, 255, 0.50);
        border-radius: 18px;
        padding: 2rem 2.2rem;
        margin-top: 1rem;
        margin-bottom: 2rem;

        box-shadow:
            0 8px 30px rgba(0, 0, 0, 0.08);

        backdrop-filter: blur(2px);
    }}

    /* 일반 글자 조금 더 선명하게 */
    [data-testid="stMainBlockContainer"] p {{
        color: #20242b;
    }}

    /* 제목 */
    [data-testid="stMainBlockContainer"] h1,
    [data-testid="stMainBlockContainer"] h2,
    [data-testid="stMainBlockContainer"] h3 {{
        color: #151a22;
        font-weight: 700;
    }}
     /* Interactive CASE 카드 */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(248, 246, 240, 0.88);
        border: 1px solid rgba(70, 70, 70, 0.18) !important;
        border-radius: 14px;
        padding: 6px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
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
        "region_crime": "절도",
        "description":
            "새벽 시간 발생한 침입 사건. "
            "현장에 남겨진 단서를 조사하세요."
    },

    "CASE-ROBBERY": {
        "title": "사라진 가방",
        "crime": "강도",
        "region_crime": "강도",
        "description":
            "피해자의 가방이 사라졌습니다. "
            "현장의 단서와 실제 데이터를 비교하세요."
    },

    "CASE-ARSON": {
        "title": "불길 속의 흔적",
        "crime": "방화",
        "region_crime": "방화",
        "description":
            "화재 현장에 남은 흔적을 조사하고 "
            "관련 범죄 데이터를 확인하세요."
    },

    "CASE-FRAUD": {
        "title": "의문의 거래",
        "crime": "사기",
        "region_crime": "사기",
        "description":
            "수상한 거래 기록이 발견되었습니다. "
            "데이터 속 패턴을 추적하세요."
    }
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
# =========================================================
# 제목
# =========================================================

st.title("🔎 CSI LAB")

st.caption(
    "게임을 하다가 실제 범죄 데이터를 발견한다"
)

st.divider()


# =========================================================
# HOME — Interactive CASE
# =========================================================

if st.session_state.page == "home":

    st.header("🎮 Interactive CASE")

    st.write(
        "수사할 사건을 선택하세요."
    )

    cols = st.columns(4)

for col, (case_id, info) in zip(
    cols,
    CASE_INFO.items()
):
    with col:

        with st.container(border=True):

            st.subheader(info["title"])
            st.caption(info["crime"])
            st.write(info["description"])

            if st.button(
                "사건 시작",
                key=f"start_{case_id}",
                use_container_width=True
            ):
                open_case(case_id)
                st.rerun()
    


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
                "※ 아래 내용은 CSI LAB 게임을 위한 가상화된 사건 증거입니다."
            )

            st.info(
                f"{case_city} {case_district} 사건 현장 주변의 "
                "CCTV 기록을 분석합니다."
            )

            st.markdown("### 🎞 CCTV 기록 #01")

            st.write(
                "사건 발생 추정 시간대에 현장 주변을 지나가는 "
                "인물과 물체가 기록되어 있습니다."
            )

            st.write(
                "영상 속에서 사건과 관련될 가능성이 있는 "
                "단서를 확인하세요."
            )

            if st.button(
                "🔎 CCTV 단서 발견",
                key="find_cctv_evidence",
                use_container_width=True
            ):

                st.session_state.evidence_found = True

                if "CCTV 기록" not in st.session_state.collected_evidence:
                    st.session_state.collected_evidence.append(
                        "CCTV 기록"
                    )

                st.rerun()

            if "CCTV 기록" in st.session_state.collected_evidence:

                st.success(
                    "✅ CCTV에서 단서를 발견했습니다."
                )

                st.markdown(
                    """
                    **수집된 단서**

                    - 사건 발생 추정 시간대의 CCTV 기록
                    - 현장 주변에서 움직이는 인물 또는 물체 확인
                    - 추가 분석이 필요한 시각 증거
                    """
                )

    # =====================================================
    # 📝 목격자 조사 결과
    # =====================================================

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

            st.markdown("### 👤 목격자 A")

            st.write(
                "“늦은 시간에 현장 근처에서 누군가 빠르게 "
                "이동하는 모습을 봤습니다.”"
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

                st.info(
                    "👤 목격자: 정확하지는 않지만 "
                    "자정 무렵이었던 것 같습니다."
                )

            elif question == "무엇을 들고 있었나요?":

                st.info(
                    "👤 목격자: 손에 무언가를 들고 있었지만 "
                    "정확히 무엇인지는 보지 못했습니다."
                )

            elif question == "어느 방향으로 이동했나요?":

                st.info(
                    "👤 목격자: 현장에서 골목 방향으로 "
                    "빠르게 이동했습니다."
                )

            if st.button(
                "🧩 목격자 진술 수집",
                key="collect_witness_evidence",
                use_container_width=True
            ):

                evidence_name = "목격자 진술: 자정 무렵 인물 목격"

                if (
                    evidence_name
                    not in st.session_state.collected_evidence
                ):
                    st.session_state.collected_evidence.append(
                        evidence_name
                    )

                st.rerun()

            if (
                "목격자 진술: 자정 무렵 인물 목격"
                in st.session_state.collected_evidence
            ):

                st.success(
                    "✅ 목격자 진술을 증거로 수집했습니다."
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
if st.session_state.page == "investigation":
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
        # =====================================================
    # 조사 결과 화면
    # =====================================================
        st.caption(
                         "※ 발생건수는 절대 건수입니다. "
                         "이 값만으로 지역의 안전·위험도를 "
                         "판단하지 않습니다."
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