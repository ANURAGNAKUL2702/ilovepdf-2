'use client'

import { useEffect, useRef, useState } from 'react'
import * as pdfjsLib from 'pdfjs-dist'
import type { PDFDocumentProxy } from 'pdfjs-dist'
import { TextBlock } from '@/types'

// Configure PDF.js worker
if (typeof window !== 'undefined') {
  pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`
}

interface PDFCanvasProps {
  file: File | null
  currentPage: number
  zoom: number
  textBlocks: TextBlock[]
  selectedBlockId: string | null
  onTextBlockSelect: (block: TextBlock) => void
  onTextBlockEdit: (blockId: string, newText: string) => void
  onAddText: (x: number, y: number, text?: string) => void
  onRotatePage?: (pageNum: number, degrees: 90 | 180 | 270) => void
  onReorderPages?: (fromPage: number, toPage: number) => void
  mode: string
}

export default function PDFCanvas({
  file,
  currentPage,
  zoom,
  textBlocks,
  selectedBlockId,
  onTextBlockSelect,
  onTextBlockEdit,
  onAddText,
  onRotatePage,
  onReorderPages,
  mode,
}: PDFCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [pdfDoc, setPdfDoc] = useState<PDFDocumentProxy | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [editingBlockId, setEditingBlockId] = useState<string | null>(null)
  const [editText, setEditText] = useState('')

  // Load PDF document
  useEffect(() => {
    if (!file) return

    setIsLoading(true)
    const fileReader = new FileReader()

    fileReader.onload = async (e) => {
      const typedArray = new Uint8Array(e.target?.result as ArrayBuffer)
      try {
        const loadingTask = pdfjsLib.getDocument(typedArray)
        const pdf = await loadingTask.promise
        setPdfDoc(pdf)
      } catch (error) {
        console.error('Error loading PDF:', error)
        alert('Failed to load PDF. Please try another file.')
      } finally {
        setIsLoading(false)
      }
    }

    fileReader.readAsArrayBuffer(file)
  }, [file])

  // Render current page
  useEffect(() => {
    if (!pdfDoc || !canvasRef.current) return

    const renderPage = async () => {
      try {
        const page = await pdfDoc.getPage(currentPage + 1)
        const viewport = page.getViewport({ scale: zoom })
        const canvas = canvasRef.current!
        const context = canvas.getContext('2d')!

        canvas.height = viewport.height
        canvas.width = viewport.width

        const renderContext = {
          canvasContext: context,
          viewport: viewport,
        }

        await page.render(renderContext).promise
      } catch (error) {
        console.error('Error rendering page:', error)
      }
    }

    renderPage()
  }, [pdfDoc, currentPage, zoom])

  const handleTextBlockClick = (block: TextBlock) => {
    if (mode === 'edit-text') {
      onTextBlockSelect(block)
    }
  }

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (mode === 'add-text' && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect()
      const x = (e.clientX - rect.left) / zoom
      const y = (e.clientY - rect.top) / zoom
      onAddText(x, y)
    } else if (mode === 'rotate-pages') {
      console.log('Rotate pages mode - click detected on canvas')
      // Placeholder for rotate functionality
    } else if (mode === 'organize-pages') {
      console.log('Organize pages mode - click detected on canvas')
      // Placeholder for organize functionality - onReorderPages will be used by page navigation
      if (onReorderPages) {
        console.log('Page reordering available')
      }
    }
  }

  const handleTextBlockDoubleClick = (block: TextBlock) => {
    if (mode === 'edit-text') {
      setEditingBlockId(block.id)
      setEditText(block.text)
    }
  }

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditText(e.target.value)
  }

  const handleTextBlur = () => {
    if (editingBlockId) {
      onTextBlockEdit(editingBlockId, editText)
      setEditingBlockId(null)
    }
  }

  const handleTextKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setEditingBlockId(null)
    } else if (e.key === 'Enter' && e.ctrlKey) {
      handleTextBlur()
    }
  }

  const currentPageBlocks = textBlocks.filter((block) => block.pageNumber === currentPage)

  // Handler for rotate button clicks
  const handleRotateClick = (degrees: 90 | 180 | 270) => {
    if (onRotatePage) {
      onRotatePage(currentPage, degrees)
    }
  }

  return (
    <div className="flex-1 overflow-auto bg-gray-100 p-8">
      {!file ? (
        <div className="flex items-center justify-center h-full">
          <div className="text-center max-w-md">
            <svg
              className="w-24 h-24 mx-auto text-gray-300 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="text-xl font-medium text-gray-700 mb-2">No PDF Loaded</h3>
            <p className="text-gray-500">
              Upload a PDF file using the button in the top navigation bar to get started
            </p>
          </div>
        </div>
      ) : isLoading ? (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-primary-600 mb-4"></div>
            <p className="text-gray-600">Loading PDF...</p>
          </div>
        </div>
      ) : (
        <div 
          ref={containerRef} 
          className="inline-block relative cursor-pointer" 
          onClick={handleCanvasClick}
          style={{ 
            cursor: mode === 'add-text' ? 'crosshair' 
              : mode === 'edit-text' ? 'text'
              : mode === 'rotate-pages' ? 'grab'
              : mode === 'organize-pages' ? 'move'
              : 'default' 
          }}
        >
          {/* Active Mode Indicator */}
          <div className="absolute top-4 right-4 bg-white rounded-lg shadow-md px-3 py-2 border border-gray-200 z-10 flex items-center space-x-2">
            {mode === 'view' && (
              <>
                <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span className="text-xs font-medium text-gray-700">View Mode</span>
              </>
            )}
            {mode === 'edit-text' && (
              <>
                <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                <span className="text-xs font-medium text-primary-700">Edit Text</span>
              </>
            )}
            {mode === 'add-text' && (
              <>
                <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span className="text-xs font-medium text-primary-700">Add Text - Click to place</span>
              </>
            )}
            {mode === 'organize-pages' && (
              <>
                <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
                <span className="text-xs font-medium text-primary-700">Organize Pages</span>
              </>
            )}
            {mode === 'rotate-pages' && (
              <>
                <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span className="text-xs font-medium text-primary-700">Rotate Pages</span>
              </>
            )}
          </div>

          <canvas ref={canvasRef} className="shadow-lg bg-white" />
          
          {/* Rotate Controls Overlay */}
          {mode === 'rotate-pages' && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg p-4 flex items-center space-x-2 border border-gray-200 z-10">
              <span className="text-sm font-medium text-gray-700">Rotate Page:</span>
              <button
                onClick={() => handleRotateClick(90)}
                className="flex items-center space-x-1 px-3 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors text-sm font-medium"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>90°</span>
              </button>
              <button
                onClick={() => handleRotateClick(180)}
                className="flex items-center space-x-1 px-3 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors text-sm font-medium"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>180°</span>
              </button>
              <button
                onClick={() => handleRotateClick(270)}
                className="flex items-center space-x-1 px-3 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors text-sm font-medium"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>270°</span>
              </button>
            </div>
          )}

          {/* Organize Pages Mode Indicator */}
          {mode === 'organize-pages' && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-white rounded-lg shadow-lg p-4 border border-gray-200 z-10">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
                <span className="text-sm font-medium text-gray-700">Use page navigation to reorder pages</span>
              </div>
            </div>
          )}
          
          {/* Text block overlays */}
          {currentPageBlocks.map((block) => {
            const isSelected = block.id === selectedBlockId
            const isEditing = block.id === editingBlockId

            return (
              <div
                key={block.id}
                className={`text-overlay ${isSelected ? 'selected' : ''}`}
                style={{
                  left: `${block.x0 * zoom}px`,
                  top: `${block.y0 * zoom}px`,
                  width: `${(block.x1 - block.x0) * zoom}px`,
                  height: `${(block.y1 - block.y0) * zoom}px`,
                  fontSize: `${block.fontSize * zoom}px`,
                  pointerEvents: mode === 'edit-text' ? 'auto' : 'none',
                }}
                onClick={() => handleTextBlockClick(block)}
                onDoubleClick={() => handleTextBlockDoubleClick(block)}
              >
                {isEditing ? (
                  <textarea
                    value={editText}
                    onChange={handleTextChange}
                    onBlur={handleTextBlur}
                    onKeyDown={handleTextKeyDown}
                    autoFocus
                    className="text-overlay-editable"
                    style={{
                      width: '100%',
                      height: '100%',
                      fontSize: `${block.fontSize * zoom}px`,
                      fontFamily: block.fontName,
                    }}
                  />
                ) : null}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
