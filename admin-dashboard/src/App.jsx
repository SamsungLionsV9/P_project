import { useState } from "react";
import "./App.css";

const popularModels = [
  { name: "아반떼", value: 480 },
  { name: "K5", value: 500 },
  { name: "그랜저", value: 420 },
  { name: "투싼", value: 380 },
  { name: "차1", value: 360 },
  { name: "차2", value: 340 },
  { name: "차3", value: 200 },
];

const dailyRequests = [120, 320, 280, 600, 450, 300, 700];
const dailyLabels = ["월", "화", "수", "목", "금", "토", "일"];

const getLinePoints = (values) => {
  const max = Math.max(...values);
  const width = 100;
  const height = 100;

  return values
    .map((v, i) => {
      const x = (i / (values.length - 1)) * width;
      const y = height - (v / max) * height;
      return `${x},${y}`;
    })
    .join(" ");
};

// 차량 데이터 관리용 더미 데이터
const vehicleRows = [
  {
    brand: "현대",
    model: "#12548796",
    year: 2023,
    distance: "0.5만KM",
    fuel: "가솔린",
    price: "1,500만원",
    body: "SUV",
    score: "3.5점",
    details: {
      accidentFree: true,          // 무사고 여부
      options: {
        sunroof: true,
        familySeat: true,
        rearCamera: true,
        navigation: false,
        smartKey: true,
      },
      region: "서울/경기",
    },
  },
  {
    brand: "기아",
    model: "#12548796",
    year: 2024,
    distance: "0.8만KM",
    fuel: "경유",
    price: "1,500만원",
    body: "SUV",
    score: "3.5점",
    details: {
      accidentFree: true,          // 무사고 여부
      options: {
        sunroof: true,
        familySeat: true,
        rearCamera: true,
        navigation: true,
        smartKey: true,
      },
      region: "강원",
    },
  },
  {
    brand: "제네시스",
    model: "#12548796",
    year: 2025,
    distance: "1만KM",
    fuel: "경유",
    price: "1,500만원",
    body: "SUV",
    score: "3.5점",
    details: {
      accidentFree: true,          // 무사고 여부
      options: {
        sunroof: true,
        familySeat: true,
        rearCamera: true,
        navigation: false,
        smartKey: true,
      },
      region: "경상",
    },
  },
  {
    brand: "쉐보레",
    model: "#12548796",
    year: 2023,
    distance: "0.3만KM",
    fuel: "경유",
    price: "1,500만원",
    body: "SUV",
    score: "3.5점",
    details: {
      accidentFree: true,          // 무사고 여부
      options: {
        sunroof: true,
        familySeat: true,
        rearCamera: true,
        navigation: false,
        smartKey: true,
      },
      region: "서울/경기",
    },
  },
  {
    brand: "기아",
    model: "#12548796",
    year: 2015,
    distance: "0.7만KM",
    fuel: "경유",
    price: "1,500만원",
    body: "SUV",
    score: "3.5점",
    details: {
      accidentFree: true,          // 무사고 여부
      options: {
        sunroof: true,
        familySeat: true,
        rearCamera: true,
        navigation: false,
        smartKey: true,
      },
      region: "충청",
    },
  },
];

// 사용자 관리용 더미 데이터
const userRows = [
  {
    no: "01.",
    id: "user1234",
    nickname: "김철수",
    phone: "010-0000-0000",
    role: "관리자",
    history: "5회",
  },
  {
    no: "02.",
    id: "user1234",
    nickname: "차파는사람",
    phone: "010-0000-0000",
    role: "판매자",
    history: "8회",
  },
  {
    no: "03.",
    id: "user1234",
    nickname: "김영희",
    phone: "010-0000-0000",
    role: "일반 사용자",
    history: "0회",
  },
  {
    no: "04.",
    id: "user1234",
    nickname: "김영호",
    phone: "010-0000-0000",
    role: "일반 사용자",
    history: "3회",
  },
  {
    no: "05.",
    id: "user1234",
    nickname: "김영희",
    phone: "010-0000-0000",
    role: "일반 사용자",
    history: "1회",
  },
  {
    no: "06.",
    id: "user1234",
    nickname: "김영희",
    phone: "010-0000-0000",
    role: "일반 사용자",
    history: "0회",
  },
  {
    no: "07.",
    id: "user1234",
    nickname: "김영희",
    phone: "010-0000-0000",
    role: "일반 사용자",
    history: "0회",
  },
  {
    no: "08.",
    id: "user1234",
    nickname: "김영희",
    phone: "010-0000-0000",
    role: "일반 사용자",
    history: "0회",
  },
];

// 분석 이력용 더미 데이터
const historyRows = Array.from({ length: 9 }).map((_, i) => ({
  time: "2025-11-25 16:19",
  userId: "user1234",
  model: i % 3 === 0 ? "그랜저" : i % 3 === 1 ? "소나타" : "아반떼",
  year: 2023,
  distance: "0.5만KM",
  estimate: i % 3 === 0 ? "2,000만원" : i % 3 === 1 ? "8,000만원" : "5,000만원",
  confidence: "89%",
}));

const pageTitleMap = {
  dashboard: "DashBoard",
  vehicles: "차량 데이터 관리",
  users: "사용자 관리",
  history: "분석 이력",
  aiLog: "AI 로그",
  settings: "설정",
};

function App() {
  const [activeMenu, setActiveMenu] = useState("dashboard");
  const maxModelValue = Math.max(...popularModels.map((m) => m.value));

  return (
    <div className="app-root">
      {/* 사이드바 */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-box" />
          <span className="service-name">서비스 이름</span>
        </div>

        <nav className="sidebar-nav">
          <div
            className={`nav-item ${activeMenu === "dashboard" ? "active" : ""
              }`}
            onClick={() => setActiveMenu("dashboard")}
          >
            <span className="nav-icon">🏠</span>
            <span>Dashboard</span>
          </div>
          <div
            className={`nav-item ${activeMenu === "vehicles" ? "active" : ""}`}
            onClick={() => setActiveMenu("vehicles")}
          >
            <span className="nav-icon">🚗</span>
            <span>차량 데이터 관리</span>
          </div>
          <div
            className={`nav-item ${activeMenu === "users" ? "active" : ""}`}
            onClick={() => setActiveMenu("users")}
          >
            <span className="nav-icon">👤</span>
            <span>사용자 관리</span>
          </div>
          <div
            className={`nav-item ${activeMenu === "history" ? "active" : ""}`}
            onClick={() => setActiveMenu("history")}
          >
            <span className="nav-icon">📊</span>
            <span>분석 이력</span>
          </div>
          <div
            className={`nav-item ${activeMenu === "aiLog" ? "active" : ""}`}
            onClick={() => setActiveMenu("aiLog")}
          >
            <span className="nav-icon">🧠</span>
            <span>AI 로그</span>
          </div>
          <div
            className={`nav-item ${activeMenu === "settings" ? "active" : ""
              }`}
            onClick={() => setActiveMenu("settings")}
          >
            <span className="nav-icon">⚙️</span>
            <span>설정</span>
          </div>
        </nav>
      </aside>

      {/* 메인 영역 */}
      <main className="main">
        {/* 상단 바 */}
        <header className="topbar">
          <h1 className="page-title">{pageTitleMap[activeMenu]}</h1>
          <div className="topbar-right">
            <button className="top-icon-btn">⚙️</button>
            <button className="top-icon-btn">🔔</button>
            <button className="top-avatar">👤</button>
          </div>
        </header>

        {/* 메인 컨텐츠 */}
        {activeMenu === "dashboard" && (
          <DashboardContent
            maxModelValue={maxModelValue}
            popularModels={popularModels}
            dailyRequests={dailyRequests}
            dailyLabels={dailyLabels}
          />
        )}

        {activeMenu === "vehicles" && <VehiclePage />}

        {activeMenu === "users" && <UserPage />}

        {activeMenu === "history" && <HistoryPage />}

        {activeMenu === "aiLog" && (
          <PlaceholderPage title="AI 로그 페이지 준비 중입니다." />
        )}

        {activeMenu === "settings" && (
          <PlaceholderPage title="설정 페이지 준비 중입니다." />
        )}
      </main>
    </div>
  );
}

/* ---- Dashboard ---- */

function DashboardContent({
  maxModelValue,
  popularModels,
  dailyRequests,
  dailyLabels,
}) {
  return (
    <>
      {/* 카드 3개 */}
      <section className="stat-cards">
        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-green">👁️</div>
            <span className="stat-label">오늘 시세 조회</span>
          </div>
          <div className="stat-value">132건</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-yellow">📁</div>
            <span className="stat-label">전체 누적 조회</span>
          </div>
          <div className="stat-value">1,024건</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <div className="stat-icon stat-icon-blue">✔️</div>
            <span className="stat-label">평균 신뢰도</span>
          </div>
          <div className="stat-value">87%</div>
        </div>
      </section>

      {/* 차트 1: 인기 많은 모델 조회수 */}
      <section className="chart-section">
        <h2 className="chart-title">인기 많은 모델 조회수</h2>
        <div className="chart-card">
          <div className="bar-chart">
            {popularModels.map((m) => (
              <div key={m.name} className="bar-item">
                <div
                  className="bar"
                  style={{
                    height: `${(m.value / maxModelValue) * 100}%`,
                  }}
                />
                <span className="bar-label">{m.name}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 차트 2: 일별 시세 분석 요청 수 */}
      <section className="chart-section">
        <h2 className="chart-title">일별 시세 분석 요청 수</h2>
        <div className="chart-card">
          <div className="line-chart-wrapper">
            <svg
              className="line-chart"
              viewBox="0 0 100 100"
              preserveAspectRatio="none"
            >
              <defs>
                <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#2f57ff" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#2f57ff" stopOpacity="0" />
                </linearGradient>
              </defs>

              <polygon
                fill="url(#areaGradient)"
                points={`0,100 ${getLinePoints(dailyRequests)} 100,100`}
              />

              <polyline
                fill="none"
                stroke="#2f57ff"
                strokeWidth="1.5"
                points={getLinePoints(dailyRequests)}
              />

              {dailyRequests.map((v, i) => {
                const max = Math.max(...dailyRequests);
                const x = (i / (dailyRequests.length - 1)) * 100;
                const y = 100 - (v / max) * 100;
                return <circle key={i} cx={x} cy={y} r="1.3" fill="#2f57ff" />;
              })}
            </svg>

            <div className="line-x-labels">
              {dailyLabels.map((l) => (
                <span key={l}>{l}</span>
              ))}
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

/* ---- 차량 데이터 관리 ---- */

function VehiclePage() {
  const [modelFilter, setModelFilter] = useState("");
  const [brandFilter, setBrandFilter] = useState("all");
  const [displayedVehicles, setDisplayedVehicles] = useState(vehicleRows);
  const brandOptions = Array.from(new Set(vehicleRows.map((v) => v.brand)));
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const closeDetail = () => setSelectedVehicle(null);

  const handleSearch = () => {
    const filtered = vehicleRows.filter((row) => {
      const matchModel =
        modelFilter.trim() === "" ||
        row.model.toLowerCase().includes(modelFilter.toLowerCase());
      const matchBrand =
        brandFilter === "all" || row.brand === brandFilter;
      return matchModel && matchBrand;
    });
    setDisplayedVehicles(filtered);
  };

  const handleReset = () => {
    setModelFilter("");
    setBrandFilter("all");
    setDisplayedVehicles(vehicleRows);
  };

  return (
    <div className="page">
      <section className="content-header">
        <h2>차량 데이터 관리</h2>
      </section>

      <section className="filter-section">
        <div className="filter-card">
          <div className="filter-grid">
            <div className="filter-field">
              <label>모델명</label>
              <input
                placeholder="Placeholder"
                value={modelFilter}
                onChange={(e) => setModelFilter(e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>브랜드</label>
              <select
                value={brandFilter}
                onChange={(e) => setBrandFilter(e.target.value)}
              >
                <option value="all">전체</option>
                {brandOptions.map((brand) => (
                  <option key={brand} value={brand}>
                    {brand}
                  </option>
                ))}
              </select>

            </div>
          </div>

          <div className="filter-actions">
            <button className="btn-primary" onClick={handleSearch}>
              검색
            </button>
            <button className="btn-ghost" onClick={handleReset}>
              초기화
            </button>
          </div>
        </div>
        <div className="filter-underline" />
      </section>

      <section className="table-section">
        <div className="table-header-row">
          <div className="table-header-left">차량 데이터 관리</div>
          <div className="table-header-right">
            <button
              className="btn-link"
              onClick={() => alert("수정 기능은 아직 백엔드와 연동 필요")}
            >
              수정
            </button>
            <button
              className="btn-link danger"
              onClick={() => alert("삭제 기능은 아직 백엔드와 연동 필요")}
            >
              삭제
            </button>
            <span className="table-header-divider">|</span>
            <button
              className="btn-link strong"
              onClick={() => alert("새 모델 추가 기능은 추후 구현 예정")}
            >
              + 새 모델 추가
            </button>
          </div>
        </div>

        <div className="table-card">
          <table className="data-table">
            <thead>
              <tr>
                <th>브랜드</th>
                <th>모델명</th>
                <th>연식</th>
                <th>주행거리</th>
                <th>연료</th>
                <th>가격</th>
                <th>차체</th>
                <th>성능 점검</th>
                <th>기타 옵션</th>
              </tr>
            </thead>
            <tbody>
              {displayedVehicles.map((row, i) => (
                <tr key={i}>
                  <td>{row.brand}</td>
                  <td>{row.model}</td>
                  <td>{row.year}</td>
                  <td>{row.distance}</td>
                  <td>{row.fuel}</td>
                  <td className="strong-text">{row.price}</td>
                  <td>{row.body}</td>
                  <td>{row.score}</td>
                  <td>
                    <button
                      className="btn-outline"
                      onClick={() => setSelectedVehicle(row)}
                    >
                      상세 보기
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <Pagination />
        </div>
      </section>

      {/* ⬇⬇ 여기부터 모달 */}
      {selectedVehicle && (
        <div className="modal-backdrop" onClick={closeDetail}>
          <div
            className="modal-card"
            onClick={(e) => e.stopPropagation()} // 안쪽 클릭해도 닫히지 않게
          >
            <div className="modal-header">
              <h3>상세 옵션 (선택)</h3>
              <button className="modal-close" onClick={closeDetail}>
                ✕
              </button>
            </div>


            <div className="detail-section">
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={!!selectedVehicle.details?.accidentFree}
                  readOnly
                />
                <span>무사고 여부</span>
              </label>
            </div>

            <div className="detail-section">
              <div className="detail-label">옵션</div>
              <div className="detail-options-grid">
                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={!!selectedVehicle.details?.options.sunroof}
                    readOnly
                  />
                  <span>선루프</span>
                </label>
                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={!!selectedVehicle.details?.options.navigation}
                    readOnly
                  />
                  <span>내비게이션</span>
                </label>
                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={!!selectedVehicle.details?.options.familySeat}
                    readOnly
                  />
                  <span>가죽시트</span>
                </label>
                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={!!selectedVehicle.details?.options.smartKey}
                    readOnly
                  />
                  <span>스마트키</span>
                </label>
                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={!!selectedVehicle.details?.options.rearCamera}
                    readOnly
                  />
                  <span>후방카메라</span>
                </label>
              </div>
            </div>

            <div className="detail-section">
              <div className="detail-label">지역</div>
              <div className="detail-region-pill">
                {selectedVehicle.details?.region || "-"}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}



/* ---- 사용자 관리 ---- */

function UserPage() {
  const [filters, setFilters] = useState({
    userId: "",
    nickname: "",
    phone: "",
    role: "all",
  });

  const [users, setUsers] = useState(userRows);
  const [displayedUsers, setDisplayedUsers] = useState(userRows);

  const handleChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleSearch = () => {
    const filtered = users.filter((row) => {
      const matchId =
        filters.userId.trim() === "" ||
        row.id.toLowerCase().includes(filters.userId.toLowerCase());
      const matchNick =
        filters.nickname.trim() === "" ||
        row.nickname.toLowerCase().includes(filters.nickname.toLowerCase());
      const matchPhone =
        filters.phone.trim() === "" ||
        row.phone.includes(filters.phone.trim());
      const matchRole =
        filters.role === "all" ||
        (filters.role === "admin" && row.role === "관리자") ||
        (filters.role === "seller" && row.role === "판매자") ||
        (filters.role === "user" && row.role === "일반 사용자");

      return matchId && matchNick && matchPhone && matchRole;
    });
    setDisplayedUsers(filtered);
  };

  const handleReset = () => {
    const resetFilters = {
      userId: "",
      nickname: "",
      phone: "",
      role: "all",
    };
    setFilters(resetFilters);
    setDisplayedUsers(users);
  };

  const handleEdit = (row) => {
    alert(`${row.id} (${row.nickname}) 수정 기능은 추후 구현 예정`);
  };

  const handleDelete = (row) => {
    if (!window.confirm(`${row.id} (${row.nickname}) 를 삭제하시겠습니까?`))
      return;

    const updated = users.filter((u) => u.no !== row.no);
    setUsers(updated);
    // 삭제 후 현재 필터 기준으로 다시 검색
    setDisplayedUsers(updated);
  };

  return (
    <div className="page">
      <section className="content-header">
        <h2>사용자 관리</h2>
      </section>

      <section className="filter-section">
        <div className="filter-card">
          <div className="filter-grid three">
            <div className="filter-field">
              <label>유저 아이디</label>
              <input
                placeholder="Placeholder"
                value={filters.userId}
                onChange={(e) => handleChange("userId", e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>닉네임</label>
              <input
                placeholder="Placeholder"
                value={filters.nickname}
                onChange={(e) => handleChange("nickname", e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>전화번호</label>
              <input
                placeholder="Placeholder"
                value={filters.phone}
                onChange={(e) => handleChange("phone", e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>권한</label>
              <select
                value={filters.role}
                onChange={(e) => handleChange("role", e.target.value)}
              >
                <option value="all">전체</option>
                <option value="admin">관리자</option>
                <option value="seller">판매자</option>
                <option value="user">일반 사용자</option>
              </select>
            </div>
          </div>
          <div className="filter-actions">
            <button className="btn-primary" onClick={handleSearch}>
              검색
            </button>
            <button className="btn-ghost" onClick={handleReset}>
              초기화
            </button>
          </div>
        </div>
        <div className="filter-underline" />
      </section>

      <section className="table-section">
        <div className="table-header-row">
          <div className="table-header-left">사용자 관리</div>
        </div>

        <div className="table-card">
          <table className="data-table">
            <thead>
              <tr>
                <th>No</th>
                <th>유저 아이디</th>
                <th>닉네임</th>
                <th>전화번호</th>
                <th>권한</th>
                <th>거래 이력</th>
                <th>관리</th>
              </tr>
            </thead>
            <tbody>
              {displayedUsers.map((row) => (
                <tr key={row.no}>
                  <td>{row.no}</td>
                  <td>{row.id}</td>
                  <td>{row.nickname}</td>
                  <td>{row.phone}</td>
                  <td>{row.role}</td>
                  <td>{row.history}</td>
                  <td className="user-actions-cell">
                    <button
                      className="btn-chip blue"
                      onClick={() => handleEdit(row)}
                    >
                      수정
                    </button>
                    <button
                      className="btn-chip red"
                      onClick={() => handleDelete(row)}
                    >
                      삭제
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <Pagination />
        </div>
      </section>
    </div>
  );
}


/* ---- 분석 이력 ---- */

function HistoryPage() {
  const [userIdFilter, setUserIdFilter] = useState("");
  const [modelFilter, setModelFilter] = useState("all");
  const [dateFilter, setDateFilter] = useState("");
  const [displayedHistory, setDisplayedHistory] = useState(historyRows);

  const handleSearch = () => {
    const filtered = historyRows.filter((row) => {
      const matchUser =
        userIdFilter.trim() === "" ||
        row.userId.toLowerCase().includes(userIdFilter.toLowerCase());
      const matchModel =
        modelFilter === "all" ||
        (modelFilter === "grandeur" && row.model === "그랜저") ||
        (modelFilter === "sonata" && row.model === "소나타") ||
        (modelFilter === "avante" && row.model === "아반떼");
      const matchDate =
        dateFilter.trim() === "" || row.time.includes(dateFilter.trim());

      return matchUser && matchModel && matchDate;
    });
    setDisplayedHistory(filtered);
  };

  const handleReset = () => {
    setUserIdFilter("");
    setModelFilter("all");
    setDateFilter("");
    setDisplayedHistory(historyRows);
  };

  return (
    <div className="page">
      <section className="content-header">
        <h2>분석 이력</h2>
      </section>

      <section className="filter-section">
        <div className="filter-card">
          <div className="filter-grid three">
            <div className="filter-field">
              <label>유저 아이디</label>
              <input
                placeholder="Placeholder"
                value={userIdFilter}
                onChange={(e) => setUserIdFilter(e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>모델</label>
              <select
                value={modelFilter}
                onChange={(e) => setModelFilter(e.target.value)}
              >
                <option value="all">전체</option>
                <option value="grandeur">그랜저</option>
                <option value="sonata">소나타</option>
                <option value="avante">아반떼</option>
              </select>
            </div>
            <div className="filter-field">
              <label>조회 일시</label>
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
              />
            </div>
          </div>

          <div className="filter-actions">
            <button className="btn-primary" onClick={handleSearch}>
              검색
            </button>
            <button className="btn-ghost" onClick={handleReset}>
              초기화
            </button>
          </div>
        </div>
        <div className="filter-underline" />
      </section>

      <section className="table-section">
        <div className="table-header-row">
          <div className="table-header-left">분석 이력</div>
        </div>

        <div className="table-card">
          <table className="data-table">
            <thead>
              <tr>
                <th>조회 일시</th>
                <th>유저 아이디</th>
                <th>모델</th>
                <th>연식</th>
                <th>주행거리</th>
                <th>예상가</th>
                <th>신뢰도</th>
              </tr>
            </thead>
            <tbody>
              {displayedHistory.map((row, i) => (
                <tr key={i}>
                  <td>{row.time}</td>
                  <td>{row.userId}</td>
                  <td>{row.model}</td>
                  <td>{row.year}</td>
                  <td>{row.distance}</td>
                  <td>{row.estimate}</td>
                  <td>
                    <span className="badge-success">{row.confidence}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <Pagination />
        </div>
      </section>
    </div>
  );
}


/* ---- 공통 요소 ---- */

function Pagination() {
  return (
    <div className="pagination">
      <button className="page-link">&lt; Previous</button>
      <div className="page-numbers">
        <button className="page-number active">1</button>
        <button className="page-number">2</button>
        <button className="page-number">3</button>
        <button className="page-number">4</button>
      </div>
      <button className="page-link">Next &gt;</button>
    </div>
  );
}

function PlaceholderPage({ title }) {
  return (
    <div className="page placeholder-page">
      <p>{title}</p>
    </div>
  );
}

export default App;
