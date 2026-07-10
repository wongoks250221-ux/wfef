import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval

# 페이지 제목 설정
st.set_page_config(page_title="안산시 소화전 위치 안내", layout="wide")
st.title("📍 안산시 소화전 위치 현황 Map")

# ==========================================
# 1. 브라우저 실시간 GPS 좌표 가져오기 (안정적인 라이브러리 방식)
# ==========================================
# 기본 좌표 지정 (안산시청)
my_lat, my_lng = 37.321877, 126.830883

# 브라우저에 직접 위치 정보 요청
location = streamlit_js_eval(data_of='geolocation', target_at='data', key='geo')

if location:
    my_lat = location['coords']['latitude']
    my_lng = location['coords']['longitude']
    st.sidebar.success("✅ 실시간 GPS 위치 감지 성공!")
else:
    st.sidebar.warning("💡 위치 확인 중이거나 권한이 필요합니다. (기본: 안산시청)")

st.sidebar.write(f"현재 기준 위도: {my_lat:.6f}, 경도: {my_lng:.6f}")

# ==========================================
# 2. 소화전 CSV 파일 로드
# ==========================================
file_path = '경기도 안산시_소화전위치 현황_20260112.csv'

@st.cache_data
def load_data(path):
    try:
        return pd.read_csv(path, encoding='utf-8')
    except:
        return pd.read_csv(path, encoding='cp949')

df = load_data(file_path)

# 사이드바에 행정동 필터 추가
all_dongs = ["전체"] + list(df['행정읍면동'].dropna().unique())
selected_dong = st.sidebar.selectbox("🔎 행정동 선택", all_dongs)

if selected_dong != "전체":
    df = df[df['행정읍면동'] == selected_dong]

# ==========================================
# 3. 지도 생성 및 마커 찍기
# ==========================================
m = folium.Map(location=[my_lat, my_lng], zoom_start=15)

# 내 위치 마커 (파란색 별 모양)
folium.Marker(
    location=[my_lat, my_lng],
    popup=folium.Popup("<b>🙋‍♂️ 현재 내 위치</b>", max_width=200),
    icon=folium.Icon(color='blue', icon='star', prefix='fa'),
).add_to(m)

# 소화전 마커 클러스터
marker_cluster = MarkerCluster().add_to(m)

for idx, row in df.iterrows():
    lat = row['위도']
    lng = row['경도']
    addr = row['주소']
    dong = row['행정읍면동']
    type_fire = row['소화전형식']

    if pd.notna(lat) and pd.notna(lng):
        popup_text = f"""
        <div style='width:200px;'>
            <b>📍 {dong} 소화전</b><br>
            • 형식: {type_fire}<br>
            • 주소: {addr}
        </div>
        """
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color='red', icon='fire', prefix='fa')
        ).add_to(marker_cluster)

# ==========================================
# 4. 최종 지도 화면에 표시
# ==========================================
st_folium(m, width=1000, height=600, returned_objects=[])
