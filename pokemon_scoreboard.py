import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time

st.set_page_config(page_title="POKÉMON LEAGUE · SCOREBOARD", page_icon="🌈", layout="wide")


def safe_rerun():
    """Streamlit 버전에 관계없이 안전하게 재실행."""
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()


# ============================================================
# 팀 설정 — 포켓몬 리그 트레이너 카드 컨셉 (화사한 파스텔 버전)
# ============================================================
TEAMS = {
    "BLUE": {
        "accent": "#00B8E0",
        "accent2": "#7FE3FF",
        "bg": "#E4F8FF",
        "glow": "rgba(0, 184, 224, 0.45)",
        "pokemon": "",
        "type_kr": "물 타입",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png",
        "confetti": ["#00B8E0", "#7FE3FF", "#C8F4FF"],
    },
    "GREEN": {
        "accent": "#2FBE6B",
        "accent2": "#9CF3BE",
        "bg": "#E6FBEE",
        "glow": "rgba(47, 190, 107, 0.45)",
        "pokemon": "",
        "type_kr": "풀 타입",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
        "confetti": ["#2FBE6B", "#9CF3BE", "#D6FAE3"],
    },
    "RED": {
        "accent": "#FF5C72",
        "accent2": "#FFA7B5",
        "bg": "#FFEAEE",
        "glow": "rgba(255, 92, 114, 0.45)",
        "pokemon": "",
        "type_kr": "불 타입",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png",
        "confetti": ["#FF5C72", "#FFA7B5", "#FFD9DF"],
    },
    "YELLOW": {
        "accent": "#FFB100",
        "accent2": "#FFDE7A",
        "bg": "#FFF8E1",
        "glow": "rgba(255, 177, 0, 0.45)",
        "pokemon": "",
        "type_kr": "전기 타입",
        "sprite": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
        "confetti": ["#FFB100", "#FFDE7A", "#FFF0BF"],
    },
}

# 하단 배경 장식용 포켓몬 (다양하게)
DECOR_POKEMON_IDS = [1, 4, 7, 25, 39, 52, 54, 104, 113, 131, 133, 143, 152, 155, 158, 172, 174, 175]

# ============================================================
# 세션 상태
# ============================================================
if "rounds" not in st.session_state:
    st.session_state.rounds = 1
if "scores" not in st.session_state:
    st.session_state.scores = {team: [0] for team in TEAMS}
if "celebrate" not in st.session_state:
    st.session_state.celebrate = None
if "active_round" not in st.session_state:
    st.session_state.active_round = {team: 1 for team in TEAMS}

# ============================================================
# 전역 스타일 (화사 / 밝은 버전)
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Poppins:wght@400;500;600&family=Space+Mono:wght@700&display=swap');

    html, body, [class^="css"], [class*=" css"] { font-family: 'Poppins', sans-serif; }

    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(0,184,224,0.16), transparent 40%),
            radial-gradient(circle at 88% 12%, rgba(255,177,0,0.16), transparent 40%),
            radial-gradient(circle at 50% 95%, rgba(255,92,114,0.14), transparent 45%),
            linear-gradient(180deg, #FFFDF6 0%, #FFF7EC 50%, #FFF1E4 100%);
        color: #3B3A45;
    }

    #MainMenu, header, footer { visibility: hidden; }

    /* ---------- 키프레임 ---------- */
    @keyframes floaty { 0%,100%{transform:translateY(0) rotate(0deg);} 50%{transform:translateY(-9px) rotate(2.5deg);} }
    @keyframes floatyBig { 0%,100%{transform:translateY(0px);} 50%{transform:translateY(-16px);} }
    @keyframes pulseGlow { 0%,100%{ filter: drop-shadow(0 0 6px var(--glow)); } 50%{ filter: drop-shadow(0 0 20px var(--glow)); } }
    @keyframes holoSheen { 0%{ background-position: 0% 50%; } 100%{ background-position: 200% 50%; } }
    @keyframes titleGrad { 0%,100%{ background-position: 0% 50%; } 50%{ background-position: 100% 50%; } }
    @keyframes popIn { 0%{ transform: scale(0.85); opacity:0; } 60%{ transform: scale(1.04); opacity:1;} 100%{ transform: scale(1); } }
    @keyframes countPulse { 0%{ transform: scale(1.3); } 100%{ transform: scale(1); } }
    @keyframes driftX { 0%{ transform: translateX(0px); } 50%{ transform: translateX(14px); } 100%{ transform: translateX(0px); } }

    /* ---------- 헤더 ---------- */
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

    /* ---------- 트레이너 카드 ---------- */
    .trainer-card {
        --glow: #ffffff66;
        position: relative;
        border-radius: 22px;
        padding: 18px 14px 14px 14px;
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
        width: 92px; height: 92px;
        margin: 6px auto 2px auto;
        border-radius: 50%;
        background: radial-gradient(circle, var(--card-bg) 0%, transparent 72%);
        display: flex; align-items: center; justify-content: center;
        animation: pulseGlow 2.4s ease-in-out infinite;
    }
    .trainer-card img.sprite {
        width: 78px; height: 78px;
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
    }
    .trainer-card .poke-sub { font-size: 0.8rem; color: #9A937E; margin-bottom: 8px; }
    .trainer-card .score-num {
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 2.7rem;
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

    /* ---------- 라운드 캡슐 ---------- */
    .round-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 20px;
        border-radius: 999px;
        background: linear-gradient(120deg, #FFFFFF, #FFF6E5);
        border: 1px solid rgba(0,0,0,0.08);
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
        color: #3B3A45;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        animation: floaty 3.4s ease-in-out infinite;
    }

    /* ---------- 순위 카드 ---------- */
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

    /* ---------- 버튼 ---------- */
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

    div[data-baseweb="select"] > div, div[data-testid="stNumberInput"] input {
        background: #FFFFFF !important;
        border-radius: 10px !important;
        border-color: rgba(0,0,0,0.10) !important;
        color: #3B3A45 !important;
    }

    section[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(0,0,0,0.08);
    }

    /* ---------- 하단 포켓몬 배경 장식 띠 ---------- */
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
        gap: 6px 2px;
        padding: 0 10px;
    }
    .poke-decor-row img {
        width: 56px;
        height: 56px;
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
        <div class="hero-sub">라운드별 점수를 기록하고 챔피언을 가려보세요</div>
        <div class="hero-divider"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 컨페티 (점수 등록 시)
# ============================================================
if st.session_state.celebrate:
    team = st.session_state.celebrate
    colors = TEAMS[team]["confetti"]
    components.html(
        f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/canvas-confetti/1.9.2/confetti.browser.min.js"></script>
        <div id="confetti-root" style="height:0;"></div>
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
                ✨ {team} 팀 점수 등록 완료! ✨
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state.celebrate = None

st.write("")

# ============================================================
# 팀 카드 + 입력
# ============================================================
cols = st.columns(4)

for col, (team, info) in zip(cols, TEAMS.items()):
    total = sum(st.session_state.scores[team])
    with col:
        st.markdown(
            f"""
            <div class="trainer-card" style="--card-accent:{info['accent']}; --card-bg:{info['bg']}; --glow:{info['glow']};">
                <div class="type-tag">{info['type_kr']}</div>
                <div class="sprite-wrap"><img class="sprite" src="{info['sprite']}" /></div>
                <div class="team-name">{team}</div>
                <div class="poke-sub">{info['pokemon']} 팀</div>
                <div class="score-num">{total}</div>
                <div class="score-label">TOTAL PTS</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        # 라운드 수가 늘어나면 옵션 목록도 항상 새로 계산됨
        round_options = list(range(1, st.session_state.rounds + 1))

        # 현재 라운드 수보다 큰 값이 저장돼 있으면 보정
        if st.session_state.active_round[team] > st.session_state.rounds:
            st.session_state.active_round[team] = st.session_state.rounds

        sel_round = st.selectbox(
            "라운드",
            round_options,
            key=f"round_select_{team}",
            index=round_options.index(st.session_state.active_round[team])
            if st.session_state.active_round[team] in round_options
            else len(round_options) - 1,
            label_visibility="collapsed",
        )
        st.session_state.active_round[team] = sel_round

        score_input = st.number_input(
            f"{sel_round}R 점수",
            value=int(st.session_state.scores[team][sel_round - 1]),
            step=1,
            key=f"score_input_{team}_{sel_round}",
        )

        if st.button("⚡ 점수 등록", key=f"submit_{team}", use_container_width=True):
            st.session_state.scores[team][sel_round - 1] = score_input
            st.session_state.celebrate = team
            with st.spinner("반영 중..."):
                time.sleep(0.3)
            safe_rerun()

st.write("")
st.write("")

# ============================================================
# 컨트롤
# ============================================================
control_cols = st.columns([1, 1, 2])

with control_cols[0]:
    if st.button("➕ 새 라운드", use_container_width=True, key="add_round_btn"):
        st.session_state.rounds += 1
        for team in TEAMS:
            st.session_state.scores[team].append(0)
            st.session_state.active_round[team] = st.session_state.rounds
        st.toast(f"🆕 ROUND {st.session_state.rounds} 추가!", icon="🎉")
        safe_rerun()

with control_cols[1]:
    if st.button("🔄 초기화", use_container_width=True, key="reset_btn"):
        st.session_state.rounds = 1
        st.session_state.scores = {team: [0] for team in TEAMS}
        st.session_state.active_round = {team: 1 for team in TEAMS}
        st.session_state.celebrate = None
        st.toast("점수판이 초기화되었어요", icon="🧹")
        safe_rerun()

with control_cols[2]:
    st.markdown(
        f"""
        <div style="text-align:right;">
            <span class="round-pill">📍 ROUND {st.session_state.rounds} / 진행 중</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.markdown(
    """<h3 style="font-family:'Baloo 2',sans-serif; color:#3B3A45;">🏆 챔피언십 순위</h3>""",
    unsafe_allow_html=True,
)

ranking = sorted(
    [(team, sum(scores)) for team, scores in st.session_state.scores.items()],
    key=lambda x: x[1],
    reverse=True,
)
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

st.write("")
st.markdown(
    """<h3 style="font-family:'Baloo 2',sans-serif; color:#3B3A45;">📊 라운드별 기록</h3>""",
    unsafe_allow_html=True,
)

table_data = {f"{team}": st.session_state.scores[team] for team in TEAMS}
df = pd.DataFrame(table_data)
df.index = [f"R{i+1}" for i in range(st.session_state.rounds)]
df.loc["TOTAL"] = df.sum()
st.dataframe(df, use_container_width=True)

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
