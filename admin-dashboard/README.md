# 🖥️ 관리자 대시보드

중고차 시세 예측 시스템 관리자용 웹 대시보드입니다.

## 📋 기능

- **Dashboard**: 통계 카드, 인기 모델 차트, 일별 분석 요청 차트
- **차량 데이터 관리**: 차량 목록 조회/검색/필터링, 상세 옵션 모달
- **사용자 관리**: 사용자 목록 조회/검색/수정/삭제
- **분석 이력**: 시세 분석 이력 조회
- **AI 로그**: (준비 중)
- **설정**: (준비 중)

## 🚀 실행 방법

```bash
cd admin-dashboard

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

브라우저에서 http://localhost:3000 접속

## 🛠️ 기술 스택

- **React 18** - UI 라이브러리
- **Vite** - 빌드 도구
- **CSS** - 스타일링 (커스텀 디자인 시스템)

## 📁 폴더 구조

```
admin-dashboard/
├── src/
│   ├── App.jsx        # 메인 컴포넌트
│   ├── App.css        # 스타일
│   └── main.jsx       # 엔트리 포인트
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 🔗 API 연동

현재 더미 데이터를 사용하며, 백엔드 API 연동 시 다음 엔드포인트 사용:

- ML Service: `http://localhost:8001`
- User Service: `http://localhost:8080`

