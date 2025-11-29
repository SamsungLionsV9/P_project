import React, { useState, useEffect } from "react";
import { Settings, Database, Bot, Bell, Shield, Save, RefreshCw, Server, HardDrive } from "lucide-react";

function SettingsPage() {
  const [aiStatus, setAiStatus] = useState({ groq_available: false, model: null });
  const [dbStats, setDbStats] = useState({ total_records: 0, db_size: '0 KB' });
  const [settings, setSettings] = useState({
    notifications: true,
    autoBackup: false,
    darkMode: true,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      // AI 상태 확인
      const aiRes = await fetch("/api/ai/status");
      if (aiRes.ok) {
        const aiData = await aiRes.json();
        setAiStatus(aiData);
      }
      
      // DB 통계 (분석 이력 수로 대체)
      const historyRes = await fetch("/api/admin/analysis-history?limit=1");
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        setDbStats({ 
          total_records: historyData.total || 0,
          db_size: 'SQLite (영구 저장)'
        });
      }
    } catch (err) {
      console.error("Settings load failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    // 설정 저장 로직 (추후 구현)
    setTimeout(() => {
      setSaving(false);
      alert("설정이 저장되었습니다.");
    }, 500);
  };

  if (loading) {
    return (
      <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
        설정 로딩 중...
      </div>
    );
  }

  return (
    <div className="settings-page">
      {/* AI 엔진 상태 */}
      <section className="settings-section">
        <div className="section-header">
          <Bot size={20} />
          <h2>AI 엔진</h2>
        </div>
        <div className="settings-card">
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-label">Groq AI 연결</span>
              <span className="setting-desc">
                {aiStatus.groq_available ? aiStatus.model : "연결 안됨"}
              </span>
            </div>
            <span className={`status-badge ${aiStatus.groq_available ? "status-success" : "status-error"}`}>
              {aiStatus.groq_available ? "연결됨" : "오프라인"}
            </span>
          </div>
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-label">분석 기능</span>
              <span className="setting-desc">네고 대본, 시그널 분석, 허위매물 탐지</span>
            </div>
            <span className={`status-badge ${aiStatus.groq_available ? "status-success" : "status-warning"}`}>
              {aiStatus.groq_available ? "AI 분석" : "규칙 기반"}
            </span>
          </div>
        </div>
      </section>

      {/* 데이터베이스 */}
      <section className="settings-section">
        <div className="section-header">
          <Database size={20} />
          <h2>데이터베이스</h2>
        </div>
        <div className="settings-card">
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-label">저장소 타입</span>
              <span className="setting-desc">{dbStats.db_size}</span>
            </div>
            <span className="status-badge status-info">SQLite</span>
          </div>
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-label">분석 이력</span>
              <span className="setting-desc">저장된 분석 결과 수</span>
            </div>
            <span className="setting-value">{dbStats.total_records.toLocaleString()}건</span>
          </div>
        </div>
      </section>

      {/* 시스템 설정 */}
      <section className="settings-section">
        <div className="section-header">
          <Settings size={20} />
          <h2>시스템 설정</h2>
        </div>
        <div className="settings-card">
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-label">알림</span>
              <span className="setting-desc">가격 변동 및 이상 탐지 알림</span>
            </div>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={settings.notifications}
                onChange={(e) => setSettings({...settings, notifications: e.target.checked})}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
          <div className="setting-item">
            <div className="setting-info">
              <span className="setting-label">자동 백업</span>
              <span className="setting-desc">매일 자정 자동 백업</span>
            </div>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={settings.autoBackup}
                onChange={(e) => setSettings({...settings, autoBackup: e.target.checked})}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>
      </section>

      {/* 저장 버튼 */}
      <div className="settings-actions">
        <button className="btn-secondary" onClick={loadSettings}>
          <RefreshCw size={16} />
          새로고침
        </button>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          <Save size={16} />
          {saving ? "저장 중..." : "설정 저장"}
        </button>
      </div>
    </div>
  );
}

export default SettingsPage;

