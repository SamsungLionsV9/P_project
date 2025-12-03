import { useState } from "react";
import "./App.css";

// 컴포넌트 임포트
import { Sidebar, PlaceholderPage } from "./components";
import { DashboardPage, VehiclePage, UserPage, HistoryPage } from "./pages";

const pageTitleMap = {
  dashboard: "DashBoard",
  vehicles: "차량 데이터 관리",
  users: "사용자 관리",
  history: "분석 이력",
  aiLog: "AI 로그",
  settings: "설정",
};

function App({ user, onLogout }) {
  const [activeMenu, setActiveMenu] = useState("dashboard");

  const handleLogout = () => {
    if (window.confirm("로그아웃 하시겠습니까?")) {
      onLogout();
    }
  };

  // 메뉴별 페이지 렌더링
  const renderPage = () => {
    switch (activeMenu) {
      case "dashboard":
        return <DashboardPage />;
      case "vehicles":
        return <VehiclePage />;
      case "users":
        return <UserPage />;
      case "history":
        return <HistoryPage />;
      case "aiLog":
        return <PlaceholderPage title="AI 로그 페이지 준비 중입니다." />;
      case "settings":
        return <PlaceholderPage title="설정 페이지 준비 중입니다." />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="app-root">
      {/* 사이드바 */}
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />

      {/* 메인 영역 */}
      <main className="main">
        {/* 상단 바 */}
        <header className="topbar">
          <h1 className="page-title">{pageTitleMap[activeMenu]}</h1>
          <div className="topbar-right">
            <span className="admin-name">{user?.username || "관리자"}</span>
            <button className="top-icon-btn" title="설정">
              ⚙️
            </button>
            <button className="top-icon-btn" title="알림">
              🔔
            </button>
            <button
              className="top-avatar logout-btn"
              onClick={handleLogout}
              title="로그아웃"
            >
              🚪
            </button>
          </div>
        </header>

        {/* 메인 컨텐츠 */}
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
