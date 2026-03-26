import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="Global Stock Analyzer", layout="wide")

st.title("📈 한-미 주요 주식 수익률 비교 대시보드")
st.sidebar.header("설정")

# 1. 주식 리스트 설정 (미국 및 한국)
ticker_dict = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "NAVER": "035420.KS",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
    "Microsoft": "MSFT",
    "S&P 500 (ETF)": "SPY"
}

# 2. 사이드바 사용자 입력
selected_stocks = st.sidebar.multiselect(
    "비교할 주식을 선택하세요",
    options=list(ticker_dict.keys()),
    default=["삼성전자", "Apple", "S&P 500 (ETF)"]
)

# 기간 선택
d = st.sidebar.date_input(
    "조회 기간",
    [datetime.now() - timedelta(days=365), datetime.now()]
)

if len(selected_stocks) > 0 and len(d) == 2:
    start_date, end_date = d
    
    # 데이터 불러오기
    tickers = [ticker_dict[s] for s in selected_stocks]
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    
    # 단일 종목 선택 시 Series를 DataFrame으로 변환
    if len(selected_stocks) == 1:
        data = data.to_frame()
        data.columns = selected_stocks
    else:
        # 컬럼명을 티커 대신 한글 이름으로 변경
        inv_ticker_dict = {v: k for k, v in ticker_dict.items()}
        data.columns = [inv_ticker_dict[t] for t in data.columns]

    # --- 시각화 부분 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("주가 흐름 (Closing Price)")
        st.line_chart(data)

    with col2:
        st.subheader("누적 수익률 (Cumulative Return %)")
        # 수익률 계산: (현재가 / 시작가 - 1) * 100
        returns = (data / data.iloc[0] - 1) * 100
        st.line_chart(returns)

    # 데이터 표 출력
    with st.expander("상세 데이터 보기"):
        st.dataframe(data.tail())
else:
    st.info("왼쪽 사이드바에서 주식을 선택하고 기간을 설정해주세요.")
