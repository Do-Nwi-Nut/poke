요청하신 문제를 해결하여 **처음부터 끝까지 바로 복사해서 사용하실 수 있는 전체 코드**입니다.

문제가 되었던 `st.data_editor`와 `st.session_state` 간의 간섭 로직을 정리하여, 점수를 입력하면 상단 보드에 실시간으로 끊김 없이 즉시 반영되도록 수정했습니다.

```python
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time

st.set_page_config(page_title="POKÉMON LEAGUE · SCOREBOARD", page_icon="🌈", layout="wide")


def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


# ============================================================
# 팀 설정
# ============================================================
TEAMS = {
    "BLUE": {
        "accent": "#00B8E0",
        "bg": "#E4F8FF",
        "glow": "rgba(0, 184, 224, 0.45)",
        "type_kr": "물 타입",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png",
        "confetti": ["#00B8E0", "#7FE3FF", "#C8F4FF"],
    },
    "GREEN": {
        "accent": "#2FBE6B",
        "bg": "#E6FBEE",
        "glow": "rgba(47, 190, 107, 0.45)",
        "type_kr": "풀 타입",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
        "confetti": ["#2FBE6B", "#9CF3BE", "#D6FAE3"],
    },
    "RED": {
        "accent": "#FF5C72",
        "bg": "#FFEAEE",
        "glow": "rgba(255, 92, 114, 0.45)",
        "type_kr": "불 타입",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png",
        "confetti": ["#FF5C72", "#FFA7B5", "#FFD9DF"],
    },
    "YELLOW": {
        "accent": "#FFB100",
        "bg": "#FFF8E1",
        "glow": "rgba(255, 177, 0, 0.45)",
        "type_kr": "전기 타입",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
        "confetti": ["#FFB100", "#FFDE7A", "#FFF0BF"],
    },
}
TEAM_NAMES = list(TEAMS.keys())

DECOR_POKEMON_IDS = [1, 4, 7, 25, 39, 52, 54, 104, 113, 131, 133, 143, 152, 155, 158, 172, 174, 175]

# ============================================================
# 세션 상태 — 점수 표 (라운드 = 행, 팀 = 열)
# ============================================================
if "score_df" not in st.session_state:
    st.session_state.score_df = pd.DataFrame(
        {team: [0] for team in TEAM_NAMES}, index=pd.Index([1], name="라운드")
    )

if "prev_totals" not in st.session_state:
    st.session_state.prev_totals = {team: 0 for team in TEAM_NAMES}

if "celebrate" not in st.session_state:
    st.session_state.celebrate = None

# ============================================================
# 전역 스타일
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Poppins:wght@400;500;600&family=Space+Mono:wght@700&display=swap');

    html, body, [class^="css"], [class*=" css"] { font-family: 'Poppins', sans-serif; }

    .stApp {
        color-scheme: light;
        background:
            radial-gradient(circle at 12% 8%, rgba(0,184,224,0.16), transparent 40%),
            radial-gradient(circle at 88% 12%, rgba(255,177,0,0.16), transparent 40%),
            radial-gradient(circle at 50% 95%, rgba(255,92,114,0.14), transparent 45%),
            linear-gradient(180deg, #FFFDF6 0%, #FFF7EC 50%, #FFF1E4 100%);
        color: #3B3A45;
    }

    #MainMenu, header, footer { visibility: hidden; }

    @keyframes floaty { 0%,100%{transform:translateY(0) rotate(0deg);} 50%{transform:translateY(-9px) rotate(2.5deg);} }
    @keyframes floatyBig { 0%,100%{transform:translateY(0px);} 50%{transform:translateY(-16px);} }
    @keyframes pulseGlow { 0%,100%{ filter: drop-shadow(0 0 6px var(--glow)); } 50%{ filter: drop-shadow(0 0 20px var(--glow)); } }
    @keyframes holoSheen { 0%{ background-position: 0% 50%; } 100%{ background-position: 200% 50%; } }
    @keyframes titleGrad { 0%,100%{ background-position: 0% 50%; } 50%{ background-position: 100% 50%; } }
    @keyframes popIn { 0%{ transform: scale(0.85); opacity:0; } 60%{ transform: scale(1.04); opacity:1;} 100%{ transform: scale(1); } }
    @keyframes countPulse { 0%{ transform: scale(1.3); } 100%{ transform: scale(1); } }

    .hero { text-align: center; padding: 26px 10px 16px 10px; }
    .hero-eyebrow {
        font-family: 'Space Mono', monospace;
        letter-spacing: 4px;
        font-size: 0.75rem;
        color: #B5A98C;
        text-transform: uppercase;
    }
    .hero h1 {
        font-family: 'Baloo 2', sans-serif;
        font-weight: 800;
        font-size: 3.1rem;
        margin: 6px 0 4px 0;
        background: linear-gradient(90deg, #00B8E0, #2FBE6B, #FFB100, #FF5C72, #00B8E0);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleGrad 6s ease infinite;
    }
    .hero-sub { color: #9A937E; font-size: 0.95rem; margin-top: -2px; }
    .hero-divider {
        height: 3px;
        width: 60%;
        margin: 16px auto 0 auto;
        border-radius: 99px;
        background: linear-gradient(90deg, #00B8E033, #2FBE6B55, #FFB10055, #FF5C7255, #00B8E033);
    }

    .trainer-card {
        --glow: #ffffff66;
        position: relative;
        border-radius: 26px;
        padding: 22px 14px 18px 14px;
        text-align: center;
        background: linear-gradient(160deg, #FFFFFFE0, #FFFFFFB0);
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 10px 28px rgba(0,0,0,0.07);
        animation: popIn 0.5s ease-out;
        overflow: hidden;
    }
    .trainer-card::before {
        content: "";
        position: absolute;
        inset: -2px;
        border-radius: 22px;
        padding: 2px;
        background: linear-gradient(120deg, transparent 30%, var(--card-accent) 50%, transparent 70%);
        background-size: 250% 250%;
        animation: holoSheen 3.2s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        opacity: 0.7;
        pointer-events: none;
    }
    .trainer-card .type-tag {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--card-accent);
        opacity: 0.95;
        margin-bottom: 2px;
        font-weight: 700;
    }
    .trainer-card .sprite-wrap {
        width: 220px; height: 220px;
        margin: 6px auto 2px auto;
        border-radius: 50%;
        background: radial-gradient(circle, var(--card-bg) 0%, transparent 72%);
        display: flex; align-items: center; justify-content: center;
        animation: pulseGlow 2.4s ease-in-out infinite;
    }
    .trainer-card img.sprite {
        width: 200px; height: 200px;
        image-rendering: pixelated;
        animation: floaty 2.8s ease-in-out infinite;
    }
    .trainer-card .team-name {
        font-family: 'Baloo 2', sans-serif;
        font-weight: 800;
        font-size: 1.4rem;
        letter-spacing: 1px;
        color: #3B3A45;
        margin-top: 4px;
        margin-bottom: 10px;
    }
    .trainer-card .score-num {
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 3.2rem;
        color: var(--card-accent);
        text-shadow: 0 0 16px var(--glow);
        animation: countPulse 0.4s ease-out;
        line-height: 1;
    }
    .trainer-card .score-label {
        font-size: 0.7rem;
        letter-spacing: 3px;
        color: #B5A98C;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .rank-card {
        border-radius: 18px;
        padding: 14px 8px;
        text-align: center;
        background: #FFFFFFCC;
        border: 1px solid rgba(0,0,0,0.06);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        animation: popIn 0.55s ease-out;
        position: relative;
    }
    .rank-card .medal { font-size: 1.7rem; animation: floaty 2.5s ease-in-out infinite; }
    .rank-card .rank-team { font-weight: 700; font-family:'Baloo 2',sans-serif; margin-top: 2px; }
    .rank-card .rank-score { font-family: 'Space Mono', monospace; font-size: 1.3rem; margin-top: 2px; color:#3B3A45;}
    .rank-card.is-first { box-shadow: 0 0 30px var(--glow); }

    .stButton button {
        border-radius: 14px !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        background: linear-gradient(135deg, #FFFFFF, #FFF6E5) !important;
        color: #3B3A45 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        transition: all 0.18s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        border-color: rgba(0,0,0,0.18) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.10);
    }
    .stButton button:active { transform: translateY(0px) scale(0.98); }

    div[data-testid="stDataEditor"] {
        --gdg-bg-cell: #FFFFFF;
        --gdg-bg-cell-medium: #FAFAFA;
        --gdg-bg-header: #FFF6E5;
        --gdg-bg-header-has-focus: #FFEFCB;
        --gdg-bg-bubble: #FFFFFF;
        --gdg-text-dark: #1A1A1A;
        --gdg-text-medium: #1A1A1A;
        --gdg-text-light: #4A4A4A;
        --gdg-text-bubble: #1A1A1A;
        --gdg-text-header: #3B3A45;
        --gdg-header-font-color: #3B3A45;
        --gdg-border-color: rgba(0,0,0,0.10);
        --gdg-accent-color: #FFB100;
        --gdg-accent-light: #FFF1CF;
        background: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid rgba(0,0,0,0.08) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        overflow: hidden;
        animation: popIn 0.5s ease-out;
        color-scheme: light;
    }
    div[data-testid="stDataEditor"] [data-testid="stElementToolbar"] {
        background: #FFFFFF !important;
    }

    section[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(0,0,0,0.08);
    }

    .poke-decor-wrap {
        position: relative;
        margin-top: 36px;
        padding: 26px 0 18px 0;
        border-radius: 26px;
        overflow: hidden;
        background: linear-gradient(135deg, #FFF3D6, #FFE3EC, #E3F7FF, #E4FBEC);
        background-size: 300% 300%;
        animation: titleGrad 10s ease infinite;
    }
    .poke-decor-title {
        text-align: center;
        font-family: 'Baloo 2', sans-serif;
        font-weight: 700;
        color: #6B6457;
        font-size: 1rem;
        margin-bottom: 10px;
        letter-spacing: 1px;
    }
    .poke-decor-row {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 10px 6px;
        padding: 0 10px;
    }
    .poke-decor-row img {
        width: 96px;
        height: 96px;
        image-rendering: pixelated;
        opacity: 0.92;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.10));
    }

    .footer-note {
        text-align: center;
        color: #B5A98C;
        font-size: 0.8rem;
        margin-top: 18px;
        font-family: 'Space Mono', monospace;
        letter-spacing: 1px;
        animation: floaty 5s ease-in-out infinite;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 헤더
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">TRAINER SCORE TRACKER</div>
        <h1>🌈 POKÉMON LEAGUE 🌈</h1>
        <div class="hero-sub">표에 라운드별 점수를 입력하면 총합 보드에 바로 반영돼요</div>
        <div class="hero-divider"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 컨페티 (총점이 오른 경우 자동 발동)
# ============================================================
if st.session_state.celebrate:
    team = st.session_state.celebrate
    colors = TEAMS[team]["confetti"]
    components.html(
        f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/canvas-confetti/1.9.2/confetti.browser.min.js"></script>
        <script>
        function fire() {{
            if (typeof confetti !== 'function') {{ setTimeout(fire, 80); return; }}
            const colors = {colors};
            confetti({{ particleCount: 110, spread: 80, startVelocity: 42, origin: {{ y: 0.3 }}, colors: colors }});
            confetti({{ particleCount: 60, angle: 60, spread: 60, origin: {{ x: 0 }}, colors: colors }});
            confetti({{ particleCount: 60, angle: 120, spread: 60, origin: {{ x: 1 }}, colors: colors }});
        }}
        fire();
        </script>
        """,
        height=0,
    )
    st.markdown(
        f"""
        <div style="text-align:center; margin-top:-6px; animation: popIn 0.5s ease-out;">
            <span style="font-family:'Baloo 2',sans-serif; font-size:1.3rem; color:{TEAMS[team]['accent']};">
                ✨ {team} 팀 점수 업데이트! ✨
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.celebrate = None

st.write("")

# ============================================================
# 합산 점수 보드 (표보다 위에 위치, 표 입력값을 즉시 반영)
# ============================================================
st.markdown(
    """<h3 style="font-family:'Baloo 2',sans-serif; color:#3B3A45;">📋 합산 점수 보드</h3>""",
    unsafe_allow_html=True,
)
score_board_container = st.container()

st.write("")

# ============================================================
# 점수 입력 표 (라운드별 행, 팀별 열) — 흰 배경, 라운드 번호 자동
# ============================================================
st.markdown(
    """<h3 style="font-family:'Baloo 2',sans-serif; color:#3B3A45;">📝 라운드별 점수 입력</h3>""",
    unsafe_allow_html=True,
)
st.caption("‘➕ 라운드 추가’ 버튼으로 라운드를 늘리면 번호가 자동으로 이어지고, 빈 칸은 0으로 처리되어 항상 바로 합산돼요.")

column_config = {
    team: st.column_config.NumberColumn(
        f"{TEAMS[team]['type_kr'].split()[0]} · {team}",
        step=1,
        format="%d",
        min_value=0,
    )
    for team in TEAM_NAMES
}

# [수정 부분] 원본 score_df 기반으로 에디터를 열되, 매 루프마다 덮어쓰지 않습니다.
edited_df = st.data_editor(
    st.session_state.score_df,
    column_config=column_config,
    num_rows="fixed",
    use_container_width=True,
    hide_index=False,
    key="score_table_editor",
)

# 합계 계산 및 실시간 반영을 위한 복사본 생성 (빈 셀 방지)
calc_df = edited_df.copy()
for team in TEAM_NAMES:
    calc_df[team] = calc_df[team].fillna(0)

round_btn_col, _ = st.columns([1, 3])
with round_btn_col:
    if st.button("➕ 라운드 추가", key="add_round_btn", use_container_width=True):
        # [수정 부분] 라운드를 늘릴 때는 지금까지 편집된 최신 값을 영구 소장 후 행을 덧붙입니다.
        next_round = int(calc_df.index.max()) + 1
        new_row = pd.DataFrame(
            {team: [0] for team in TEAM_NAMES},
            index=pd.Index([next_round], name="라운드"),
        )
        st.session_state.score_df = pd.concat([calc_df, new_row])
        if "score_table_editor" in st.session_state:
            del st.session_state["score_table_editor"]
        st.toast(f"🆕 {next_round}라운드 추가!", icon="🎉")
        safe_rerun()

# ============================================================
# 총점 계산 (표 입력값 기준으로 즉시 반영)
# ============================================================
new_totals = {team: int(calc_df[team].sum()) for team in TEAM_NAMES}

increased_teams = [
    team for team in TEAM_NAMES
    if new_totals[team] > st.session_state.prev_totals.get(team, 0)
]
if increased_teams:
    st.session_state.celebrate = increased_teams[0]
st.session_state.prev_totals = new_totals

# 위쪽에 미리 만들어둔 합산 점수 보드 컨테이너에 카드 채우기
with score_board_container:
    cards_placeholder = st.columns(4)
    for col, team in zip(cards_placeholder, TEAM_NAMES):
        info = TEAMS[team]
        total = new_totals[team]
        with col:
            st.markdown(
                f"""
                <div class="trainer-card" style="--card-accent:{info['accent']}; --card-bg:{info['bg']}; --glow:{info['glow']};">
                    <div class="type-tag">{info['type_kr']}</div>
                    <div class="sprite-wrap"><img class="sprite" src="{info['sprite']}" /></div>
                    <div class="team-name">{team}</div>
                    <div class="score-num">{total}</div>
                    <div class="score-label">TOTAL PTS</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.write("")
st.write("")

# ============================================================
# 챔피언십 순위
# ============================================================
st.write("")
st.markdown(
    """<h3 style="font-family:'Baloo 2',sans-serif; color:#3B3A45;">🏆 챔피언십 순위</h3>""",
    unsafe_allow_html=True,
)

ranking = sorted(new_totals.items(), key=lambda x: x[1], reverse=True)
medal = ["🥇", "🥈", "🥉", "🎗️"]

rank_cols = st.columns(4)
for i, (team, total) in enumerate(ranking):
    info = TEAMS[team]
    with rank_cols[i]:
        first_class = "is-first" if i == 0 else ""
        st.markdown(
            f"""
            <div class="rank-card {first_class}" style="--glow:{info['glow']}; border-color:{info['accent']}33;">
                <div class="medal">{medal[i]}</div>
                <div class="rank-team" style="color:{info['accent']};">{team}</div>
                <div class="rank-score">{total} <span style="font-size:0.8rem; color:#9A937E;">PTS</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# 초기화 버튼
# ============================================================
st.write("")
if st.button("🔄 전체 초기화", key="reset_btn"):
    st.session_state.score_df = pd.DataFrame(
        {team: [0] for team in TEAM_NAMES}, index=pd.Index([1], name="라운드")
    )
    if "score_table_editor" in st.session_state:
        del st.session_state["score_table_editor"]
    st.session_state.prev_totals = {team: 0 for team in TEAM_NAMES}
    st.session_state.celebrate = None
    st.toast("점수판이 초기화되었어요", icon="🧹")
    safe_rerun()

# ============================================================
# 하단 배경 장식 — 다양한 포켓몬들
# ============================================================
decor_imgs = "".join(
    f'<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pid}.png" '
    f'style="animation: floatyBig {2.2 + (pid % 5) * 0.3}s ease-in-out infinite; animation-delay: {(pid % 7) * 0.15}s;" />'
    for pid in DECOR_POKEMON_IDS
)

st.markdown(
    f"""
    <div class="poke-decor-wrap">
        <div class="poke-decor-title">✨ 오늘도 함께한 포켓몬 친구들 ✨</div>
        <div class="poke-decor-row">
            {decor_imgs}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """<div class="footer-note">🌈 POKÉMON LEAGUE SCOREBOARD · GOOD LUCK TRAINERS 🌈</div>""",
    unsafe_allow_html=True,
)

```
