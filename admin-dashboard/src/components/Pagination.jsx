import React from "react";

function Pagination({ currentPage = 1, totalPages = 4, onPageChange }) {
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);

  return (
    <div className="pagination">
      <button
        className="page-link"
        onClick={() => onPageChange && onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
      >
        &lt; Previous
      </button>
      <div className="page-numbers">
        {pages.map((page) => (
          <button
            key={page}
            className={`page-number ${currentPage === page ? "active" : ""}`}
            onClick={() => onPageChange && onPageChange(page)}
          >
            {page}
          </button>
        ))}
      </div>
      <button
        className="page-link"
        onClick={() => onPageChange && onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
      >
        Next &gt;
      </button>
    </div>
  );
}

export default Pagination;

