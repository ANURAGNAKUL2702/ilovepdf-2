// Type definitions for PDF Editor

export interface TextBlock {
  id: string
  text: string
  x0: number
  y0: number
  x1: number
  y1: number
  pageNumber: number
  fontName: string
  fontSize: number
  fontFlags: number
  color: string
  lineNumber: number
  blockNumber: number
}

export interface FontInfo {
  name: string
  size: number
  bold: boolean
  italic: boolean
  monospace: boolean
  serif: boolean
  color: string
}

export interface TextAlignment {
  type: 'left' | 'center' | 'right' | 'justified'
  margin: number
}

export interface RenderOptions {
  fontName?: string
  fontSize?: number
  color?: string
  bold?: boolean
  italic?: boolean
  lineSpacing?: number
  alignment?: TextAlignment
}

export interface PDFMetadata {
  pageCount: number
  pageWidth: number
  pageHeight: number
  title?: string
  author?: string
}

export interface EditOperation {
  type: 'insert' | 'replace' | 'delete'
  pageNumber: number
  x?: number
  y?: number
  oldText?: string
  newText?: string
  blockId?: string
  renderOptions?: RenderOptions
}

export interface SpellingError {
  word: string
  startIndex: number
  endIndex: number
  suggestions: string[]
}

export interface ToolType {
  id: string
  name: string
  icon: string
  description: string
}

export type EditorMode = 'view' | 'edit-text' | 'add-text' | 'organize-pages' | 'rotate-pages'

export interface EditorState {
  mode: EditorMode
  currentPage: number
  zoom: number
  selectedTextBlock: TextBlock | null
  textBlocks: TextBlock[]
  editOperations: EditOperation[]
  pdfFile: File | null
  pdfMetadata: PDFMetadata | null
}
