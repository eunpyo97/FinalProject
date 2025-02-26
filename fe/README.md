

## 주요 라이브러리
1. 상태관리 : zustand
2. API 요청 : Axios
3. 스타일링 : Styled Components  


## 설치 및 실행 방법
1. 설치
```
cd fe
npm install
```
2. .env 기재내용
```
REACT_APP_API_BASE_URL=http://localhost:5000
```
3. 실행
```
npm start
```  


## 폴더 구조
```
📂 fe/ 
├── 📂 public/  # 정적 파일
│   └── assets/ # 이미지 등 정적 리소스
│   └── 📄 index.html  # 메인 HTML 파일
├── 📂 src/  # 소스 코드
│   ├── 📂 api/  # API 요청  
│   │   ├── 📄 auth.js    # 로그인/회원가입 관련 API  
│   │   ├── 📄 chat.js     
│   │   ├── 📄 calendar.js    
│   │   ├── 📄 emotion.js      
│   │   └── 📄 config.js  # Axios 기본 설정  
│   ├── 📂 components/    # 재사용 가능한 UI 컴포넌트
│   │   ├── 📄 Button.js  # 재사용 가능한 버튼
│   │   ├── 📄 ErrorMessage.js  # 에러 메시지 표시
│   │   ├── 📄 Navbar.js  # 네비게이션 바 
│   │   └── 📄 Spinner.js  # 로딩 스피너 
│   ├── 📂 pages/         # 개별 페이지
│   │   ├── 📄 Calendar.js    
│   │   ├── 📄 Chat.js 
│   │   ├── 📄 ChatList.js 
│   │   ├── 📄 ChatRoomDetail.js 
│   │   ├── 📄 DiaryDetail.js 
│   │   ├── 📄 DiaryList.js 
│   │   ├── 📄 ForgotPassword.js  # 비밀번호 찾기  
│   │   ├── 📄 Home.js     # 로그인 후 홈 화면 (메뉴 포함)
│   │   ├── 📄 Landing.js  # 랜딩 페이지 (로그인/회원가입 버튼)
│   │   ├── 📄 Login.js    # 로그인 페이지
│   │   ├── 📄 Signup.js   # 회원가입 페이지
│   │   └── 📄 ResetPassword.js  # 비밀번호 재설정  
│   ├── 📂 routes/         # React Router 설정
│   │   ├── 📄 PrivateRoute.js  # 로그인 필요 페이지 보호
│   │   └── 📄 routes.js   # 전체 경로 정의
│   ├── 📂 store/          # Zustand 상태 관리  
│   │   ├── 📄 authStore.js  # 로그인 상태 관리 
│   │   └── 📄 emotionStore.js 
│   ├── 📂 styles/         # Styled Components 스타일 관리
│   │   └── 📄 GlobalStyle.js  # 전역 스타일
│   ├── 📂 utils/      
│   │   ├── 📄 webcamUtils.js # 웹캠   
│   │   └── 📄 validation.js  # 유효성 검사
│   ├── 📄 App.js           # 전체 앱 구조
│   └── 📄 index.js          # React 진입점
├── 📄 package.json         # 패키지 정보
├── 📄 package-lock.json
├── 📄 .gitignore  
├── 📄 README.md 
└── 📄 .env  

```