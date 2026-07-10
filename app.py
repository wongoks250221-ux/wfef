import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import streamlit.components.v1 as components

# 페이지 제목 설정
st.set_page_config(page_title="안산시 소화전 위치 안내", layout="wide")
st.title("📍 안산시 소화전 위치 현황 Map")

# ==========================================
# 1. 브라우저 실시간 GPS 좌표 가져오기 (Streamlit 호환 HTML/JS 사용)
# ==========================================
@st.cache_data
def get_location_component():
    # 브라우저의 Geolocation API를 사용하여 좌표를 streamlit 세션 상태로 전달하는 컴포넌트
    js_code = """
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: {lat: lat, lng: lng}}, '*');
        },
        (error) => {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: {lat: 37.321877, lng: 126.830883}}, '*');
        }
    );
    </script>
    """
    return components.html(js_code, height=0, width=0)

# 위치 추적 컴포넌트 실행
location_data = get_location_component()

# 기본 좌표 지정 (안산시청)
my_lat, my_lng = 37.321877, 126.830883

# 브라우저에서 받아온 좌표가 있으면 업데이트
if st.session_state.get('location_value'):
    my_lat = st.session_state['location_value']['lat']
    my_lng = st.session_state['location_value']['lng']

st.sidebar.write(f"현재 기준 위도: {my_lat:.6f}, 경도: {my_lng:.6f}")

# ==========================================
# 2. 소화전 CSV 파일 로드
# ==========================================
# ⚠️ 파일 경로는 본인의 프로젝트 폴더 내부 경로에 맞게 맞춰주세요. (같은 폴더에 두는 걸 추천)
file_path = '경기도 안산시_소화전위치 현황_20260112.csv'

@st.cache_data
def load_data(path):
    try:
        return pd.read_csv(path, encoding='utf-8')
    except:
        return pd.read_csv(path, encoding='cp949') # 인코딩 에러 방지 방어코드

df = load_data(file_path)

# 사이드바에 행정동 필터 추가 기능 (스트림릿만의 장점!)
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
# 4. 최종 지도 화면에 표시 (Streamlit 방식)
# ==========================================
st_folium(m, width=1000, height=600, returned_objects=[])
