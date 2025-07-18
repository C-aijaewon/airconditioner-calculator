# 🏠 한국형 에어컨 가동률 예측기

여름철 에어컨 사용에 따른 전기요금을 미리 계산해보는 프로그램입니다.

## ✨ 주요 기능

- **실시간 날씨 연동** - 현재 위치의 온도/습도 자동 반영
- **누진제 계산** - 2024년 최신 전기요금 누진제 적용
- **월별 최적화** - 6~9월 한국 기후 특성 반영
- **스마트 추천** - 습도별 최적 운전 모드 제안

## 🚀 바로 사용하기

### 방법 1: 웹에서 실행 (인터넷만 있으면 OK)
> 🔗 [여기를 클릭하세요](https://airconditioner-calculator-qennspe3zar4kwwh2j44hf.streamlit.app/) 

### 방법 2: 내 컴퓨터에서 실행
```bash
# 1. 다운로드
git clone https://github.com/C-aijaewon/airconditioner-calculator.git

# 2. 폴더 이동
cd airconditioner-calculator

# 3. 실행
run_app.bat
```

## 🔧 사용법

1. **기본 정보 입력**
   - 하루 사용 시간 (슬라이더)
   - 실내 온도/습도
   - 에어컨 설정 온도

2. **전기요금 계산**
   - 전월 사용량 입력
   - 자동으로 누진구간 계산

3. **결과 확인**
   - 예상 가동률
   - 일일/월간 전기요금
   - 절약 팁

## 💡 특별한 점

- 📊 **정확한 계산**: 한국 기상청 데이터 기반
- 💰 **누진제 반영**: 구간별 요금 자동 계산  
- 🌡️ **불쾌지수**: 체감 온도까지 고려
- 📱 **모바일 지원**: 스마트폰에서도 사용 가능

## 📋 필요한 것

- Python 3.8 이상
- 인터넷 연결

## 🤝 문의 & 제안

개선 아이디어나 버그를 발견하셨나요?
- 📧 이메일: onelloved1@gmail.com
- 💬 이슈: [GitHub Issues](https://github.com/C-aijaewon/airconditioner-calculator/issues)

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자유롭게 사용하세요!

---