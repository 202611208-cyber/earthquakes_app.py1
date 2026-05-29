# 3. 버튼 클릭 시 위험도 계산 결과를 보여주고 별 마커 추가
if st.button("위험도 분석"):
    # 입력한 위도/경도 기준 반경 5도 이내의 지진들만 필터링하여 비율 계산
    near_df = df_new[
        (df_new['위도'] >= lat - 5) & (df_new['위도'] <= lat + 5) &
        (df_new['경도'] >= lon - 5) & (df_new['경도'] <= lon + 5)
    ]

    # 주변에 데이터가 없는 경우 -> 안전 구역으로 판단
    if len(near_df) == 0:
        with result_container:
            st.success("✅ 분석 결과: 지진 데이터가 없는 매우 안전한 지역입니다.")
        
        # 지도에도 안전을 의미하는 초록색 마커 추가
        folium.Marker(
            location=[lat, lon],
            popup="안전 지대 (지진 기록 없음)",
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        
    else:
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)
        main_cluster = int(cluster_ratio.idxmax())

        # 상단 영역에 결과 텍스트 출력
        with result_container:
            # 위험도에 따라 다른 색상 메시지박스 출력 (선택 사항)
            risk_level = risk_dict[main_cluster]
            if risk_level == '높음':
                st.error(f"🚨 예상 위험도: {risk_level} (주의가 필요합니다!)")
            elif risk_level == '중간':
                st.warning(f"⚠️ 예상 위험도: {risk_level} (일반적인 주의 요망)")
            else:
                st.success(f"🟢 예상 위험도: {risk_level} (비교적 안전한 지역입니다.)")

        # 사용자가 입력한 위치에 검은색 별 마커(★) 추가
        folium.Marker(
            location=[lat, lon],
            popup=f"내가 설정한 위치 (위험도: {risk_dict[main_cluster]})",
            icon=folium.Icon(color='black', icon='star')
        ).add_to(m)
