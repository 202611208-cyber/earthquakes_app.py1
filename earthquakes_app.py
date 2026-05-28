import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 레이아웃 확장 (지도를 가득 차게 보기 위함)
st.set_page_config(layout="wide")

st.title("세계 지진 위험도 분석 시스템")
st.write("위도와 경도를 입력하면 주변 지진 데이터를 기반으로 위험도를 분석합니다.")

# 1. 코랩에서 추출한 10,000개 요약 데이터 로드 (C:\eartquake\ 폴더 안에 이 파일이 있어야 합니다!)
try:
    df_new = pd.read_csv("deploy_earthquakes.csv")
except FileNotFoundError:
    st.error("🚨 'deploy_earthquakes.csv' 파일을 찾을 수 없습니다.")
    st.info("💡 코랩에서 다운로드한 'deploy_earthquakes.csv' 파일을 'C:\\eartquake\\' 폴더 안에 넣어주세요!")
    st.stop()

# 군집 설정 (코랩 분류 기준에 맞춤)
risk_dict = {0: '높음', 1: '낮음', 2: '중간'}
colors = {0: 'red', 1: 'blue', 2: 'green'}

# 2. 사용자 입력창 정의
lat = st.number_input("위도 입력", value=37.5)
lon = st.number_input("경도 입력", value=127.0)

# 결과 출력이 들어갈 상단 공간 확보
result_container = st.container()

# -------------------------------------------------------------------------
# [코랩 스타일 지도 고정] center와 zoom을 고정하여 자동 줌인 현상을 차단하고 전 세계 점 표출
# -------------------------------------------------------------------------
m = folium.Map(
    location=[0, 0], 
    zoom_start=2, 
    tiles="CartoDB positron"
)

# 이미 클러스터 결과가 포함된 10,000개의 점을 지도에 바로 뿌리기
for i in range(len(df_new)):
    # NaN 값이 있을 경우를 대비하여 처리하고 정수형으로 변환
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

# 3. 버튼 클릭 시 위험도 계산 결과를 보여주고 별 마커 추가
if st.button("위험도 분석"):
    # 입력한 위도/경도 기준 반경 5도 이내의 지진들만 필터링하여 비율 계산
    near_df = df_new[
        (df_new['위도'] >= lat - 5) & (df_new['위도'] <= lat + 5) &
        (df_new['경도'] >= lon - 5) & (df_new['경도'] <= lon + 5)
    ]

    if len(near_df) == 0:
        with result_container:
            st.warning("입력하신 위치 주변에 분석할 지진 기록이 부족합니다.")
    else:
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)
        main_cluster = int(cluster_ratio.idxmax())

        # 상단 영역에 결과 텍스트 출력
        with result_container:
            st.subheader(f"🌐 예상 위험도: {risk_dict[main_cluster]}")

        # 사용자가 입력한 위치에 검은색 별 마커(★) 추가
        folium.Marker(
            location=[lat, lon],
            popup=f"내가 설정한 위치 (위험도: {risk_dict[main_cluster]})",
            icon=folium.Icon(color='black', icon='star')
        ).add_to(m)

# 4. 지도 렌더링 (지도가 움직이거나 한반도로 멋대로 줌인되지 않도록 옵션 강제 고정)
st_folium(
    m, 
    width=1200, 
    height=650, 
    center=[0, 0],  
    zoom=2,         
    returned_objects=[]
)