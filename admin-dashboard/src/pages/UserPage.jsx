import React, { useState, useEffect } from "react";
import Pagination from "../components/Pagination";

function UserPage() {
  const [filters, setFilters] = useState({
    email: "",
    username: "",
    phone: "",
    role: "all",
  });

  const [users, setUsers] = useState([]);
  const [displayedUsers, setDisplayedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState(null);
  const [editForm, setEditForm] = useState({
    username: "",
    phoneNumber: "",
    role: "USER",
  });

  const loadUsers = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem("adminToken");
      const response = await fetch("http://localhost:8080/api/admin/users", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await response.json();
      if (data.success) {
        setUsers(data.users);
        setDisplayedUsers(data.users);
      }
    } catch (error) {
      console.error("Failed to load users:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleSearch = () => {
    const filtered = users.filter((row) => {
      const matchEmail =
        filters.email.trim() === "" ||
        row.email.toLowerCase().includes(filters.email.toLowerCase());
      const matchUsername =
        filters.username.trim() === "" ||
        row.username.toLowerCase().includes(filters.username.toLowerCase());
      const matchPhone =
        filters.phone.trim() === "" ||
        (row.phoneNumber && row.phoneNumber.includes(filters.phone.trim()));
      const matchRole = filters.role === "all" || row.role === filters.role;

      return matchEmail && matchUsername && matchPhone && matchRole;
    });
    setDisplayedUsers(filtered);
  };

  const handleReset = () => {
    setFilters({ email: "", username: "", phone: "", role: "all" });
    setDisplayedUsers(users);
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setEditForm({
      username: user.username || "",
      phoneNumber: user.phoneNumber || "",
      role: user.role || "USER",
    });
  };

  const handleEditSubmit = async () => {
    try {
      const token = localStorage.getItem("adminToken");
      const response = await fetch(
        `http://localhost:8080/api/admin/users/${editingUser.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(editForm),
        }
      );
      const data = await response.json();
      if (data.success) {
        alert("사용자 정보가 수정되었습니다");
        setEditingUser(null);
        loadUsers();
      } else {
        alert(data.message || "수정 실패");
      }
    } catch (error) {
      alert("수정 중 오류가 발생했습니다");
      console.error(error);
    }
  };

  const handleDelete = async (user) => {
    if (
      !window.confirm(`${user.email} (${user.username}) 를 삭제하시겠습니까?`)
    )
      return;

    try {
      const token = localStorage.getItem("adminToken");
      const response = await fetch(
        `http://localhost:8080/api/admin/users/${user.id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      if (data.success) {
        alert("사용자가 삭제되었습니다");
        loadUsers();
      } else {
        alert(data.message || "삭제 실패");
      }
    } catch (error) {
      alert("삭제 중 오류가 발생했습니다");
      console.error(error);
    }
  };

  const handleToggleActive = async (user) => {
    try {
      const token = localStorage.getItem("adminToken");
      const endpoint = user.isActive ? "deactivate" : "activate";
      const response = await fetch(
        `http://localhost:8080/api/admin/users/${user.id}/${endpoint}`,
        {
          method: "PUT",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      if (data.success) {
        loadUsers();
      }
    } catch (error) {
      console.error(error);
    }
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case "ADMIN":
        return "관리자";
      case "USER":
        return "일반 사용자";
      default:
        return role;
    }
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
              <label>이메일</label>
              <input
                placeholder="이메일 검색"
                value={filters.email}
                onChange={(e) => handleChange("email", e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>사용자명</label>
              <input
                placeholder="사용자명 검색"
                value={filters.username}
                onChange={(e) => handleChange("username", e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>전화번호</label>
              <input
                placeholder="전화번호 검색"
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
                <option value="ADMIN">관리자</option>
                <option value="USER">일반 사용자</option>
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
            <button className="btn-ghost" onClick={loadUsers}>
              새로고침
            </button>
          </div>
        </div>
        <div className="filter-underline" />
      </section>

      <section className="table-section">
        <div className="table-header-row">
          <div className="table-header-left">
            사용자 관리 ({displayedUsers.length}명)
          </div>
        </div>

        <div className="table-card">
          {loading ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
              로딩 중...
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>이메일</th>
                  <th>사용자명</th>
                  <th>전화번호</th>
                  <th>권한</th>
                  <th>가입방식</th>
                  <th>상태</th>
                  <th>관리</th>
                </tr>
              </thead>
              <tbody>
                {displayedUsers.map((user) => (
                  <tr key={user.id} style={{ opacity: user.isActive ? 1 : 0.5 }}>
                    <td>{user.id}</td>
                    <td>{user.email}</td>
                    <td>{user.username}</td>
                    <td>{user.phoneNumber || "-"}</td>
                    <td>
                      <span className={`role-badge ${user.role.toLowerCase()}`}>
                        {getRoleLabel(user.role)}
                      </span>
                    </td>
                    <td>{user.provider}</td>
                    <td>
                      <span
                        className={`status-badge ${
                          user.isActive ? "active" : "inactive"
                        }`}
                        onClick={() => handleToggleActive(user)}
                        style={{ cursor: "pointer" }}
                      >
                        {user.isActive ? "활성" : "비활성"}
                      </span>
                    </td>
                    <td className="user-actions-cell">
                      <button
                        className="btn-chip blue"
                        onClick={() => handleEdit(user)}
                      >
                        수정
                      </button>
                      <button
                        className="btn-chip red"
                        onClick={() => handleDelete(user)}
                      >
                        삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <Pagination />
        </div>
      </section>

      {/* 수정 모달 */}
      {editingUser && (
        <div className="modal-backdrop" onClick={() => setEditingUser(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>사용자 정보 수정</h3>
              <button
                className="modal-close"
                onClick={() => setEditingUser(null)}
              >
                ✕
              </button>
            </div>

            <div className="edit-form">
              <div className="form-group">
                <label>이메일 (수정 불가)</label>
                <input type="text" value={editingUser.email} disabled />
              </div>

              <div className="form-group">
                <label>사용자명</label>
                <input
                  type="text"
                  value={editForm.username}
                  onChange={(e) =>
                    setEditForm({ ...editForm, username: e.target.value })
                  }
                />
              </div>

              <div className="form-group">
                <label>전화번호</label>
                <input
                  type="text"
                  value={editForm.phoneNumber}
                  onChange={(e) =>
                    setEditForm({ ...editForm, phoneNumber: e.target.value })
                  }
                  placeholder="010-0000-0000"
                />
              </div>

              <div className="form-group">
                <label>권한</label>
                <select
                  value={editForm.role}
                  onChange={(e) =>
                    setEditForm({ ...editForm, role: e.target.value })
                  }
                >
                  <option value="USER">일반 사용자</option>
                  <option value="ADMIN">관리자</option>
                </select>
              </div>

              <div className="modal-actions">
                <button
                  className="btn-ghost"
                  onClick={() => setEditingUser(null)}
                >
                  취소
                </button>
                <button className="btn-primary" onClick={handleEditSubmit}>
                  저장
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserPage;

