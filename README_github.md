# 한국형 에어컨 가동률 예측기 ❄️

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/YOUR_USERNAME/airconditioner-calculator/main/Airconditioner.py)

한국 여름철 특성을 반영한 스마트한 에어컨 전기요금 계산기입니다.

## 🌟 주요 기능

### 🌡️ 실시간 날씨 연동
- 현재 위치 자동 감지
- 실시간 온도/습도 정보 활용
- Open-Meteo API 연동

### 💰 누진제 반영 요금 계산
- 2024년 최신 전기요금 누진제 적용
- 전월 사용량 기반 정확한 예측
- 구간 변경 시 경고 알림

### 📊 한국 여름 특성 반영
- 월별 가중치 자동 조정 (6~9월)
- 열대야 조건 특별 보정
- 불쾌지수 기반 추천

### 💡 스마트 운전 모드 추천
- 습도별 최적 모드 제안
- 절전 팁 제공
- 실시간 가동률 분석

## 🖥️ 스크린샷

![메인 화면](screenshots/main.png)
*메인 화면 - 가동률과 요금 예측*

## 🚀 사용 방법

### 온라인으로 바로 사용하기 (권장)
👉 [여기를 클릭하세요](https://share.streamlit.io/C-aijaewon/airconditioner-calculator)

### 로컬에서 실행하기

1. **저장소 클론**
   ```bash
   git clone https://github.com/C-aijaewon/airconditioner-calculator.git
   cd airconditioner-calculator
   ```

2. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **실행**
   ```bash
   streamlit run Airconditioner.py
   ```

## 📋 시스템 요구사항

- Python 3.8 이상
- 인터넷 연결 (날씨 API용)
- 모던 웹 브라우저

## 🔧 설정 방법

1. **기본 정보 입력**
   - 하루 사용 시간
   - 실내 온도/습도
   - 설정 온도

2. **전기요금 계산**
   - 전월 사용량 입력
   - 누진제 자동 적용

3. **고급 설정** (선택사항)
   - 정격 소비전력
   - COP 값
   - 가중치 조정

## 📈 계산 원리

```
가동률 = 기본값(0.45) + α×ΔT + β×ΔH + 외부온도영향 + 열대야보정 + 불쾌지수보정
```

- **α (온도 가중치)**: 월별 자동 조정
- **β (습도 가중치)**: 장마철 특별 보정
- **특수 보정**: 한국 기후 특성 반영

## 🤝 기여하기

개선 아이디어나 버그 리포트는 [Issues](https://github.com/YOUR_USERNAME/airconditioner-calculator/issues)에 남겨주세요!

## 📄 라이선스

MIT License

## 👨‍💻 개발자

- 개발자: [C-aijaewon]
- 이메일: onelloved1@gmail.com

---

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!