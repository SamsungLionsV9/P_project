import React from "react";

const menuItems = [
  { key: "dashboard", label: "Dashboard", icon: "🏠" },
  { key: "vehicles", label: "차량 데이터 관리", icon: "🚗" },
  { key: "users", label: "사용자 관리", icon: "👤" },
  { key: "history", label: "분석 이력", icon: "📊" },
  { key: "aiLog", label: "AI 로그", icon: "🧠" },
  { key: "settings", label: "설정", icon: "⚙️" },
];

function Sidebar({ activeMenu, setActiveMenu }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-box" />
        <span className="service-name">Car-Sentix</span>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <div
            key={item.key}
            className={`nav-item ${activeMenu === item.key ? "active" : ""}`}
            onClick={() => setActiveMenu(item.key)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;

