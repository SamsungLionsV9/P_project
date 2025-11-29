import React, { useState, useEffect } from "react";
import Pagination from "../components/Pagination";

function VehiclePage() {
  const [modelFilter, setModelFilter] = useState("");
  const [brandFilter, setBrandFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [vehicles, setVehicles] = useState([]);
  const [displayedVehicles, setDisplayedVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    domesticCount: 0,
    importedCount: 0,
    totalCount: 0,
  });
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [vehicleDetail, setVehicleDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const closeDetail = () => {
    setSelectedVehicle(null);
    setVehicleDetail(null);
  };

  // 차량 상세정보 로드 (옵션, 사고이력)
  const loadVehicleDetail = async (vehicle) => {
    setDetailLoading(true);
    try {
      const response = await fetch(`/api/admin/vehicle/${vehicle.id}?category=${vehicle.category}`);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setVehicleDetail(data);
        }
      }
    } catch (err) {
      console.error("Failed to load vehicle detail:", err);
    } finally {
      setDetailLoading(false);
    }
  };

  // 상세 버튼 클릭 시
  const handleDetailClick = (vehicle) => {
    setSelectedVehicle(vehicle);
    loadVehicleDetail(vehicle);
  };

  const loadVehicles = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (brandFilter) params.append("brand", brandFilter);
      if (modelFilter) params.append("model", modelFilter);
      params.append("category", categoryFilter);
      params.append("limit", "50");

      const response = await fetch(`/api/admin/vehicles?${params}`);
      if (!response.ok) {
        throw new Error(`서버 오류: ${response.status}`);
      }
      const data = await response.json();
      if (data.success) {
        setVehicles(data.vehicles);
        setDisplayedVehicles(data.vehicles);
      } else {
        throw new Error(data.message || "데이터 로드 실패");
      }

      const statsRes = await fetch("/api/admin/vehicle-stats");
      const statsData = await statsRes.json();
      if (statsData.success) {
        setStats(statsData);
      }
    } catch (err) {
      console.error("Failed to load vehicles:", err);
      setError(err.message || "차량 데이터를 불러오는데 실패했습니다");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVehicles();
  }, []);

  const handleSearch = () => {
    loadVehicles();
  };

  const handleReset = () => {
    setModelFilter("");
    setBrandFilter("");
    setCategoryFilter("all");
    loadVehicles();
  };

  const formatPrice = (price) => {
    if (!price) return "-";
    return `${price.toLocaleString()}만원`;
  };

  const formatMileage = (mileage) => {
    if (!mileage) return "-";
    return `${(mileage / 10000).toFixed(1)}만km`;
  };

  return (
    <div className="page">
      <section className="content-header">
        <h2>차량 데이터 관리</h2>
        <div style={{ fontSize: "14px", color: "#666", marginTop: "8px" }}>
          총 {stats.totalCount.toLocaleString()}대 (국산{" "}
          {stats.domesticCount.toLocaleString()} / 수입{" "}
          {stats.importedCount.toLocaleString()})
        </div>
      </section>

      <section className="filter-section">
        <div className="filter-card">
          <div className="filter-grid three">
            <div className="filter-field">
              <label>브랜드</label>
              <input
                placeholder="브랜드 검색"
                value={brandFilter}
                onChange={(e) => setBrandFilter(e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>모델명</label>
              <input
                placeholder="모델명 검색"
                value={modelFilter}
                onChange={(e) => setModelFilter(e.target.value)}
              />
            </div>
            <div className="filter-field">
              <label>카테고리</label>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <option value="all">전체</option>
                <option value="domestic">국산차</option>
                <option value="imported">수입차</option>
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
            <button className="btn-ghost" onClick={loadVehicles}>
              새로고침
            </button>
          </div>
        </div>
        <div className="filter-underline" />
      </section>

      <section className="table-section">
        <div className="table-header-row">
          <div className="table-header-left">
            차량 목록 ({displayedVehicles.length}대)
          </div>
        </div>

        <div className="table-card">
          {loading ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
              로딩 중...
            </div>
          ) : error ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#e74c3c" }}>
              <div style={{ marginBottom: "10px" }}>⚠️ {error}</div>
              <button className="btn-primary" onClick={loadVehicles}>
                다시 시도
              </button>
            </div>
          ) : displayedVehicles.length === 0 ? (
            <div style={{ padding: "40px", textAlign: "center", color: "#888" }}>
              검색 결과가 없습니다
            </div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>구분</th>
                  <th>브랜드</th>
                  <th>모델명</th>
                  <th>연식</th>
                  <th>주행거리</th>
                  <th>연료</th>
                  <th>가격</th>
                  <th>지역</th>
                  <th>상세</th>
                </tr>
              </thead>
              <tbody>
                {displayedVehicles.map((row, i) => (
                  <tr key={row.id || i}>
                    <td>
                      <span className={`category-badge ${row.category}`}>
                        {row.category === "domestic" ? "국산" : "수입"}
                      </span>
                    </td>
                    <td>{row.brand}</td>
                    <td>{row.model}</td>
                    <td>{row.year}년</td>
                    <td>{formatMileage(row.mileage)}</td>
                    <td>{row.fuel || "-"}</td>
                    <td className="strong-text">{formatPrice(row.price)}</td>
                    <td>{row.region || "-"}</td>
                    <td>
                      <button
                        className="btn-outline"
                        onClick={() => handleDetailClick(row)}
                      >
                        상세
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

      {/* 상세 모달 */}
      {selectedVehicle && (
        <div className="modal-backdrop" onClick={closeDetail}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>차량 상세 정보</h3>
              <button className="modal-close" onClick={closeDetail}>
                ✕
              </button>
            </div>

            <div className="detail-section">
              <div className="detail-label">기본 정보</div>
              <div className="detail-info-grid">
                <div>
                  <span className="info-label">브랜드:</span>
                  <span>{selectedVehicle.brand}</span>
                </div>
                <div>
                  <span className="info-label">모델:</span>
                  <span>{selectedVehicle.model}</span>
                </div>
                <div>
                  <span className="info-label">연식:</span>
                  <span>{selectedVehicle.year}년</span>
                </div>
                <div>
                  <span className="info-label">가격:</span>
                  <span className="strong-text">
                    {formatPrice(selectedVehicle.price)}
                  </span>
                </div>
                <div>
                  <span className="info-label">주행거리:</span>
                  <span>{formatMileage(selectedVehicle.mileage)}</span>
                </div>
                <div>
                  <span className="info-label">연료:</span>
                  <span>{selectedVehicle.fuel || "-"}</span>
                </div>
              </div>
            </div>

            {/* 사고 이력 / 성능점검 */}
            {vehicleDetail && (
              <div className="detail-section">
                <div className="detail-label">차량 상태</div>
                <div className="detail-info-grid">
                  <div>
                    <span className="info-label">무사고:</span>
                    <span className={vehicleDetail.is_accident_free ? "text-success" : "text-warning"}>
                      {vehicleDetail.is_accident_free ? "✅ 무사고" : "⚠️ 사고이력 있음"}
                    </span>
                  </div>
                  <div>
                    <span className="info-label">성능점검:</span>
                    <span className={vehicleDetail.inspection_grade === "excellent" ? "text-success" : ""}>
                      {vehicleDetail.inspection_grade === "excellent" ? "우수" :
                       vehicleDetail.inspection_grade === "good" ? "양호" : "보통"}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="detail-section">
              <div className="detail-label">옵션</div>
              {detailLoading ? (
                <p>옵션 정보 로딩 중...</p>
              ) : (
                <div className="detail-options-grid">
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={!!(vehicleDetail?.options?.sunroof || selectedVehicle.options?.sunroof)}
                      readOnly
                    />
                    <span>선루프</span>
                  </label>
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={!!(vehicleDetail?.options?.navigation || selectedVehicle.options?.navigation)}
                      readOnly
                    />
                    <span>내비게이션</span>
                  </label>
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={!!(vehicleDetail?.options?.leather_seat || selectedVehicle.options?.leather_seat)}
                      readOnly
                    />
                    <span>가죽시트</span>
                  </label>
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={!!(vehicleDetail?.options?.smart_key || selectedVehicle.options?.smart_key)}
                      readOnly
                    />
                    <span>스마트키</span>
                  </label>
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={!!(vehicleDetail?.options?.rear_camera || selectedVehicle.options?.rear_camera)}
                      readOnly
                    />
                    <span>후방카메라</span>
                  </label>
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={!!(vehicleDetail?.options?.heated_seat || selectedVehicle.options?.heated_seat)}
                      readOnly
                    />
                    <span>열선시트</span>
                  </label>
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={!!(vehicleDetail?.options?.ventilated_seat)}
                      readOnly
                    />
                    <span>통풍시트</span>
                  </label>
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={!!(vehicleDetail?.options?.led_lamp)}
                      readOnly
                    />
                    <span>LED램프</span>
                  </label>
                </div>
              )}
            </div>

            <div className="detail-section">
              <div className="detail-label">지역</div>
              <div className="detail-region-pill">
                {vehicleDetail?.region || selectedVehicle.region || "-"}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VehiclePage;

