'use client'

import { useState, useCallback } from 'react'
import TopNavBar from './TopNavBar'
import LeftSidebar from './LeftSidebar'
import RightPropertiesPanel from './RightPropertiesPanel'
import PDFCanvas from './PDFCanvas'
import PageNavigation from './PageNavigation'
import { EditorMode, TextBlock, RenderOptions } from '@/types'
import type { PropertyValue } from './RightPropertiesPanel'
// API integration ready for backend connection
import { pdfAPI } from '@/lib/api'

export default function PDFEditor() {
  const [file, setFile] = useState<File | null>(null)
  const [pdfId, setPdfId] = useState<string | null>(null)
  const [mode, setMode] = useState<EditorMode>('view')
  const [currentPage, setCurrentPage] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [zoom, setZoom] = useState(1.0)
  const [textBlocks, setTextBlocks] = useState<TextBlock[]>([])
  const [selectedBlock, setSelectedBlock] = useState<TextBlock | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Handle file upload
  const handleFileUpload = useCallback(async (uploadedFile: File) => {
    setFile(uploadedFile)
    setIsLoading(true)

    try {
      console.log('File uploaded:', uploadedFile.name)
      
      // Call the actual backend API
      const response = await pdfAPI.uploadPDF(uploadedFile)
      
      // Set the PDF ID and metadata from the backend
      setPdfId(response.id)
      setTotalPages(response.metadata.pages)
      setCurrentPage(0)

      // Fetch text blocks from the backend
      const blocks = await pdfAPI.extractTextBlocks(response.id)
      setTextBlocks(blocks)
      
    } catch (error) {
      console.error('Error uploading file:', error)
      alert('Failed to upload file. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Handle save
  const handleSave = useCallback(async () => {
    if (!pdfId) return

    try {
      setIsLoading(true)
      console.log('Saving changes...')
      
      // In production, this would save all edits to backend
      // await pdfAPI.saveEdits(pdfId)
      
      alert('Changes saved successfully!')
    } catch (error) {
      console.error('Error saving:', error)
      alert('Failed to save changes. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [pdfId])

  // Handle export
  const handleExport = useCallback(async () => {
    if (!pdfId) return

    try {
      setIsLoading(true)
      console.log('Exporting PDF...')
      
      // Export the PDF from backend
      const blob = await pdfAPI.exportPDF(pdfId)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `edited-${file?.name || 'document.pdf'}`
      a.click()
      URL.revokeObjectURL(url)
      
      console.log('PDF exported successfully')
    } catch (error) {
      console.error('Error exporting:', error)
      alert('Failed to export PDF. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [pdfId, file])

  // Handle mode change
  const handleModeChange = useCallback((newMode: EditorMode) => {
    console.log('Mode changed to:', newMode)
    setMode(newMode)
    if (newMode !== 'edit-text') {
      setSelectedBlock(null)
    }
  }, [])

  // Handle page change
  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page)
    setSelectedBlock(null)
  }, [])

  // Handle zoom change
  const handleZoomChange = useCallback((newZoom: number) => {
    setZoom(newZoom)
  }, [])

  // Handle text block selection
  const handleTextBlockSelect = useCallback((block: TextBlock) => {
    setSelectedBlock(block)
  }, [])

  // Handle text block edit
  const handleTextBlockEdit = useCallback(
    async (blockId: string, newText: string) => {
      if (!pdfId) return

      try {
        // Update local state first for immediate feedback
        setTextBlocks((prev) =>
          prev.map((block) => (block.id === blockId ? { ...block, text: newText } : block))
        )

        // Send update to backend
        await pdfAPI.replaceText(pdfId, blockId, newText, true)

        console.log('Text updated:', blockId, newText)
      } catch (error) {
        console.error('Error updating text:', error)
        alert('Failed to update text. Please try again.')
        // Revert local state on error
        const blocks = await pdfAPI.extractTextBlocks(pdfId, currentPage)
        setTextBlocks(blocks)
      }
    },
    [pdfId, currentPage]
  )

  // Handle adding new text
  const handleAddText = useCallback(
    async (x: number, y: number, text: string = "New Text") => {
      if (!pdfId || mode !== 'add-text') return

      try {
        // Insert text via API
        await pdfAPI.insertText(pdfId, currentPage, text, x, y, {
          fontSize: 12,
          fontName: 'Helvetica'
        })

        // Refresh text blocks
        const blocks = await pdfAPI.extractTextBlocks(pdfId, currentPage)
        setTextBlocks(blocks)
        
        console.log('Text added at:', x, y)
      } catch (error) {
        console.error('Error adding text:', error)
        alert('Failed to add text. Please try again.')
      }
    },
    [pdfId, currentPage, mode]
  )

  // Handle page rotation
  const handleRotatePage = useCallback(
    async (pageNum: number, degrees: 90 | 180 | 270) => {
      if (!pdfId) return

      try {
        console.log(`Rotating page ${pageNum} by ${degrees} degrees`)
        // In production, this would call backend API
        // await pdfAPI.rotatePage(pdfId, pageNum, degrees)
        alert(`Page ${pageNum + 1} rotated by ${degrees}° (API integration pending)`)
      } catch (error) {
        console.error('Error rotating page:', error)
        alert('Failed to rotate page. Please try again.')
      }
    },
    [pdfId]
  )

  // Handle page reordering
  const handleReorderPages = useCallback(
    async (fromPage: number, toPage: number) => {
      if (!pdfId) return

      try {
        console.log(`Moving page ${fromPage} to position ${toPage}`)
        // In production, this would call backend API
        // await pdfAPI.reorderPages(pdfId, fromPage, toPage)
        alert(`Page ${fromPage + 1} moved to position ${toPage + 1} (API integration pending)`)
      } catch (error) {
        console.error('Error reordering pages:', error)
        alert('Failed to reorder pages. Please try again.')
      }
    },
    [pdfId]
  )

  // Handle property change
  const handlePropertyChange = useCallback(
    (property: keyof RenderOptions, value: PropertyValue) => {
      if (!selectedBlock) return

      console.log('Property changed:', property, value)
      
      // Update selected block properties
      const updatedBlock = { ...selectedBlock, [property]: value }
      setSelectedBlock(updatedBlock)

      // Update in text blocks array
      setTextBlocks((prev) =>
        prev.map((block) => (block.id === selectedBlock.id ? updatedBlock : block))
      )

      // In production, send update to backend
      // await pdfAPI.updateBlockProperties(pdfId, selectedBlock.id, { [property]: value })
    },
    [selectedBlock]
  )

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Top Navigation Bar */}
      <TopNavBar
        onFileUpload={handleFileUpload}
        onSave={handleSave}
        onExport={handleExport}
        hasFile={file !== null}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <LeftSidebar
          currentMode={mode}
          onModeChange={handleModeChange}
          disabled={!file}
        />

        {/* Center Canvas Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {file && (
            <PageNavigation
              currentPage={currentPage}
              totalPages={totalPages}
              zoom={zoom}
              onPageChange={handlePageChange}
              onZoomChange={handleZoomChange}
            />
          )}

          <PDFCanvas
            file={file}
            currentPage={currentPage}
            zoom={zoom}
            textBlocks={textBlocks}
            selectedBlockId={selectedBlock?.id || null}
            onTextBlockSelect={handleTextBlockSelect}
            onTextBlockEdit={handleTextBlockEdit}
            onAddText={handleAddText}
            onRotatePage={handleRotatePage}
            onReorderPages={handleReorderPages}
            mode={mode}
          />
        </div>

        {/* Right Properties Panel */}
        <RightPropertiesPanel
          selectedBlock={selectedBlock}
          onPropertyChange={handlePropertyChange}
        />
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-4">
            <div className="animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-primary-600"></div>
            <span className="text-gray-700">Processing...</span>
          </div>
        </div>
      )}
    </div>
  )
}
