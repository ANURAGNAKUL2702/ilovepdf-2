'use client'

import { useEffect, useRef, useState } from 'react'
import * as pdfjsLib from 'pdfjs-dist'
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
  mode,
}: PDFCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [pdfDoc, setPdfDoc] = useState<any>(null)
  const [pageCount, setPageCount] = useState(0)
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
        setPageCount(pdf.numPages)
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
        <div ref={containerRef} className="inline-block relative">
          <canvas ref={canvasRef} className="shadow-lg bg-white" />
          
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
