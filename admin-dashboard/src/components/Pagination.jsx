import React from "react";

function Pagination({ currentPage = 1, totalPages = 1, onPageChange }) {
  // 최대 표시할 페이지 버튼 수
  const MAX_VISIBLE = 7;
  
  // 표시할 페이지 범위 계산
  const getPageNumbers = () => {
    if (totalPages <= MAX_VISIBLE) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    
    const pages = [];
    const half = Math.floor(MAX_VISIBLE / 2);
    
    let start = Math.max(1, currentPage - half);
    let end = Math.min(totalPages, currentPage + half);
    
    // 시작 또는 끝 조정
    if (currentPage <= half) {
      end = MAX_VISIBLE - 1;
    } else if (currentPage >= totalPages - half) {
      start = totalPages - MAX_VISIBLE + 2;
    }
    
    // 첫 페이지
    if (start > 1) {
      pages.push(1);
      if (start > 2) pages.push("...");
    }
    
    // 중간 페이지들
    for (let i = start; i <= end; i++) {
      if (i > 0 && i <= totalPages) pages.push(i);
    }
    
    // 마지막 페이지
    if (end < totalPages) {
      if (end < totalPages - 1) pages.push("...");
      pages.push(totalPages);
    }
    
    return pages;
  };

  return (
    <div className="pagination">
      <button
        className="page-link"
        onClick={() => onPageChange && onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
      >
        &lt;
      </button>
      <div className="page-numbers">
        {getPageNumbers().map((page, idx) => (
          page === "..." ? (
            <span key={`ellipsis-${idx}`} className="page-ellipsis">...</span>
          ) : (
            <button
              key={page}
              className={`page-number ${currentPage === page ? "active" : ""}`}
              onClick={() => onPageChange && onPageChange(page)}
            >
              {page}
            </button>
          )
        ))}
      </div>
      <button
        className="page-link"
        onClick={() => onPageChange && onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
      >
        &gt;
      </button>
      <span className="page-info">
        {currentPage.toLocaleString()} / {totalPages.toLocaleString()}
      </span>
    </div>
  );
}

export default Pagination;

