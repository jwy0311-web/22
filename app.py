import html
import streamlit as st
from roadmap_data import (FIELDS, FIELD_COLORS, SEMESTERS, build_grid,
                          filter_units, load_units, related_units)

st.set_page_config(page_title="과학 교육과정 로드맵", page_icon="🔬", layout="wide")

CSS = """
<style>
.grid{display:grid;gap:8px;margin-bottom:12px}
.head{font-weight:700;text-align:center;padding:6px;border-radius:8px;background:#e9edf3;color:#223}
.rowlabel{font-weight:700;color:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;padding:6px}
.cell{min-height:40px;border-radius:8px;background:#f6f7f9;padding:4px;display:flex;flex-direction:column;gap:4px}
.card{color:#fff;border-radius:6px;padding:5px 7px;font-size:12.5px;line-height:1.3}
.card small{opacity:.85;display:block}
.hl{outline:3px solid #ffd400}
</style>
"""


def card(u, highlight=False):
    cls = "card hl" if highlight else "card"
    return (f'<div class="{cls}" style="background:{FIELD_COLORS[u["field"]]}">'
            f'{html.escape(u["unit"])}<small>{html.escape(u["subject"])} · {u["kind"]}</small></div>')


def render_semester_view(units, selected):
    grid = build_grid(units, "학기별")
    cols = "".join(f'<div class="head">{s}</div>' for s in SEMESTERS)
    cells = "".join('<div class="cell">' + "".join(card(u, u is selected) for u in grid[s]) + "</div>"
                    for s in SEMESTERS)
    st.markdown(f'<div class="grid" style="grid-template-columns:repeat(6,1fr)">{cols}{cells}</div>',
                unsafe_allow_html=True)


def render_field_view(units, selected):
    grid = build_grid(units, "분야별")
    out = '<div></div>' + "".join(f'<div class="head">{s}</div>' for s in SEMESTERS)
    for f in FIELDS:
        if not any(grid[f][s] for s in SEMESTERS):
            continue
        out += f'<div class="rowlabel" style="background:{FIELD_COLORS[f]}">{f}</div>'
        for s in SEMESTERS:
            out += '<div class="cell">' + "".join(card(u, u is selected) for u in grid[f][s]) + "</div>"
    st.markdown(f'<div class="grid" style="grid-template-columns:80px repeat(6,1fr)">{out}</div>',
                unsafe_allow_html=True)


def main():
    st.markdown(CSS, unsafe_allow_html=True)
    st.title("🔬 과학 교육과정 로드맵")
    st.caption("지금 배우는 단원이 앞뒤로 어디와 이어지는지 한눈에 확인해 보세요. (2022 개정 교육과정 기준)")

    try:
        units = load_units()
    except Exception as e:  # 데이터 오류가 나도 앱이 멈추지 않도록
        st.error(f"로드맵 데이터를 불러오지 못했어요: {e}")
        return

    with st.sidebar:
        st.header("보기 설정")
        mode = st.radio("보기 방식", ["학년·학기 순서(통시적)", "과학 분야별"])
        fields = st.multiselect("분야", FIELDS, default=FIELDS)
        kinds = st.multiselect("과목 유형", ["공통", "일반선택", "진로선택", "융합선택"],
                               default=["공통", "일반선택", "진로선택", "융합선택"])
        keyword = st.text_input("단원·과목 검색", placeholder="예: 주기율, 유전, 에너지")

    shown = filter_units(units, fields, kinds, keyword)
    if not shown:
        st.warning("조건에 맞는 단원이 없어요. 필터나 검색어를 바꿔 보세요.")
        return

    labels = {f'{u["subject"]} - {u["unit"]}': u for u in shown}
    choice = st.selectbox("🔗 단원을 고르면 연결된 단원을 보여줘요", ["(선택 안 함)"] + list(labels))
    selected = labels.get(choice)

    st.markdown("".join(
        f'<span style="background:{c};color:#fff;border-radius:12px;padding:2px 10px;margin-right:6px;font-size:13px">{f}</span>'
        for f, c in FIELD_COLORS.items()), unsafe_allow_html=True)
    st.write("")

    if mode.startswith("학년"):
        render_semester_view(shown, selected)
    else:
        render_field_view(shown, selected)

    if selected:
        st.subheader(f"'{selected['unit']}'와 이어지는 단원")
        rel = related_units(units, selected)
        if rel:
            for u in rel:
                st.write(f"- **{u['semester']}** · {u['subject']} · {u['unit']} ({u['field']})")
        else:
            st.info("연결된 단원이 아직 등록되지 않았어요.")


main()

streamlit

"""과학 교육과정 로드맵 - 데이터와 처리 함수 (2022 개정 교육과정 기준).
※ 단원명·학기 배치는 학교마다 다를 수 있으니 실제 교육과정 문서와 대조해 수정하세요.
"""

SEMESTERS = ["고1-1학기", "고1-2학기", "고2-1학기", "고2-2학기", "고3-1학기", "고3-2학기"]
FIELDS = ["물리", "화학", "생명", "지구과학", "융합·탐구"]
FIELD_COLORS = {"물리": "#4F8EF7", "화학": "#F2994A", "생명": "#4CAF7A",
                "지구과학": "#A0714F", "융합·탐구": "#9B6FD1"}

# (과목, 유형, 단원, 학기, 분야, 연계 키워드)
RAW = [
    ("통합과학1", "공통", "자연 세계의 이해", "고1-1학기", "융합·탐구", "측정 탐구"),
    ("통합과학1", "공통", "과학의 측정과 우리 사회", "고1-1학기", "융합·탐구", "측정 정보"),
    ("통합과학1", "공통", "우주와 원소의 생성", "고1-1학기", "지구과학", "우주 원소"),
    ("통합과학1", "공통", "원소의 주기성과 결합", "고1-1학기", "화학", "원소 결합"),
    ("통합과학1", "공통", "결합으로 이루어진 세상", "고1-1학기", "화학", "결합 전자기 물질"),
    ("통합과학1", "공통", "지구시스템", "고1-1학기", "지구과학", "지구시스템 대기해양"),
    ("통합과학1", "공통", "역학 시스템", "고1-1학기", "물리", "힘운동 에너지"),
    ("통합과학1", "공통", "생명 시스템", "고1-1학기", "생명", "물질대사"),
    ("과학탐구실험1", "공통", "과학 탐구 방법과 절차", "고1-1학기", "융합·탐구", "측정 탐구"),
    ("통합과학2", "공통", "화학 변화", "고1-2학기", "화학", "반응"),
    ("통합과학2", "공통", "생물다양성과 진화", "고1-2학기", "생명", "진화유전"),
    ("통합과학2", "공통", "생태계와 환경", "고1-2학기", "생명", "생태 기후"),
    ("통합과학2", "공통", "에너지 전환과 활용", "고1-2학기", "물리", "에너지"),
    ("과학탐구실험2", "공통", "융합 탐구 활동", "고1-2학기", "융합·탐구", "탐구"),
    ("물리학", "일반선택", "힘과 운동", "고2-1학기", "물리", "힘운동 에너지"),
    ("물리학", "일반선택", "전기와 자기", "고2-1학기", "물리", "전자기"),
    ("물리학", "일반선택", "파동과 정보 통신", "고2-2학기", "물리", "파동빛"),
    ("물리학", "일반선택", "빛과 물질", "고2-2학기", "물리", "파동빛 전자기"),
    ("화학", "일반선택", "화학의 언어", "고2-1학기", "화학", "원소 반응"),
    ("화학", "일반선택", "원자의 세계", "고2-1학기", "화학", "원소 결합"),
    ("화학", "일반선택", "화학 결합과 분자의 세계", "고2-2학기", "화학", "결합 물질"),
    ("화학", "일반선택", "역동적인 화학 반응", "고2-2학기", "화학", "반응"),
    ("생명과학", "일반선택", "사람의 물질대사", "고2-1학기", "생명", "물질대사"),
    ("생명과학", "일반선택", "항상성과 몸의 조절", "고2-1학기", "생명", "물질대사"),
    ("생명과학", "일반선택", "유전", "고2-2학기", "생명", "진화유전"),
    ("생명과학", "일반선택", "생태계와 상호작용", "고2-2학기", "생명", "생태 기후"),
    ("지구과학", "일반선택", "지구의 역사와 판 구조론", "고2-1학기", "지구과학", "지구시스템"),
    ("지구과학", "일반선택", "대기와 해양", "고2-2학기", "지구과학", "대기해양 기후"),
    ("지구과학", "일반선택", "별과 우주", "고2-2학기", "지구과학", "우주 원소"),
    ("역학과 에너지", "진로선택", "역학과 에너지 전체", "고3-1학기", "물리", "힘운동 에너지"),
    ("전자기와 양자", "진로선택", "전자기와 양자 전체", "고3-2학기", "물리", "전자기 파동빛"),
    ("물질과 에너지", "진로선택", "물질과 에너지 전체", "고3-1학기", "화학", "원소 결합 물질"),
    ("화학 반응의 세계", "진로선택", "화학 반응의 세계 전체", "고3-2학기", "화학", "반응"),
    ("세포와 물질대사", "진로선택", "세포와 물질대사 전체", "고3-1학기", "생명", "물질대사"),
    ("생물의 유전", "진로선택", "생물의 유전 전체", "고3-2학기", "생명", "진화유전"),
    ("지구시스템과학", "진로선택", "지구시스템과학 전체", "고3-1학기", "지구과학", "지구시스템 대기해양"),
    ("행성우주과학", "진로선택", "행성우주과학 전체", "고3-2학기", "지구과학", "우주 원소"),
    ("기후변화와 환경생태", "융합선택", "기후변화와 환경생태 전체", "고3-2학기", "융합·탐구", "기후 생태 대기해양"),
]

KEYS = ["subject", "kind", "unit", "semester", "field", "tags"]


def load_units():
    """RAW 튜플을 딕셔너리 리스트로 변환 (tags는 리스트로)."""
    units = []
    for row in RAW:
        d = dict(zip(KEYS, row))
        d["tags"] = d["tags"].split()
        units.append(d)
    return units


def filter_units(units, fields=None, kinds=None, keyword=""):
    """분야·유형·검색어 조건에 맞는 단원만 반환. 조건이 비어 있으면 전체."""
    kw = (keyword or "").strip().lower()
    result = []
    for u in units:
        if fields and u["field"] not in fields:
            continue
        if kinds and u["kind"] not in kinds:
            continue
        if kw and kw not in (u["subject"] + u["unit"] + " ".join(u["tags"])).lower():
            continue
        result.append(u)
    return result


def related_units(units, target):
    """target과 키워드를 하나라도 공유하는 다른 단원을 학기 순서로 반환."""
    found = [u for u in units if u is not target and set(u["tags"]) & set(target["tags"])]
    return sorted(found, key=lambda u: SEMESTERS.index(u["semester"]))


def build_grid(units, mode):
    """mode='학기별'이면 {학기: [단원]}, mode='분야별'이면 {분야: {학기: [단원]}}."""
    if mode == "학기별":
        return {s: [u for u in units if u["semester"] == s] for s in SEMESTERS}
    return {f: {s: [u for u in units if u["field"] == f and u["semester"] == s]
                for s in SEMESTERS} for f in FIELDS}
