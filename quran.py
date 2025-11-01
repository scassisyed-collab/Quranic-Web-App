import requests
import streamlit as st

# --- Page Setup ---
st.set_page_config(page_title="Quranic Web APP", layout="centered")

# --- Custom CSS for Arabic & English fonts ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri+Quran&display=swap');

    html, body, [class*="css"] {
        font-family: 'Amiri Quran', serif;
    }

    .quran-text {
        font-family: 'Amiri Quran', serif;
        font-size: 28px;
        direction: rtl;
        text-align: right;
        line-height: 2.3;
        margin-bottom: 12px;
    }

    .translation-text {
        font-family: 'Segoe UI', sans-serif;
        font-size: 18px;
        color: #333333;
        direction: ltr;
        text-align: left;
        margin-bottom: 25px;
    }

    .ayah-number {
        color: #888;
        font-size: 16px;
    }

    .header {
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1 class='header'>📖 Quranic Web APP</h1>", unsafe_allow_html=True)

# --- Fetch Surah list with caching ---
@st.cache_data
def get_surah_list():
    try:
        res = requests.get("https://api.alquran.cloud/v1/surah")
        res.raise_for_status()
        return res.json()["data"]
    except Exception:
        st.error("⚠️ Unable to fetch Surah list. Please check your connection.")
        st.stop()

surahs = get_surah_list()
surahIndex = [f"{s['number']}. {s['name']} - {s['englishName']}" for s in surahs]

# --- Sidebar Controls ---
st.sidebar.title("⚙️ Controls")
surahname = st.sidebar.selectbox("Select Surah", surahIndex)
surahnum = int(surahname.split(".")[0])

reciters = [
    "ar.abdurrahmaansudais",
    "ar.saoodshuraym",
    "ar.mahermuaiqly",
    "ar.alafasy"
]

reciter = st.sidebar.selectbox("Select Reciter", reciters)
show_recitation = st.sidebar.checkbox("🎧 Show Recitation", value=False)
show_translation = st.sidebar.checkbox("🌐 Show English Translation", value=False)

# --- Fetch Surah Data (Arabic + optionally Translation) ---
@st.cache_data
def get_surah_data(surahnum, reciter):
    res = requests.get(f"https://api.alquran.cloud/v1/surah/{surahnum}/{reciter}")
    res.raise_for_status()
    return res.json()["data"]["ayahs"]

@st.cache_data
def get_translation_data(surahnum):
    res = requests.get(f"https://api.alquran.cloud/v1/surah/{surahnum}/en.asad")
    res.raise_for_status()
    return res.json()["data"]["ayahs"]

try:
    arabic_ayahs = get_surah_data(surahnum, reciter)
    translations = get_translation_data(surahnum) if show_translation else None
except Exception:
    st.error("⚠️ Unable to fetch Surah or translation data. Please try again later.")
    st.stop()

# --- Display Surah Header ---
surah_meta = next(s for s in surahs if s['number'] == surahnum)
st.markdown(f"### {surah_meta['englishName']} ({surah_meta['englishNameTranslation']})")
st.markdown(f"**Arabic Name:** {surah_meta['name']}  | **Ayahs:** {surah_meta['numberOfAyahs']}")

st.markdown("---")

# --- Display Each Ayah ---
for i, ayah in enumerate(arabic_ayahs):
    st.markdown(f"<div class='quran-text'>{ayah['text']}</div>", unsafe_allow_html=True)
    if show_translation:
        st.markdown(f"<div class='translation-text'><b>Translation:</b> {translations[i]['text']}</div>", unsafe_allow_html=True)
    if show_recitation:
        st.audio(ayah["audio"])

st.success("✅ End of Surah")
