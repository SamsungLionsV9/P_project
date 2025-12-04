import React from "react";
import {
  LayoutDashboard,
  Car,
  Users,
  BarChart3,
  Bot,
  Settings,
  Rocket
} from "lucide-react";

const menuItems = [
  { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { key: "vehicles", label: "차량 데이터 관리", icon: Car },
  { key: "users", label: "사용자 관리", icon: Users },
  { key: "history", label: "분석 이력", icon: BarChart3 },
  { key: "insights", label: "B2B 인사이트", icon: Rocket },
  { key: "aiLog", label: "AI 로그", icon: Bot },
  { key: "settings", label: "설정", icon: Settings },
];

function Sidebar({ activeMenu, setActiveMenu }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-box" />
        <span className="service-name">언제 살까?</span>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => {
          const IconComponent = item.icon;
          return (
            <div
              key={item.key}
              className={`nav-item ${activeMenu === item.key ? "active" : ""}`}
              onClick={() => setActiveMenu(item.key)}
            >
              <span className="nav-icon">
                <IconComponent size={18} />
              </span>
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>
    </aside>
  );
}

export default Sidebar;

