import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="주식 비교 분석", layout="wide")

st.title("📈 한국 vs 미국 주식 수익률 비교")

# -------------------------------
# 주식 리스트
# -------------------------------
korean_stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS"
}

us_stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA"
}

# -------------------------------
# 사이드바
# -------------------------------
st.sidebar.header("📌 종목 선택")

selected_kor = st.sidebar.multiselect(
    "한국 주식",
    list(korean_stocks.keys()),
    default=["삼성전자"]
)

selected_us = st.sidebar.multiselect(
    "미국 주식",
    list(us_stocks.keys()),
    default=["Apple"]
)

period = st.sidebar.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "3y", "5y"],
    index=3
)

# -------------------------------
# 티커 정리
# -------------------------------
tickers = [korean_stocks[k] for k in selected_kor] + \
          [us_stocks[u] for u in selected_us]

if len(tickers) == 0:
    st.warning("종목을 선택하세요!")
    st.stop()

# -------------------------------
# 데이터 다운로드
# -------------------------------
with st.spinner("데이터 불러오는 중..."):
    data = yf.download(tickers, period=period)

# 👉 🔥 데이터 비어있으면 중단
if data.empty:
    st.error("데이터를 불러오지 못했습니다 😢 (티커 또는 네트워크 문제)")
    st.stop()

# -------------------------------
# Close 처리
# -------------------------------
try:
    if isinstance(data.columns, pd.MultiIndex):
        data = data["Close"]
    else:
        data = data[["Close"]]
except Exception:
    st.error("가격 데이터를 가져오지 못했습니다.")
    st.stop()

# 👉 🔥 NaN 제거
data = data.dropna()

# 👉 🔥 또 비면 중단
if data.empty:
    st.error("유효한 데이터가 없습니다.")
    st.stop()

# -------------------------------
# 수익률 계산 (안전)
# -------------------------------
base = data.iloc[0]

returns = (data / base - 1) * 100

# -------------------------------
# 그래프
# -------------------------------
st.subheader("📊 수익률 비교 (%)")
st.line_chart(returns)

# -------------------------------
# 테이블
# -------------------------------
st.subheader("📋 최근 데이터")
st.dataframe(returns.tail())

# -------------------------------
# 상세 분석
# -------------------------------
st.subheader("🔍 개별 종목 분석")

selected_detail = st.selectbox("종목 선택", tickers)

detail = yf.download(selected_detail, period=period)

if detail.empty:
    st.warning("해당 종목 데이터를 불러올 수 없습니다.")
else:
    st.line_chart(detail["Close"])
    st.write(detail.tail())
