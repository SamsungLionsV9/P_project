import { useState } from "react";
import "./LoginPage.css";

function LoginPage({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/admin/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "omit",  // 세션 쿠키 전송 안함
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (data.success) {
        // 토큰과 사용자 정보 저장
        localStorage.setItem("adminToken", data.token);
        localStorage.setItem("adminUser", JSON.stringify(data.user));
        onLogin(data.user);
      } else {
        setError(data.message || "로그인에 실패했습니다");
      }
    } catch (err) {
      setError("서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.");
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo" />
          <h1>관리자 대시보드</h1>
          <p>Car-Sentix 관리 시스템</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="login-error">{error}</div>}

          <div className="form-group">
            <label>이메일</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@carsentix.com"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>비밀번호</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호를 입력하세요"
              required
              disabled={loading}
            />
          </div>

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? "로그인 중..." : "로그인"}
          </button>
        </form>

        <div className="login-footer">
          <p>기본 관리자 계정</p>
          <code>admin@carsentix.com / admin1234!</code>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;

