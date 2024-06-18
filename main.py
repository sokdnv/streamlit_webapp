import streamlit as st


def link_button(url, text):
    st.markdown(f'<a href="{url}" target="_blank"><button>{text}</button></a>', unsafe_allow_html=True)


# Название
st.title('Добро пожаловать')
st.divider()

st.page_link('pages/apple_stock.py', label='Акции apple', icon='📈')
st.page_link('pages/tips.py', label='Графики чаевых', icon='💶')

button = st.button('Нажми меня')

if button:
    st.balloons()
    link_button("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "И меня!")
