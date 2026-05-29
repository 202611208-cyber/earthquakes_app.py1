import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 레이아웃 확장
st.set_page_config(layout="wide")

st.title("세계 지진 위험도 분석 시스템")
st.write("위도와 경도를 입력하면 주변 지진 데이터를 기반으로 위험도를 분석합니다.")

# 1. 데이터 로드
try:
    df_new = pd.read_csv("deploy_earthquakes.csv")
except FileNotFoundError:
    st.error("🚨 'deploy_earthquakes.csv' 파일을 찾을 수 없습니다.")
    st.stop()

# 군집 설정
risk_dict = {0: '높음', 1: '낮음', 2: '중간'}
colors = {0: 'red', 1: 'blue', 2: 'green'}

# 2. 사용자 입력창 정의
lat = st.number_input("위도 입력", value=37.5)
lon = st.number_input("경도 입력", value=127.0)

# 결과 출력이 들어갈 상단 공간 확보
result_container = st.container()

# 지도 기본 설정
m = folium.Map(
    location=[0, 0], 
    zoom_start=2, 
    tiles="CartoDB positron"
)

# 기존 데이터 지도에 표시
for i in range(len(df_new)):
    try:
        cluster = int(df_new.iloc[i]['cluster'])
    except:
        continue
        
    folium.CircleMarker(
        location=[df_new.iloc[i]['위도'], df_new.iloc[i]['경도']],
        radius=3,
        color=colors.get(cluster, 'gray'),
        fill=True,
        fill_color=colors.get(cluster, 'gray'),
        fill_opacity=0.6
    ).add_to(m)

# 3. 버튼 클릭 시 위험도 계산 (★ 이 부분의 들여쓰기가 맨 앞에 붙어있어야 합니다 ★)
if st.button("위험도 분석"):
    # 입력한 위도/경도 기준 반경 5도 이내의 지진들만 필터링
    near_df = df_new[
        (df_new['위도'] >= lat - 5) & (df_new['위도'] <= lat + 5) &
        (df_new['경도'] >= lon - 5) & (df_new['경도'] <= lon + 5)
    ]

    # 질문하신 부분: 데이터가 없으면 안전한 지역으로 안내
    if len(near_df) == 0:
        with result_container:
            st.success("✅ 분석 결과: 주변에 지진 기록이 없는 안전한 지역입니다.")
        
        folium.Marker(
            location=[lat, lon],
            popup="안전 지대 (지진 기록 없음)",
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        
    else:
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)
        main_cluster = int(cluster_ratio.idxmax())

        with result_container:
            risk_level = risk_dict[main_cluster]
            if risk_level == '높음':
                st.error(f"🚨 예상 위험도: {risk_level} (주의가 필요합니다!)")
            elif risk_level == '중간':
                st.warning(f"⚠️ 예상 위험도: {risk_level} (일반적인 주의 요망)")
            else:
                st.success(f"🟢 예상 위험도: {risk_level} (비교적 안전한 지역입니다.)")

        folium.Marker(
            location=[lat, lon],
            popup=f"내가 설정한 위치 (위험도: {risk_dict[main_cluster]})",
            icon=folium.Icon(color='black', icon='star')
        ).add_to(m)

# 4. 지도 렌더링
st_folium(
    m, 
    width=1200, 
    height=650, 
    center=[0, 0],  
    zoom=2,         
    returned_objects=[]
)
