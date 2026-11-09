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
