import pandas as pd
import mplfinance as mpf
import streamlit as st
import yfinance as yf


# Название
st.header('Котировки компании Apple')
st.divider()

# Описание
st.caption('С использованием yfinance')

st.page_link('main.py', label='На главную', icon='🔙')

# Выбор периода
period = st.sidebar.radio('Интервал', ['1д', '5д', '1м', '6м', '1г'], horizontal=True)
slider = st.sidebar.toggle('Показать объём')

# словарь периода + интервала
date_dict = {
    '1д': ['1d', '5m'],
    '5д': ['5d', '30m'],
    '1м': ['1mo', '90m'],
    '6м': ['6mo', '1wk'],
    '1г': ['1y', '1wk']
}

# добыча информации об акции
apple_stock = yf.Ticker("AAPL")
period_tuple = date_dict.get(period)
data = apple_stock.history(period=period_tuple[0], interval=period_tuple[1]).reset_index()

# задаём формат для дат
try:
    data['Datetime'] = pd.to_datetime(data['Datetime'])
    data.set_index('Datetime', inplace=True)
except KeyError:
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)

# меняем названия столбцов для совместимости с mplfinance для построения свечей
data.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low',
                     'Close': 'close', 'Volume': 'volume'}, inplace=True)

# Построение графика с объемом на второй оси
fig, ax = mpf.plot(data,
                   type='candle',
                   volume=True if slider else False,
                   title=f'График стоимости акций Apple за {period}',
                   ylabel='Стоимость $',
                   datetime_format='%d-%b' if period != '1д' else '%H:%M',
                   style='binance',
                   xrotation=0,
                   figscale=1.2,
                   tight_layout=True,
                   returnfig=True)

# отображение графика
st.set_option('deprecation.showPyplotGlobalUse', False)
st.pyplot(fig)
