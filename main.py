import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Space+Mono:wght@400;700&display=swap');

  /* Global */
  html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: #0a0e1a;
    color: #e8eaf0;
  }
  .main { background-color: #0a0e1a; }
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1220 0%, #111827 100%);
    border-right: 1px solid #1e2a3a;
  }

  /* Header */
  .dashboard-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
  }
  .dashboard-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 60%;
    height: 200%;
    background: radial-gradient(ellipse, rgba(56,189,248,0.06) 0%, transparent 70%);
    pointer-events: none;
  }
  .header-title {
    font-family: 'Space Mono', monospace;
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
  }
  .header-sub {
    color: #64748b;
    font-size: 0.85rem;
    margin: 0;
    letter-spacing: 0.03em;
  }
  .live-badge {
    display: inline-block;
    background: rgba(34,197,94,0.15);
    border: 1px solid rgba(34,197,94,0.4);
    color: #4ade80;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    padding: 3px 10px;
    border-radius: 20px;
    margin-left: 12px;
    vertical-align: middle;
    letter-spacing: 0.1em;
    animation: pulse 2s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* Metric Cards */
  .metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
  }
  .metric-card {
    background: linear-gradient(135deg, #111827, #1a2235);
    border: 1px solid #1e2a3a;
    border-radius: 12px;
    padding: 16px 18px;
    transition: border-color 0.2s, transform 0.2s;
    position: relative;
    overflow: hidden;
  }
  .metric-card:hover {
    border-color: #38bdf8;
    transform: translateY(-2px);
  }
  .metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 12px 12px 0 0;
  }
  .metric-card.up::after   { background: linear-gradient(90deg, #4ade80, #22d3ee); }
  .metric-card.down::after { background: linear-gradient(90deg, #f87171, #fb923c); }
  .metric-card.neu::after  { background: linear-gradient(90deg, #64748b, #94a3b8); }
  .metric-ticker  { font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #64748b; letter-spacing: 0.1em; margin-bottom: 4px; }
  .metric-name    { font-size: 0.78rem; color: #94a3b8; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .metric-price   { font-family: 'Space Mono', monospace; font-size: 1.15rem; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; }
  .metric-return  { font-family: 'Space Mono', monospace; font-size: 0.9rem; font-weight: 700; }
  .metric-return.up   { color: #4ade80; }
  .metric-return.down { color: #f87171; }
  .metric-return.neu  { color: #94a3b8; }
  .metric-vol { font-size: 0.7rem; color: #475569; margin-top: 4px; }

  /* Section label */
  .section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    color: #38bdf8;
    text-transform: uppercase;
    margin: 28px 0 10px 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1e3a5f, transparent);
  }

  /* Sidebar styling */
  .sidebar-section {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 12px;
    border: 1px solid #1e2a3a;
  }
  .sidebar-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    color: #38bdf8;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  /* Streamlit overrides */
  div[data-testid="stMetric"] { display: none; }
  .stMultiSelect [data-baseweb="tag"] {
    background-color: #1e3a5f !important;
    border-color: #38bdf8 !important;
  }
  .stSelectbox > div, .stMultiSelect > div {
    background-color: #111827 !important;
  }
  div.stButton > button {
    background: linear-gradient(135deg, #0369a1, #1d4ed8);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    padding: 8px 20px;
    width: 100%;
    transition: opacity 0.2s;
  }
  div.stButton > button:hover { opacity: 0.85; }

  /* Comparison table */
  .compare-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    margin-top: 10px;
  }
  .compare-table th {
    background: #111827;
    color: #64748b;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 10px 12px;
    border-bottom: 1px solid #1e2a3a;
    text-align: left;
  }
  .compare-table td {
    padding: 10px 12px;
    border-bottom: 1px solid rgba(30,42,58,0.5);
    color: #cbd5e1;
  }
  .compare-table tr:hover td { background: rgba(56,189,248,0.04); }
  .tag-kr { background: rgba(239,68,68,0.15); color: #f87171; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-family: 'Space Mono', monospace; }
  .tag-us { background: rgba(59,130,246,0.15); color: #60a5fa; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-family: 'Space Mono', monospace; }

  /* Chart wrapper */
  .chart-wrapper {
    background: #0d1220;
    border: 1px solid #1e2a3a;
    border-radius: 14px;
    padding: 4px;
    margin-bottom: 16px;
  }

  /* Tooltip-like info box */
  .info-box {
    background: rgba(56,189,248,0.07);
    border-left: 3px solid #38bdf8;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 0.78rem;
    color: #94a3b8;
    margin-bottom: 16px;
  }
  
  /* Hide streamlit default elements */
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Stock Universe ────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS",
    "POSCO홀딩스": "005490.KS",
    "카카오": "035720.KS",
    "NAVER": "035420.KS",
    "셀트리온": "068270.KS",
    "기아": "000270.KS",
    "LG화학": "051910.KS",
    "삼성SDI": "006400.KS",
    "KB금융": "105560.KS",
    "신한지주": "055550.KS",
    "하나금융지주": "086790.KS",
}

US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B",
    "Eli Lilly": "LLY",
    "JPMorgan Chase": "JPM",
    "Visa": "V",
    "ExxonMobil": "XOM",
    "Johnson & Johnson": "JNJ",
    "Broadcom": "AVGO",
    "Netflix": "NFLX",
}

INDICES = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "다우존스": "^DJI",
}

PERIOD_MAP = {
    "1개월": ("1mo", 30),
    "3개월": ("3mo", 90),
    "6개월": ("6mo", 180),
    "1년":   ("1y",  365),
    "2년":   ("2y",  730),
    "5년":   ("5y",  1825),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(tickers: list, period: str) -> dict:
    result = {}
    for ticker in tickers:
        try:
            obj = yf.Ticker(ticker)
            df = obj.history(period=period)
            if df.empty:
                continue
            df.index = pd.to_datetime(df.index).tz_localize(None)
            result[ticker] = df
        except Exception:
            pass
    return result

def calc_return(df: pd.DataFrame) -> float:
    if df is None or len(df) < 2:
        return 0.0
    return (df["Close"].iloc[-1] / df["Close"].iloc[0] - 1) * 100

def latest_price(df: pd.DataFrame) -> float:
    if df is None or df.empty:
        return 0.0
    return df["Close"].iloc[-1]

def daily_change(df: pd.DataFrame) -> float:
    if df is None or len(df) < 2:
        return 0.0
    return (df["Close"].iloc[-1] / df["Close"].iloc[-2] - 1) * 100

def calc_volatility(df: pd.DataFrame) -> float:
    if df is None or len(df) < 5:
        return 0.0
    returns = df["Close"].pct_change().dropna()
    return returns.std() * np.sqrt(252) * 100

def return_class(v: float) -> str:
    if v > 0:   return "up"
    if v < 0:   return "down"
    return "neu"

def fmt_return(v: float) -> str:
    sign = "▲" if v > 0 else ("▼" if v < 0 else "–")
    return f"{sign} {abs(v):.2f}%"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">📊 대시보드 설정</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">⏱ 조회 기간</div>', unsafe_allow_html=True)
        period_label = st.selectbox("", list(PERIOD_MAP.keys()), index=3, label_visibility="collapsed")
        period_str, _ = PERIOD_MAP[period_label]
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🇰🇷 한국 주식 선택</div>', unsafe_allow_html=True)
        kr_default = ["삼성전자", "SK하이닉스", "NAVER", "현대차"]
        selected_kr_names = st.multiselect("", list(KR_STOCKS.keys()), default=kr_default, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">🇺🇸 미국 주식 선택</div>', unsafe_allow_html=True)
        us_default = ["Apple", "NVIDIA", "Microsoft", "Tesla"]
        selected_us_names = st.multiselect("", list(US_STOCKS.keys()), default=us_default, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">📉 차트 유형</div>', unsafe_allow_html=True)
        chart_type = st.selectbox("", ["캔들스틱", "라인 차트", "영역 차트"], label_visibility="collapsed")
        show_volume = st.checkbox("거래량 표시", value=False)
        show_ma = st.checkbox("이동평균선 표시 (20일, 60일)", value=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📌 지수 표시</div>', unsafe_allow_html=True)
    show_indices = st.checkbox("주요 지수 수익률 포함", value=True)
    st.markdown('</div>', unsafe_allow_html=True)

    refresh = st.button("🔄  데이터 새로고침")
    if refresh:
        st.cache_data.clear()
        st.rerun()

# ── Build Ticker Lists ────────────────────────────────────────────────────────
selected_kr = {name: KR_STOCKS[name] for name in selected_kr_names}
selected_us = {name: US_STOCKS[name] for name in selected_us_names}
all_tickers = list(selected_kr.values()) + list(selected_us.values())
if show_indices:
    all_tickers += list(INDICES.values())

# ── Fetch ─────────────────────────────────────────────────────────────────────
with st.spinner("시장 데이터 불러오는 중..."):
    data = fetch_data(all_tickers, period_str)

# ── Header ────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%Y.%m.%d %H:%M")
st.markdown(f"""
<div class="dashboard-header">
  <p class="header-title">글로벌 주식 비교 <span class="live-badge">LIVE</span></p>
  <p class="header-sub">한국 · 미국 주요 종목 수익률 & 차트 비교 대시보드 &nbsp;|&nbsp; {now_str} 기준 &nbsp;|&nbsp; 조회 기간: {period_label}</p>
</div>
""", unsafe_allow_html=True)

# ── Metric Cards – Korean ─────────────────────────────────────────────────────
if selected_kr_names:
    st.markdown('<div class="section-label">🇰🇷 한국 주식</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(selected_kr_names), 5))
    for i, (name, ticker) in enumerate(selected_kr.items()):
        df = data.get(ticker)
        ret = calc_return(df)
        price = latest_price(df)
        vol = calc_volatility(df)
        cls = return_class(ret)
        with cols[i % min(len(selected_kr_names), 5)]:
            st.markdown(f"""
            <div class="metric-card {cls}">
              <div class="metric-ticker">{ticker}</div>
              <div class="metric-name">{name}</div>
              <div class="metric-price">₩{price:,.0f}</div>
              <div class="metric-return {cls}">{fmt_return(ret)}</div>
              <div class="metric-vol">변동성 {vol:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

# ── Metric Cards – US ─────────────────────────────────────────────────────────
if selected_us_names:
    st.markdown('<div class="section-label">🇺🇸 미국 주식</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(selected_us_names), 5))
    for i, (name, ticker) in enumerate(selected_us.items()):
        df = data.get(ticker)
        ret = calc_return(df)
        price = latest_price(df)
        vol = calc_volatility(df)
        cls = return_class(ret)
        with cols[i % min(len(selected_us_names), 5)]:
            st.markdown(f"""
            <div class="metric-card {cls}">
              <div class="metric-ticker">{ticker}</div>
              <div class="metric-name">{name}</div>
              <div class="metric-price">${price:,.2f}</div>
              <div class="metric-return {cls}">{fmt_return(ret)}</div>
              <div class="metric-vol">변동성 {vol:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

# ── Index Metrics ─────────────────────────────────────────────────────────────
if show_indices:
    st.markdown('<div class="section-label">📊 주요 지수</div>', unsafe_allow_html=True)
    idx_cols = st.columns(len(INDICES))
    for i, (name, ticker) in enumerate(INDICES.items()):
        df = data.get(ticker)
        ret = calc_return(df)
        price = latest_price(df)
        cls = return_class(ret)
        with idx_cols[i]:
            st.markdown(f"""
            <div class="metric-card {cls}">
              <div class="metric-ticker">{ticker}</div>
              <div class="metric-name">{name}</div>
              <div class="metric-price">{price:,.2f}</div>
              <div class="metric-return {cls}">{fmt_return(ret)}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Normalized Return Chart (All in one) ─────────────────────────────────────
st.markdown('<div class="section-label">📈 누적 수익률 비교</div>', unsafe_allow_html=True)
st.markdown('<div class="info-box">첫 거래일을 0%로 정규화하여 모든 종목의 수익률을 동일 기준으로 비교합니다.</div>', unsafe_allow_html=True)

fig_norm = go.Figure()
color_kr = px.colors.sequential.Reds_r[:len(selected_kr)]
color_us = px.colors.sequential.Blues_r[:len(selected_us)]

for i, (name, ticker) in enumerate(selected_kr.items()):
    df = data.get(ticker)
    if df is None or df.empty: continue
    norm = (df["Close"] / df["Close"].iloc[0] - 1) * 100
    fig_norm.add_trace(go.Scatter(
        x=norm.index, y=norm.values, name=f"🇰🇷 {name}",
        line=dict(width=2, color=f"hsl({355 - i*25},70%,{65 - i*5}%)"),
        hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>수익률: %{{y:.2f}}%<extra></extra>",
    ))

for i, (name, ticker) in enumerate(selected_us.items()):
    df = data.get(ticker)
    if df is None or df.empty: continue
    norm = (df["Close"] / df["Close"].iloc[0] - 1) * 100
    fig_norm.add_trace(go.Scatter(
        x=norm.index, y=norm.values, name=f"🇺🇸 {name}",
        line=dict(width=2, dash="dot", color=f"hsl({220 - i*15},75%,{65 - i*4}%)"),
        hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>수익률: %{{y:.2f}}%<extra></extra>",
    ))

fig_norm.add_hline(y=0, line_dash="dash", line_color="rgba(100,116,139,0.4)")
fig_norm.update_layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Noto Sans KR", color="#94a3b8"),
    legend=dict(bgcolor="rgba(15,23,42,0.8)", bordercolor="#1e2a3a", borderwidth=1,
                font=dict(size=11)),
    hovermode="x unified",
    xaxis=dict(gridcolor="#1e2a3a", showline=False, zeroline=False),
    yaxis=dict(gridcolor="#1e2a3a", showline=False, zeroline=False,
               ticksuffix="%"),
    margin=dict(l=10, r=10, t=20, b=10),
    height=420,
)

st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
st.plotly_chart(fig_norm, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Bar Chart: Return Ranking ─────────────────────────────────────────────────
st.markdown('<div class="section-label">🏆 수익률 순위</div>', unsafe_allow_html=True)
rank_data = []
for name, ticker in {**selected_kr, **selected_us}.items():
    df = data.get(ticker)
    if df is not None:
        ret = calc_return(df)
        market = "🇰🇷 KR" if ticker in selected_kr.values() else "🇺🇸 US"
        rank_data.append({"종목": name, "수익률": ret, "시장": market})

if rank_data:
    rank_df = pd.DataFrame(rank_data).sort_values("수익률", ascending=True)
    colors = ["#f87171" if v < 0 else "#4ade80" for v in rank_df["수익률"]]
    fig_bar = go.Figure(go.Bar(
        x=rank_df["수익률"], y=rank_df["종목"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.2f}%" for v in rank_df["수익률"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>수익률: %{x:.2f}%<extra></extra>",
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Noto Sans KR", color="#94a3b8"),
        xaxis=dict(gridcolor="#1e2a3a", zeroline=True, zerolinecolor="#334155",
                   ticksuffix="%"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=80, t=10, b=10),
        height=max(280, len(rank_df) * 38),
        showlegend=False,
    )
    fig_bar.add_vline(x=0, line_color="rgba(100,116,139,0.4)")
    st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Individual Candle Charts ──────────────────────────────────────────────────
all_selected = {**selected_kr, **selected_us}
if all_selected:
    st.markdown('<div class="section-label">🕯️ 개별 종목 차트</div>', unsafe_allow_html=True)
    
    chart_name = st.selectbox("종목 선택", list(all_selected.keys()))
    chart_ticker = all_selected[chart_name]
    df_chart = data.get(chart_ticker)

    if df_chart is not None and not df_chart.empty:
        rows = 2 if show_volume else 1
        row_heights = [0.7, 0.3] if show_volume else [1.0]
        fig_candle = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                                   vertical_spacing=0.04, row_heights=row_heights)

        if chart_type == "캔들스틱":
            fig_candle.add_trace(go.Candlestick(
                x=df_chart.index, open=df_chart["Open"], high=df_chart["High"],
                low=df_chart["Low"], close=df_chart["Close"], name=chart_name,
                increasing=dict(line=dict(color="#4ade80"), fillcolor="rgba(74,222,128,0.3)"),
                decreasing=dict(line=dict(color="#f87171"), fillcolor="rgba(248,113,113,0.3)"),
            ), row=1, col=1)
        elif chart_type == "라인 차트":
            fig_candle.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart["Close"], name=chart_name,
                line=dict(color="#38bdf8", width=2),
                fill=None,
            ), row=1, col=1)
        else:  # 영역 차트
            fig_candle.add_trace(go.Scatter(
                x=df_chart.index, y=df_chart["Close"], name=chart_name,
                line=dict(color="#38bdf8", width=2),
                fill="tozeroy", fillcolor="rgba(56,189,248,0.08)",
            ), row=1, col=1)

        if show_ma and len(df_chart) >= 20:
            ma20 = df_chart["Close"].rolling(20).mean()
            fig_candle.add_trace(go.Scatter(
                x=df_chart.index, y=ma20, name="MA20",
                line=dict(color="#f59e0b", width=1.5, dash="dot"),
            ), row=1, col=1)
        if show_ma and len(df_chart) >= 60:
            ma60 = df_chart["Close"].rolling(60).mean()
            fig_candle.add_trace(go.Scatter(
                x=df_chart.index, y=ma60, name="MA60",
                line=dict(color="#818cf8", width=1.5, dash="dash"),
            ), row=1, col=1)

        if show_volume:
            vol_colors = ["#4ade80" if c >= o else "#f87171"
                          for c, o in zip(df_chart["Close"], df_chart["Open"])]
            fig_candle.add_trace(go.Bar(
                x=df_chart.index, y=df_chart["Volume"], name="거래량",
                marker_color=vol_colors, showlegend=False,
            ), row=2, col=1)

        fig_candle.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Noto Sans KR", color="#94a3b8"),
            xaxis_rangeslider_visible=False,
            legend=dict(bgcolor="rgba(15,23,42,0.8)", bordercolor="#1e2a3a", borderwidth=1),
            hovermode="x unified",
            margin=dict(l=10, r=10, t=20, b=10),
            height=500 if show_volume else 420,
        )
        for axis in ["xaxis", "xaxis2", "yaxis", "yaxis2"]:
            fig_candle.update_layout(**{axis: dict(gridcolor="#1e2a3a", showline=False, zeroline=False)})

        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.plotly_chart(fig_candle, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Comparison Table ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">📋 종합 비교 테이블</div>', unsafe_allow_html=True)

rows_html = ""
for name, ticker in {**selected_kr, **selected_us}.items():
    df = data.get(ticker)
    if df is None or df.empty:
        continue
    market = "KR" if ticker in selected_kr.values() else "US"
    tag_cls = "tag-kr" if market == "KR" else "tag-us"
    price = latest_price(df)
    currency = "₩" if market == "KR" else "$"
    price_fmt = f"{currency}{price:,.0f}" if market == "KR" else f"{currency}{price:,.2f}"
    ret = calc_return(df)
    d_change = daily_change(df)
    vol = calc_volatility(df)
    ret_cls = "up" if ret > 0 else ("down" if ret < 0 else "neu")
    color_map = {"up": "#4ade80", "down": "#f87171", "neu": "#94a3b8"}
    ret_color = color_map[ret_cls]
    rows_html += f"""
    <tr>
      <td><span class="{tag_cls}">{market}</span></td>
      <td style="font-family:'Space Mono',monospace;font-size:0.75rem;color:#64748b">{ticker}</td>
      <td style="color:#e2e8f0;font-weight:500">{name}</td>
      <td style="font-family:'Space Mono',monospace">{price_fmt}</td>
      <td style="font-family:'Space Mono',monospace;color:{ret_color}">{fmt_return(ret)}</td>
      <td style="font-family:'Space Mono',monospace;color:{'#4ade80' if d_change>0 else '#f87171'}">{fmt_return(d_change)}</td>
      <td style="font-family:'Space Mono',monospace;color:#94a3b8">{vol:.1f}%</td>
    </tr>
    """

st.markdown(f"""
<div style="background:#0d1220;border:1px solid #1e2a3a;border-radius:14px;padding:16px;overflow-x:auto;">
<table class="compare-table">
  <thead><tr>
    <th>시장</th><th>티커</th><th>종목명</th>
    <th>현재가</th><th>기간 수익률</th><th>전일 대비</th><th>연환산 변동성</th>
  </tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

# ── Correlation Heatmap ───────────────────────────────────────────────────────
combined_tickers = {**selected_kr, **selected_us}
if len(combined_tickers) >= 3:
    st.markdown('<div class="section-label">🔗 상관관계 히트맵</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">일간 수익률 기준 종목 간 상관관계. 1에 가까울수록 같은 방향으로 움직이는 경향이 있습니다.</div>', unsafe_allow_html=True)

    price_dict = {}
    for name, ticker in combined_tickers.items():
        df = data.get(ticker)
        if df is not None and len(df) > 5:
            price_dict[name] = df["Close"]

    if len(price_dict) >= 3:
        price_df = pd.DataFrame(price_dict).dropna()
        ret_df = price_df.pct_change().dropna()
        corr = ret_df.corr()

        fig_heat = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns, y=corr.index,
            colorscale=[
                [0.0, "#f87171"], [0.4, "#1e293b"],
                [0.5, "#1e293b"], [0.6, "#1e293b"],
                [1.0, "#4ade80"],
            ],
            zmid=0, zmin=-1, zmax=1,
            text=np.round(corr.values, 2),
            texttemplate="%{text}",
            textfont=dict(size=11, family="Space Mono"),
            hovertemplate="%{y} × %{x}<br>상관계수: %{z:.3f}<extra></extra>",
        ))
        fig_heat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Noto Sans KR", color="#94a3b8"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=max(320, len(price_dict) * 42),
        )
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:40px;padding:20px;text-align:center;border-top:1px solid #1e2a3a;">
  <p style="color:#334155;font-size:0.72rem;font-family:'Space Mono',monospace;letter-spacing:0.08em">
    데이터 출처: Yahoo Finance (yfinance) &nbsp;|&nbsp; 투자 참고용 자료이며 투자 권유가 아닙니다 &nbsp;|&nbsp; 실시간 데이터가 아닐 수 있습니다
  </p>
</div>
""", unsafe_allow_html=True)
