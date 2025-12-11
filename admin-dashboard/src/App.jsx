import { useState, useEffect, useRef } from "react";
import "./App.css";
import { Bell, LogOut, AlertTriangle, X } from "lucide-react";

// 컴포넌트 임포트
import { Sidebar, PlaceholderPage } from "./components";
import { DashboardPage, VehiclePage, UserPage, HistoryPage } from "./pages";
import AILogPage from "./pages/AILogPage";
import SettingsPage from "./pages/SettingsPage";
import EconomicInsightsPage from "./pages/EconomicInsightsPage";
import B2BMarketIntelligencePage from "./pages/B2BMarketIntelligencePage";

const pageTitleMap = {
  dashboard: "DashBoard",
  vehicles: "차량 데이터 관리",
  users: "사용자 관리",
  history: "분석 이력",
  insights: "B2B 인사이트",
  aiLog: "AI 로그",
  settings: "설정",
};

const API_BASE = "";  // 프록시 사용 (vite.config.js)

function App({ user, onLogout }) {
  const [activeMenu, setActiveMenu] = useState("dashboard");
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const notifRef = useRef(null);

  // 알림 조회
  const fetchNotifications = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/notifications?limit=20&unread_only=false`);
      const data = await res.json();
      if (data.success) {
        // 허위매물 고위험 알림만 필터링
        const fraudAlerts = (data.notifications || []).filter(
          n => n.type === 'fraud_alert' && n.data?.risk_level === 'high'
        );
        setNotifications(fraudAlerts);
        setUnreadCount(fraudAlerts.filter(n => !n.is_read).length);
      }
    } catch (e) {
      console.error('알림 조회 실패:', e);
    }
  };

  // 알림 읽음 처리
  const markAsRead = async (notifId) => {
    try {
      await fetch(`${API_BASE}/api/notifications/${notifId}/read`, { method: 'PUT' });
      fetchNotifications();
    } catch (e) {
      console.error('읽음 처리 실패:', e);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // 30초마다 갱신
    return () => clearInterval(interval);
  }, []);

  // 드롭다운 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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
      case "insights":
        return <B2BMarketIntelligencePage />;
      case "aiLog":
        return <AILogPage />;
      case "settings":
        return <SettingsPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="app-root">
      {/* 사이드바 */}
      <Sidebar activeMenu={activeMenu} setActiveMenu={setActiveMenu} />

      {/* 메인 영역 */}
      <main className={`main ${activeMenu === 'b2b' ? 'no-padding' : ''}`}>
        {/* 상단 바 - B2B 페이지에서는 숨김 (자체 헤더 사용) */}
        {activeMenu !== 'b2b' && (
        <header className="topbar">
          <h1 className="page-title">{pageTitleMap[activeMenu]}</h1>
          <div className="topbar-right">
            <span className="admin-name">{user?.username || "관리자"}</span>
            <div className="notification-wrapper" ref={notifRef}>
              <button 
                className={`top-icon-btn ${unreadCount > 0 ? 'has-notif' : ''}`} 
                title="알림"
                onClick={() => setShowNotifications(!showNotifications)}
              >
                <Bell size={18} />
                {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
              </button>
              
              {showNotifications && (
                <div className="notification-dropdown">
                  <div className="notif-header">
                    <span>🚨 허위매물 고위험 알림</span>
                    <button onClick={() => setShowNotifications(false)}><X size={14} /></button>
                  </div>
                  <div className="notif-list">
                    {notifications.length === 0 ? (
                      <div className="notif-empty">허위매물 고위험 알림이 없습니다</div>
                    ) : (
                      notifications.map(n => (
                        <div 
                          key={n.id} 
                          className={`notif-item ${n.is_read ? 'read' : 'unread'}`}
                          onClick={() => markAsRead(n.id)}
                        >
                          <div className="notif-icon"><AlertTriangle size={16} color="#dc2626" /></div>
                          <div className="notif-content">
                            <div className="notif-title">{n.title}</div>
                            <div className="notif-desc">{n.message}</div>
                            <div className="notif-meta">
                              <span>{n.data?.car_info}</span>
                              <span>{new Date(n.created_at).toLocaleString('ko-KR')}</span>
                            </div>
                          </div>
                          {!n.is_read && <span className="notif-dot"></span>}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
            <button
              className="top-avatar logout-btn"
              onClick={handleLogout}
              title="로그아웃"
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>
        )}

        {/* 메인 컨텐츠 */}
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
