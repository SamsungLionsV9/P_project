import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import LoginPage from './LoginPage'
import './App.css'
import './LoginPage.css'

function Root() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 저장된 토큰과 사용자 정보 확인
    const token = localStorage.getItem('adminToken');
    const savedUser = localStorage.getItem('adminUser');
    
    if (token && savedUser) {
      // 토큰 유효성 검증
      verifyToken(token, JSON.parse(savedUser));
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (token, savedUser) => {
    try {
      const response = await fetch('http://localhost:8080/api/admin/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // 토큰이 유효하지 않으면 로그아웃
        handleLogout();
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      // 서버 연결 실패 시 저장된 사용자 정보 사용
      setUser(savedUser);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminUser');
    setUser(null);
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        color: '#fff',
        fontSize: '18px'
      }}>
        로딩 중...
      </div>
    );
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return <App user={user} onLogout={handleLogout} />;
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
)
