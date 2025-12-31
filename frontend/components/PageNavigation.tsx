'use client'

interface PageNavigationProps {
  currentPage: number
  totalPages: number
  zoom: number
  onPageChange: (page: number) => void
  onZoomChange: (zoom: number) => void
}

const ZOOM_LEVELS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]

export default function PageNavigation({
  currentPage,
  totalPages,
  zoom,
  onPageChange,
  onZoomChange,
}: PageNavigationProps) {
  const handlePrevious = () => {
    if (currentPage > 0) {
      onPageChange(currentPage - 1)
    }
  }

  const handleNext = () => {
    if (currentPage < totalPages - 1) {
      onPageChange(currentPage + 1)
    }
  }

  const handleZoomIn = () => {
    const currentIndex = ZOOM_LEVELS.indexOf(zoom)
    if (currentIndex < ZOOM_LEVELS.length - 1) {
      onZoomChange(ZOOM_LEVELS[currentIndex + 1])
    }
  }

  const handleZoomOut = () => {
    const currentIndex = ZOOM_LEVELS.indexOf(zoom)
    if (currentIndex > 0) {
      onZoomChange(ZOOM_LEVELS[currentIndex - 1])
    }
  }

  const handleZoomReset = () => {
    onZoomChange(1.0)
  }

  return (
    <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
      {/* Page Navigation */}
      <div className="flex items-center space-x-2">
        <button
          onClick={handlePrevious}
          disabled={currentPage === 0}
          className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Previous page"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Page</span>
          <input
            type="number"
            value={currentPage + 1}
            onChange={(e) => {
              const page = parseInt(e.target.value) - 1
              if (page >= 0 && page < totalPages) {
                onPageChange(page)
              }
            }}
            min="1"
            max={totalPages}
            className="w-16 px-2 py-1 text-sm text-center border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <span className="text-sm text-gray-600">of {totalPages}</span>
        </div>

        <button
          onClick={handleNext}
          disabled={currentPage === totalPages - 1}
          className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Next page"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Zoom Controls */}
      <div className="flex items-center space-x-2">
        <button
          onClick={handleZoomOut}
          disabled={zoom === ZOOM_LEVELS[0]}
          className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Zoom out"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
          </svg>
        </button>

        <select
          value={zoom}
          onChange={(e) => onZoomChange(parseFloat(e.target.value))}
          className="px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          {ZOOM_LEVELS.map((level) => (
            <option key={level} value={level}>
              {Math.round(level * 100)}%
            </option>
          ))}
        </select>

        <button
          onClick={handleZoomIn}
          disabled={zoom === ZOOM_LEVELS[ZOOM_LEVELS.length - 1]}
          className="p-2 rounded-md hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          title="Zoom in"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
          </svg>
        </button>

        <button
          onClick={handleZoomReset}
          className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          title="Reset zoom to 100%"
        >
          Reset
        </button>
      </div>

      {/* Quick Info */}
      <div className="text-sm text-gray-600">
        Zoom: {Math.round(zoom * 100)}%
      </div>
    </div>
  )
}
