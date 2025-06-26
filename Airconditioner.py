# Airconditioner_korean_summer.py
import streamlit as st
import requests
import geocoder
from datetime import datetime
import calendar

def get_location():
    """IP 기반으로 위도, 경도 반환 (실패 시 (None, None))."""
    try:
        g = geocoder.ip('me')
        if g.ok and g.latlng:
            return g.latlng
        return None, None
    except Exception as e:
        st.error(f"위치 조회 중 오류 발생: {str(e)}")
        return None, None

def get_weather(lat, lon):
    """
    Open-Meteo API를 사용해 외부 온도(°C)와 습도(%)를 반환.
    실패 시 (None, None).
    """
    try:
        # 현재 시간의 습도를 얻기 위해 hourly 데이터에서 현재 시간 찾기
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&hourly=relativehumidity_2m"
            f"&timezone=auto"
        )
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()  # HTTP 에러 체크
        
        data = resp.json()
        t_out = data["current_weather"]["temperature"]
        
        # 현재 시간에 해당하는 습도 찾기
        current_time = datetime.fromisoformat(data["current_weather"]["time"])
        hourly_times = data["hourly"]["time"]
        hourly_humidity = data["hourly"]["relativehumidity_2m"]
        
        # 현재 시간과 가장 가까운 시간의 습도 찾기
        current_hour = current_time.strftime("%Y-%m-%dT%H:00")
        if current_hour in hourly_times:
            idx = hourly_times.index(current_hour)
            h_out = hourly_humidity[idx]
        else:
            # 못 찾으면 첫 번째 값 사용
            h_out = hourly_humidity[0]
            
        return t_out, h_out
    except requests.exceptions.RequestException as e:
        st.error(f"날씨 API 오류: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"날씨 데이터 처리 오류: {str(e)}")
        return None, None

def calculate_discomfort_index(temp, humidity):
    """불쾌지수 계산"""
    return 0.81 * temp + 0.01 * humidity * (0.99 * temp - 14.3) + 46.3

def estimate_compressor_ratio(t_in, h_in, t_out, h_out, t_set, 
                            alpha=0.030, beta=0.0045, month=None):
    """
    한국 여름철 특성을 반영한 실외기 가동률 예측 (0.1 ~ 1.0)
    
    Parameters:
    - t_in: 실내온도
    - h_in: 실내습도
    - t_out: 외부온도
    - h_out: 외부습도
    - t_set: 설정온도
    - alpha: 온도 가중치 (기본값: 0.030)
    - beta: 습도 가중치 (기본값: 0.0045)
    - month: 월 (6, 7, 8, 9) - None이면 평균값 사용
    """
    # 월별 가중치 조정
    if month:
        monthly_weights = {
            6: (0.028, 0.0045),  # 6월: 초여름
            7: (0.032, 0.0055),  # 7월: 장마철, 습도 영향 최대
            8: (0.035, 0.0040),  # 8월: 폭염, 온도 영향 최대
            9: (0.025, 0.0030)   # 9월: 늦여름, 영향 감소
        }
        alpha, beta = monthly_weights.get(month, (alpha, beta))
    
    # 온도차와 습도차
    delta_t = t_in - t_set
    delta_h = h_in - h_out
    
    # 기본 가동률 (한국 여름 특성상 높게 설정)
    base_ratio = 0.45
    
    # 외부 온도 영향 (25도 이상에서 가중)
    outdoor_factor = 0.015 * max(0, t_out - 25)
    
    # 열대야 조건 (외부 온도 25도 이상일 때 추가 가중)
    night_factor = 0.05 if t_out >= 25 else 0
    
    # 불쾌지수 고려
    discomfort_index = calculate_discomfort_index(t_in, h_in)
    discomfort_factor = max(0, (discomfort_index - 75) * 0.01)
    
    # 최종 가동률 계산
    ratio = (base_ratio + 
             alpha * delta_t + 
             beta * delta_h + 
             outdoor_factor + 
             night_factor +
             discomfort_factor)
    
    return min(max(ratio, 0.1), 1.0)

def get_operation_mode_recommendation(h_in, t_in, t_set):
    """습도와 온도에 따른 운전 모드 추천"""
    if h_in >= 70:
        return "🌧️ 제습 모드 강력 권장", "st-warning"
    elif h_in >= 60:
        return "💧 제습 모드 권장", "st-info"
    elif h_in >= 50 and t_in - t_set > 3:
        return "❄️ 일반 냉방 모드", "st-info"
    elif h_in < 50 and t_in - t_set < 2:
        return "🌬️ 약냉방 또는 송풍 모드", "st-success"
    else:
        return "❄️ 일반 냉방 모드", "st-info"

def calculate_progressive_rate(total_kwh):
    """
    주택용 전기요금 누진제 계산 (2024년 기준)
    Returns: (총 요금, 평균 단가)
    """
    # 기본요금
    if total_kwh <= 200:
        base_charge = 1130
    elif total_kwh <= 400:
        base_charge = 2710
    else:
        base_charge = 7300
    
    # 전력량 요금 계산
    if total_kwh <= 200:
        usage_charge = total_kwh * 115.9
    elif total_kwh <= 400:
        usage_charge = 200 * 115.9 + (total_kwh - 200) * 206.6
    else:
        usage_charge = 200 * 115.9 + 200 * 206.6 + (total_kwh - 400) * 307.3
    
    total_charge = base_charge + usage_charge
    avg_rate = total_charge / total_kwh if total_kwh > 0 else 115.9
    
    return total_charge, avg_rate

def calculate_power_usage(
    t_in, h_in, t_out, h_out, t_set,
    usage_hour, rated_power, rate_per_kwh,
    cop=3.52, alpha=0.030, beta=0.0045, month=None,
    previous_usage=0
):
    """
    전력 사용량 계산 (한국 여름철 특성 반영)
    Returns: 일일 기준 전력 사용량 및 비용
    """
    ratio = estimate_compressor_ratio(t_in, h_in, t_out, h_out, t_set, alpha, beta, month)
    compressor_hours = usage_hour * ratio
    
    # COP를 고려한 실제 전력 소비
    # 외부 온도가 높을수록 효율이 떨어짐
    cop_adjusted = cop * (1 - 0.01 * max(0, t_out - 35))
    effective_power = rated_power * (cop / cop_adjusted)
    
    # 일일 전력 소비량
    power_kwh = compressor_hours * effective_power
    estimated_cost = power_kwh * rate_per_kwh
    
    # 월간 에어컨 사용량
    monthly_aircon_kwh = power_kwh * 30
    
    # 누진제 적용 계산
    # 전월 사용량만
    prev_total_charge, prev_avg_rate = calculate_progressive_rate(previous_usage)
    
    # 전월 + 에어컨 사용량
    new_total_kwh = previous_usage + monthly_aircon_kwh
    new_total_charge, new_avg_rate = calculate_progressive_rate(new_total_kwh)
    
    # 에어컨으로 인한 추가 요금
    additional_charge = new_total_charge - prev_total_charge
    daily_additional_charge = additional_charge / 30
    
    # 불쾌지수 계산 (에어컨 가동 전 상태)
    discomfort_index_before = calculate_discomfort_index(t_in, h_in)
    
    # 예상 불쾌지수 (에어컨 가동 후 - 간단한 추정)
    # 설정 온도와 습도 감소 효과 추정
    estimated_humidity_after = h_in - (h_in - 50) * ratio * 0.5  # 가동률에 따른 습도 감소
    discomfort_index_after = calculate_discomfort_index(t_set, estimated_humidity_after)
    
    return {
        "compressor_ratio": round(ratio * 100, 1),
        "compressor_hours": round(compressor_hours, 2),
        "power_kwh": round(power_kwh, 2),
        "estimated_cost": int(estimated_cost),
        "cop_adjusted": round(cop_adjusted, 2),
        "discomfort_index_before": round(discomfort_index_before, 1),
        "discomfort_index_after": round(discomfort_index_after, 1),
        "humidity_after": round(estimated_humidity_after, 1),
        "monthly_aircon_kwh": round(monthly_aircon_kwh, 2),
        "prev_total_charge": int(prev_total_charge),
        "new_total_charge": int(new_total_charge),
        "additional_charge": int(additional_charge),
        "daily_additional_charge": int(daily_additional_charge),
        "new_total_kwh": round(new_total_kwh, 2),
        "prev_avg_rate": round(prev_avg_rate, 1),
        "new_avg_rate": round(new_avg_rate, 1)
    }

def main():
    st.set_page_config(
        page_title="한국형 에어컨 가동률 예측기",
        page_icon="❄️",
        layout="wide"
    )
    
    st.title("❄️ 한국형 에어컨 실외기 가동률 예측기")
    st.markdown("한국 여름철 특성을 반영한 에어컨 가동률과 전기요금 예측 시스템")
    
    # 사이드바 설정
    st.sidebar.title("⚙️ 설정 패널")
    
    # 현재 월 자동 감지
    current_month = datetime.now().month
    if 6 <= current_month <= 9:
        default_month = current_month
    else:
        default_month = 7  # 여름이 아니면 7월 기본값
    
    # 월 선택
    month_names = {6: "6월 (초여름)", 7: "7월 (장마철)", 8: "8월 (폭염)", 9: "9월 (늦여름)"}
    selected_month = st.sidebar.selectbox(
        "📅 월 선택 (가중치 자동 조정)",
        options=[6, 7, 8, 9],
        format_func=lambda x: month_names[x],
        index=[6, 7, 8, 9].index(default_month) if default_month in [6, 7, 8, 9] else 1
    )
    
    # 1) 하루 사용 시간
    usage_hour = st.sidebar.slider(
        "⏰ 하루 에어컨 사용 시간 (시간)",
        min_value=1, max_value=24, value=8, step=1
    )
    
    # 2) 실내 환경 설정
    st.sidebar.subheader("🏠 실내 환경")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        t_in = st.number_input(
            "실내 온도 (°C)",
            min_value=16, max_value=35, value=28, step=1
        )
    with col2:
        h_in = st.number_input(
            "실내 습도 (%)",
            min_value=0, max_value=100, value=65, step=1
        )
    
    # 3) 설정 온도
    t_set = st.sidebar.slider(
        "🎯 에어컨 설정 온도 (°C)",
        min_value=16, max_value=30, value=24, step=1
    )
    
    # 4) 외부 환경
    st.sidebar.subheader("🌤️ 외부 환경")
    manual = st.sidebar.checkbox("외부 온·습도 수동 입력", value=False)
    
    if manual:
        col3, col4 = st.sidebar.columns(2)
        with col3:
            t_out = st.number_input(
                "외부 온도 (°C)",
                min_value=-30, max_value=50, value=32, step=1
            )
        with col4:
            h_out = st.number_input(
                "외부 습도 (%)",
                min_value=0, max_value=100, value=75, step=1
            )
    else:
        with st.sidebar:
            with st.spinner("위치 정보 조회 중..."):
                lat, lon = get_location()
        
        if lat is not None and lon is not None:
            with st.sidebar:
                with st.spinner("날씨 정보 조회 중..."):
                    t_out, h_out = get_weather(lat, lon)
            
            if t_out is None or h_out is None:
                st.sidebar.warning("⚠️ 외부 날씨 조회 실패 – 수동 입력 모드를 활성화하세요.")
                manual = True
        else:
            st.sidebar.warning("⚠️ 위치 조회 실패 – 수동 입력 모드를 활성화하세요.")
            manual = True
        
        # 자동 조회 실패 시 수동 입력
        if manual or t_out is None or h_out is None:
            col3, col4 = st.sidebar.columns(2)
            with col3:
                t_out = st.number_input(
                    "외부 온도 (°C)",
                    min_value=-30, max_value=50, value=32, step=1
                )
            with col4:
                h_out = st.number_input(
                    "외부 습도 (%)",
                    min_value=0, max_value=100, value=75, step=1
                )
        else:
            st.sidebar.success(f"📍 외부 온도: {t_out}°C  |  습도: {h_out}%")
    
    # 5) Advanced 옵션
    with st.sidebar.expander("🔧 Advanced 옵션", expanded=False):
        rated_power = st.number_input(
            "정격 소비전력 (kW)",
            min_value=0.1, max_value=5.0, value=0.907, step=0.001,
            format="%.3f",
            help="에어컨의 정격 소비전력"
        )
        rate_per_kwh = st.number_input(
            "전기 요금 단가 (원/kWh)",
            min_value=10.0, max_value=500.0, value=115.9, step=0.1,
            format="%.1f",
            help="전기 요금 단가"
        )
        cop = st.number_input(
            "에너지 소비효율 (COP)",
            min_value=1.0, max_value=10.0, value=3.52, step=0.01,
            format="%.2f",
            help="에너지 소비효율 (높을수록 효율적)"
        )
    
    # 전월 사용량 입력 (누진제 계산용)
    with st.sidebar.expander("📊 전월 전기 사용량", expanded=False):
        previous_usage = st.number_input(
            "전월 전체 전기 사용량 (kWh)",
            min_value=0, max_value=2000, value=300, step=10,
            help="전기요금 고지서의 전월 사용량을 입력하세요"
        )
        
        # 주택용 전기요금 누진제 정보 표시
        st.caption("""
        **주택용 전기요금 누진제 (2024년 기준)**
        - 1구간: ~200kWh (115.9원/kWh)
        - 2구간: 201~400kWh (206.6원/kWh)
        - 3구간: 401kWh~ (307.3원/kWh)
        """)
    
    # 온습도 가중치 (월별 자동 조정)
    with st.sidebar.expander("📊 온습도 가중치 (월별 자동 조정)", expanded=False):
        # 월별 기본값 설정
        monthly_defaults = {
            6: (0.028, 0.0045),
            7: (0.032, 0.0055),
            8: (0.035, 0.0040),
            9: (0.025, 0.0030)
        }
        default_alpha, default_beta = monthly_defaults.get(selected_month, (0.030, 0.0045))
        
        use_custom_weights = st.checkbox("수동 조정", value=False)
        
        if use_custom_weights:
            alpha = st.number_input(
                "온도 가중치 α",
                min_value=0.0,
                max_value=0.1,
                value=default_alpha,
                step=0.001,
                format="%.3f",
                help="온도 차이가 가동률에 미치는 영향"
            )
            beta = st.number_input(
                "습도 가중치 β",
                min_value=0.0,
                max_value=0.05,
                value=default_beta,
                step=0.0001,
                format="%.4f",
                help="습도 차이가 가동률에 미치는 영향"
            )
        else:
            alpha, beta = default_alpha, default_beta
            st.info(f"{month_names[selected_month]} 기본값: α={alpha:.3f}, β={beta:.4f}")
    
    # 계산 및 결과 표시
    results = calculate_power_usage(
        t_in, h_in, t_out, h_out, t_set,
        usage_hour, rated_power, rate_per_kwh,
        cop, alpha, beta, selected_month, previous_usage
    )
    
    # 메인 화면에 결과 표시
    col_main1, col_main2 = st.columns(2)
    
    with col_main1:
        st.subheader("📊 예측 결과")
        
        # 가동률에 따른 색상 설정
        ratio_color = "🟢" if results['compressor_ratio'] < 60 else "🟡" if results['compressor_ratio'] < 80 else "🔴"
        st.metric(f"{ratio_color} 실외기 가동률", f"{results['compressor_ratio']}%")
        
        st.metric("⏱️ 실외기 작동 시간", f"{results['compressor_hours']} 시간/일")
        st.metric("⚡ 일일 소비 전력", f"{results['power_kwh']} kWh/일")
        
        # 누진제 적용 전후 비교
        st.subheader("💰 전기요금 예측")
        
        col_cost1, col_cost2 = st.columns(2)
        with col_cost1:
            st.metric("단순 계산 요금", f"{results['estimated_cost']:,} 원/일",
                     help="단일 요율 적용 시")
            monthly_simple = results['estimated_cost'] * 30
            st.metric("", f"{monthly_simple:,} 원/월")
        
        with col_cost2:
            st.metric("누진제 적용 요금", f"{results['daily_additional_charge']:,} 원/일",
                     delta=f"+{results['daily_additional_charge'] - results['estimated_cost']:,}",
                     help="실제 추가되는 요금")
            st.metric("", f"{results['additional_charge']:,} 원/월")
        
        # 누진제 상세 정보
        with st.expander("📊 누진제 적용 상세", expanded=False):
            col_prog1, col_prog2 = st.columns(2)
            with col_prog1:
                st.write("**전월 사용량**")
                st.write(f"- 사용량: {previous_usage} kWh")
                st.write(f"- 요금: {results['prev_total_charge']:,} 원")
                st.write(f"- 평균단가: {results['prev_avg_rate']:.1f} 원/kWh")
            
            with col_prog2:
                st.write("**예상 사용량 (전월+에어컨)**")
                st.write(f"- 사용량: {results['new_total_kwh']:.0f} kWh")
                st.write(f"- 요금: {results['new_total_charge']:,} 원")
                st.write(f"- 평균단가: {results['new_avg_rate']:.1f} 원/kWh")
            
            # 누진구간 변화 경고
            if previous_usage <= 200 and results['new_total_kwh'] > 200:
                st.warning("⚠️ 1구간 → 2구간으로 상승 예상")
            elif previous_usage <= 400 and results['new_total_kwh'] > 400:
                st.error("🚨 2구간 → 3구간으로 상승 예상 (요금 급증!)")
        
        # 월간 예상 비용 표시
        st.metric("📅 월간 에어컨 사용량", f"{results['monthly_aircon_kwh']} kWh/월")
        st.metric("📈 보정된 COP", f"{results['cop_adjusted']}")
        
        # 불쾌지수 표시 (가동 전 → 가동 후)
        di_before = results['discomfort_index_before']
        di_after = results['discomfort_index_after']
        
        di_level_before = "쾌적" if di_before < 68 else "보통" if di_before < 75 else "불쾌" if di_before < 80 else "매우 불쾌"
        di_level_after = "쾌적" if di_after < 68 else "보통" if di_after < 75 else "불쾌" if di_after < 80 else "매우 불쾌"
        
        di_color_before = "🟢" if di_before < 68 else "🟡" if di_before < 75 else "🟠" if di_before < 80 else "🔴"
        di_color_after = "🟢" if di_after < 68 else "🟡" if di_after < 75 else "🟠" if di_after < 80 else "🔴"
        
        col_di1, col_di2 = st.columns(2)
        with col_di1:
            st.metric(f"{di_color_before} 현재 불쾌지수", f"{di_before:.1f} ({di_level_before})")
        with col_di2:
            st.metric(f"{di_color_after} 예상 불쾌지수", f"{di_after:.1f} ({di_level_after})", 
                     delta=f"{di_after - di_before:.1f}")
        
        st.caption(f"💧 예상 습도: {results['humidity_after']:.1f}%")
    
    with col_main2:
        st.subheader("📈 가동률 분석")
        
        # 가동률 게이지 차트
        st.progress(results['compressor_ratio'] / 100)
        
        # 운전 모드 추천
        mode_rec, mode_class = get_operation_mode_recommendation(h_in, t_in, t_set)
        st.markdown(f"""
        <div class="{mode_class}" style="padding: 10px; border-radius: 5px;">
        <b>권장 운전 모드:</b> {mode_rec}
        </div>
        """, unsafe_allow_html=True)
        
        # 조건 요약
        st.info(f"""
        **현재 조건:**
        - 🌡️ 온도차 (실내-설정): {t_in - t_set}°C
        - 💧 습도차 (실내-외부): {h_in - h_out}%
        - 🌤️ 외부 온도: {t_out}°C
        - 📅 적용 월: {month_names[selected_month]}
        """)
        
        # 전기요금 절약 정보 추가
        if results['additional_charge'] > 50000:
            st.error(f"""
            ⚠️ **주의**: 에어컨으로 인한 추가 요금이 5만원을 초과합니다!
            - 누진세 구간 상승으로 요금이 급증할 수 있습니다
            - 설정 온도를 26-28°C로 조정을 권장합니다
            - 현재 평균 단가: {results['new_avg_rate']:.1f}원/kWh
            """)
        
        if results['compressor_ratio'] > 70:
            st.warning("""
            💡 **절약 팁**: 가동률이 높습니다!
            - 설정 온도를 1-2도 높여보세요 (권장: 26-28°C)
            - 선풍기와 함께 사용하면 체감온도를 낮출 수 있습니다
            - 창문과 커튼을 닫아 열 유입을 차단하세요
            - 습도가 높다면 제습 모드를 활용하세요
            """)
        elif h_in > 70:
            st.warning("""
            💧 **습도 관리 팁**: 습도가 매우 높습니다!
            - 제습 모드를 사용하면 전력 효율이 2.7배 향상됩니다
            - 창문을 닫고 환기는 짧게 하세요
            - 실내 빨래는 피하세요
            """)
    
    # 하단에 계산 공식 설명
    with st.expander("📐 한국형 계산 공식 설명", expanded=False):
        st.markdown(f"""
        ### 🇰🇷 한국 여름철 특성을 반영한 가동률 계산:
        ```
        가동률 = 기본값(0.45) + α×ΔT + β×ΔH + 외부온도영향 + 열대야보정 + 불쾌지수보정
        ```
        
        ### 월별 가중치 (α, β):
        - **6월**: α=0.028, β=0.0045 (초여름)
        - **7월**: α=0.032, β=0.0055 (장마철, 습도 최대)
        - **8월**: α=0.035, β=0.0040 (폭염, 온도 최대)
        - **9월**: α=0.025, β=0.0030 (늦여름)
        
        ### 특수 보정:
        - **외부온도 영향**: 25°C 이상시 0.015×(외부온도-25)
        - **열대야 보정**: 외부온도 25°C 이상시 +5%
        - **불쾌지수**: DI = 0.81T + 0.01H(0.99T - 14.3) + 46.3
        
        ### 전력 소비:
        ```
        보정 COP = COP × (1 - 0.01 × max(0, 외부온도 - 35))
        유효 전력 = 정격전력 × (COP / 보정 COP)
        소비 전력 = 가동 시간 × 가동률 × 유효 전력
        ```
        
        💡 **참고**: 한국 여름철 평균기온이 역대 최고를 기록하며,
        열대야 일수가 평년 대비 3.1배 증가한 특성을 반영했습니다.
        """)

if __name__ == "__main__":
    main()