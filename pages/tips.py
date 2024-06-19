import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from io import BytesIO
import plotly.express as px
import matplotlib.dates as mpl_dates

plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')

# Название
st.header('Исследование по чаевым')
st.divider()
st.page_link('main.py', label='На главную', icon='🔙')

# Проверка наличия данных в сессионном состоянии
if 'tips' not in st.session_state:
    st.session_state.tips = None

# Загрузка датафрейма
data = st.sidebar.file_uploader('Загрузить датафрейм с чаевыми', type='csv')
button = st.sidebar.button('Загрузить подготовленный датафрейм')

if data:
    st.session_state.tips = pd.read_csv(data)
elif button:
    st.session_state.tips = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv")

# Использование ранее загруженного датафрейма
tips = st.session_state.tips

if tips is not None:
    # Ползунок для отображения датафрейма
    choice = st.sidebar.toggle('Показать датафрейм')

    if choice:
        st.sidebar.write(tips)

    # Предварительные вычисления
    if 'time_order' not in tips.columns:
        start_date = np.datetime64('2023-01-01')
        end_date = np.datetime64('2023-01-31')

        random_dates = start_date + np.random.randint(0, (end_date - start_date).astype('timedelta64[D]').astype(int) + 1,
                                                      len(tips))

        random_hours = np.random.randint(9, 23, len(tips))
        random_minutes = np.random.randint(0, 60, len(tips))

        tips['time_order'] = [date + np.timedelta64(hour, 'h') + np.timedelta64(minute, 'm')
                              for date, hour, minute in zip(random_dates, random_hours, random_minutes)]

    tips['tip %'] = tips['tip'] / tips['total_bill']
    tips['date_only'] = tips['time_order'].dt.date

    tips['day_of_week'] = tips['time_order'].dt.day_name()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    tips['day_of_week'] = pd.Categorical(tips['day_of_week'], categories=days_order, ordered=True)

    tips['time_only'] = tips['time_order'].dt.time

    def time_classificator(time):
        if 9 <= time.hour < 12:
            return "breakfast"
        elif 12 <= time.hour < 16:
            return "lunch"
        elif 16 <= time.hour < 23:
            return "dinner"


    tips['time_class'] = tips['time_only'].apply(time_classificator)

    tips_lunch = tips[tips['time_class'] == 'lunch']
    tips_dinner = tips[tips['time_class'] == 'dinner']

    # Функция для создания, отображения и скачивания графика
    def create_plot(title, xlabel, ylabel, plot_func, filename, *args, **kwargs):
        fig, ax = plt.subplots(figsize=(10, 6))
        plot_func(*args, **kwargs, ax=ax)
        ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        st.pyplot(fig)
        st.download_button(label=f"Скачать график: {title}", data=buf, file_name=f"{filename}.png", mime="image/png")
        st.divider()

    plot = st.selectbox('Выберите график', ['Динамика чаевых во времени',
                            'Распределение чеков',
                            'Связь между чеком и суммой чаевых',
                            'Распределение чаевых по дням недели',
                            'Распределение суммы чека по дням недели и приемам пищи',
                            'Распределение чаевых на обед и ланч',
                            'Распределение чаевых по полу и курению'])

    if plot == 'Динамика чаевых во времени':
        # График 1: Динамика чаевых во времени
        st.subheader('Динамика чаевых во времени')
        def plot_tip_dynamics(data, x, y, ax):
            sns.lineplot(data=data, x=x, y=y, ax=ax)
            ax.xaxis.set_major_formatter(mpl_dates.DateFormatter('%d/%m'))

        create_plot(
            title='Динамика чаевых',
            xlabel='Date',
            ylabel='Tip %',
            plot_func=plot_tip_dynamics,
            filename='tip_dynamics',
            data=tips, x='date_only', y='tip %'
        )

    elif plot == 'Распределение чеков':
        # График 2: Распределение чеков
        st.subheader('Распределение чеков')
        create_plot(
            title='Распределение чеков',
            xlabel='',
            ylabel='Сумма',
            plot_func=sns.histplot,
            filename='bill_distribution',
            data=tips, x='total_bill'
        )

    elif plot == 'Связь между чеком и суммой чаевых':
        # График 3: Связь между чеком и суммой чаевых
        st.subheader('Связь между чеком и суммой чаевых')
        create_plot(
            title='Зависимость чаевых от чека',
            xlabel='Сумма чека',
            ylabel='Чаевые',
            plot_func=sns.scatterplot,
            filename='tips_vs_bill',
            data=tips, x='total_bill', y='tip', size='tip %', sizes=(10, 100), legend=False
        )

    # График 4: Распределение чаевых по дням недели
    elif plot == 'Распределение чаевых по дням недели':
        st.subheader('Распределение чаевых по дням недели')
        create_plot(
            title='Распределение % чаевых по дням недели',
            xlabel='% чаевых',
            ylabel='',
            plot_func=sns.scatterplot,
            filename='tips_by_weekday',
            data=tips, y='day_of_week', x='tip %', hue='sex', palette={'Female': 'r', 'Male': 'b'}
        )

    elif plot == 'Распределение суммы чека по дням недели и приемам пищи':
        # График 5: Распределение суммы чека по дням недели и приемам пищи
        st.subheader('Распределение суммы чека по дням недели и приемам пищи')
        create_plot(
            title='Счета по дням недели',
            xlabel='',
            ylabel='Сумма чека',
            plot_func=sns.boxplot,
            filename='bills_by_weekday',
            data=tips, x='day_of_week', y='total_bill', hue='time_class', hue_order=['breakfast', 'lunch', 'dinner']
        )

    # График 6: Распределение чаевых на обед и ланч
    elif plot == 'Распределение чаевых на обед и ланч':
        st.subheader('Распределение чаевых на обед и ланч')

        fig_lunch = px.histogram(tips_lunch, x='tip %', title='Распределение чаевых во время ланча')
        fig_dinner = px.histogram(tips_dinner, x='tip %', title='Распределение чаевых во время обеда')

        fig_lunch.update_layout(xaxis_title='% чаевых', yaxis_title='')
        fig_dinner.update_layout(xaxis_title='% чаевых', yaxis_title='')

        st.plotly_chart(fig_lunch)
        st.plotly_chart(fig_dinner)
        st.divider()

    # График 7: Распределение чаевых по полу и курению
    elif plot == 'Распределение чаевых по полу и курению':
        st.subheader('Распределение чаевых по полу и курению')
        fig_male = px.scatter(tips[tips['sex'] == 'Male'], x='total_bill', y='tip', color='smoker',
                              title='Чаевые от мужчин', labels={'total_bill': 'Чек', 'tip': 'Чаевые'})
        fig_female = px.scatter(tips[tips['sex'] == 'Female'], x='total_bill', y='tip', color='smoker',
                                title='Чаевые от женщин', labels={'total_bill': 'Чек', 'tip': 'Чаевые'})

        st.plotly_chart(fig_male)
        st.plotly_chart(fig_female)

else:
    st.subheader("Загрузите датафрейм для продолжения.")
