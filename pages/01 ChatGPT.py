import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="주식 비교 분석", layout="wide")

st.title("📈 한국 vs 미국 주식 수익률 비교")

# -------------------------------
# 기본 주식 리스트
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
# 사용자 선택
# -------------------------------
st.sidebar.header("📌 종목 선택")

selected_kor = st.sidebar.multiselect(
    "한국 주식 선택",
    list(korean_stocks.keys()),
    default=["삼성전자"]
)

selected_us = st.sidebar.multiselect(
    "미국 주식 선택",
    list(us_stocks.keys()),
    default=["Apple"]
)

period = st.sidebar.selectbox(
    "기간 선택",
    ["1mo", "3mo", "6mo", "1y", "3y", "5y"],
    index=3
)

# -------------------------------
# 데이터 가져오기
# -------------------------------
tickers = []

for k in selected_kor:
    tickers.append(korean_stocks[k])

for u in selected_us:
    tickers.append(us_stocks[u])

if len(tickers) == 0:
    st.warning("종목을 하나 이상 선택하세요!")
    st.stop()

data = yf.download(tickers, period=period)["Adj Close"]

# -------------------------------
# 수익률 계산
# -------------------------------
returns = (data / data.iloc[0] - 1) * 100

# -------------------------------
# 그래프 출력
# -------------------------------
st.subheader("📊 수익률 비교 (%)")

fig, ax = plt.subplots(figsize=(10, 5))

for col in returns.columns:
    ax.plot(returns.index, returns[col], label=col)

ax.set_ylabel("수익률 (%)")
ax.legend()
ax.grid()

st.pyplot(fig)

# -------------------------------
# 데이터 테이블
# -------------------------------
st.subheader("📋 수익률 데이터")

st.dataframe(returns.tail())

# -------------------------------
# 개별 종목 상세 보기
# -------------------------------
st.subheader("🔍 개별 종목 상세 분석")

selected_detail = st.selectbox(
    "종목 선택",
    tickers
)

detail_data = yf.download(selected_detail, period=period)

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(detail_data.index, detail_data["Close"])
ax2.set_title(f"{selected_detail} 가격")
ax2.grid()

st.pyplot(fig2)

st.write(detail_data.tail())
