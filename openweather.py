import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import datetime


#az extra megjelenéshez:
import plotly.graph_objects as go

#api kulcs a .toml fájlból
API_KEY=st.secrets["openweather"]["api_key"]

#-------------------------------- OLDAL JELLEMZŐK -------------------------------
st.set_page_config(
    page_title="🌤️ Időjárás Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
#----------------------------- INPUT MEZŐK JELLEMZŐI------------------------------
# sidebar inputok
st.sidebar.title("🌍 Hely kiválasztása")

city_name = st.sidebar.text_input("Város neve:", "Budapest")
country_code = st.sidebar.text_input("Ország kódja (pl. HU):", "HU")
#---------------------------------------------------------------------------------
# cache-elés és lekérés, url összeállítása
@st.cache_data(ttl=600)
def get_weather(city, country, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

data = get_weather(city_name, country_code, API_KEY)

#ha a lekérés hibára futna (nem 200-as status cod)
if data.get("cod") != 200:
    st.warning(f"Hiba történt a(z) **{city_name}, {country_code}** lekérdezésekor: {data.get('message', 'Ismeretlen hiba')}")
    st.stop()

#megfelelő adatok kinyerése
temp = data["main"]["temp"]
feels_like = data["main"]["feels_like"]
humidity = data["main"]["humidity"]
wind_speed = data["wind"]["speed"]
desc = data["weather"][0]["description"].capitalize()
icon = data["weather"][0]["icon"]
lat = data["coord"]["lat"]
lon = data["coord"]["lon"]
timestamp = datetime.datetime.fromtimestamp(data["dt"])

#---------------------------------- OLDAL FELSŐ RÉSZE -----------------------------------
# felső dashboard összeállítása, elosztása
st.title(f"🌤️ Időjárás Dashboard - {city_name}, {country_code}")
st.caption(f"⏰ Frissítve: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="🌡️ Hőmérséklet", value=f"{temp} °C")
with col2:
    st.metric(label="🥵 Hőérzet", value=f"{feels_like} °C")
with col3:
    st.metric(label="💧 Páratartalom", value=f"{humidity} %")
with col4:
    st.metric(label="💨 Szélsebesség", value=f"{wind_speed} m/s")

st.markdown("---")

#--------------------------------- KÖZÉPSŐ VIZUÁLIS MEGJELENÍTÉSEK----------------------
#az időjárás jellemzői
st.subheader(f"📋 Jelenlegi időjárás: {desc}")
st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png", width=100)

# a hőmérséklet és a hőérzet "gauge chart" megjelenítése
col1, col2 = st.columns(2)
with col1:
    st.subheader("🌡️ Hőmérséklet")
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=temp,
        gauge={'axis': {'range': [-30, 50]}, 'bar': {'color': "#FF5733"}},
        number={'suffix': " °C"},
        title={'text': "Hőmérséklet"}
    ))
    fig1.update_layout(height=250, margin=dict(t=30, b=10))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🥵 Hőérzet")
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=feels_like,
        gauge={'axis': {'range': [-30, 50]}, 'bar': {'color': "#33C1FF"}},
        number={'suffix': " °C"},
        title={'text': "Hőérzet"}
    ))
    fig2.update_layout(height=250, margin=dict(t=30, b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

#------------------------- ALSÓ TÉRKÉP SZAKASZ----------------------
#térkép hozzáadása
st.subheader(f"📍 {city_name}, {country_code} térképen")
st.map([{"lat": lat, "lon": lon}])
#-------------------------------------------------------------------


#A dizájnt teljes mértékben a chatgpt-re bíztam, azon kívül is sokszor kértem tőle segítséget, most ez a téma elég komplikált egyelőre.
#Kiegészítettem 1-2 dologgal a feladatot, például az ország inputtal, mert amikor teszteltem azt vettem észre, hogy a listában nem szereplő kisebb városra rákeresve
#valamilyen külföldi várost dobott be (amire 36 fok fölötti hőmérsékletet mutatott éppen).
