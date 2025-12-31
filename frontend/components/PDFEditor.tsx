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
// import { pdfAPI } from '@/lib/api'

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
      // In a real implementation, this would call the backend API
      // For now, we'll simulate the response
      console.log('File uploaded:', uploadedFile.name)
      
      // Simulate API call delay
      await new Promise((resolve) => setTimeout(resolve, 500))
      
      // In production, the page count would come from backend API
      // For now, set a default
      setTotalPages(1)
      setCurrentPage(0)

      // Simulate PDF ID from backend
      const mockPdfId = `pdf-${Date.now()}`
      setPdfId(mockPdfId)

      // In production, fetch text blocks from backend
      // const blocks = await pdfAPI.extractTextBlocks(mockPdfId)
      // setTextBlocks(blocks)
      
      // For demo, create mock text blocks
      setTextBlocks([])
      
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
      
      // In production, this would export the PDF from backend
      // const blob = await pdfAPI.exportPDF(pdfId)
      // const url = URL.createObjectURL(blob)
      // const a = document.createElement('a')
      // a.href = url
      // a.download = `edited-${file?.name || 'document.pdf'}`
      // a.click()
      // URL.revokeObjectURL(url)
      
      alert('Export functionality will download the edited PDF')
    } catch (error) {
      console.error('Error exporting:', error)
      alert('Failed to export PDF. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [pdfId])

  // Handle mode change
  const handleModeChange = useCallback((newMode: EditorMode) => {
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
        // Update local state
        setTextBlocks((prev) =>
          prev.map((block) => (block.id === blockId ? { ...block, text: newText } : block))
        )

        // In production, send update to backend
        // await pdfAPI.replaceText(pdfId, blockId, newText, true)

        console.log('Text updated:', blockId, newText)
      } catch (error) {
        console.error('Error updating text:', error)
        alert('Failed to update text. Please try again.')
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
