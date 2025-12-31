import axios, { AxiosInstance } from 'axios'
import { TextBlock, PDFMetadata, RenderOptions, SpellingError } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

class PDFEditorAPI {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  /**
   * Upload a PDF file and get its metadata
   */
  async uploadPDF(file: File): Promise<{ id: string; metadata: PDFMetadata }> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await this.client.post('/pdf/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  }

  /**
   * Extract text blocks from a PDF
   */
  async extractTextBlocks(pdfId: string, pageNumber?: number): Promise<TextBlock[]> {
    const params = pageNumber !== undefined ? { page: pageNumber } : {}
    const response = await this.client.get(`/pdf/${pdfId}/text-blocks`, { params })
    return response.data.textBlocks
  }

  /**
   * Get PDF metadata
   */
  async getPDFMetadata(pdfId: string): Promise<PDFMetadata> {
    const response = await this.client.get(`/pdf/${pdfId}/metadata`)
    return response.data
  }

  /**
   * Check spelling in the PDF
   */
  async checkSpelling(
    pdfId: string,
    pageNumber?: number
  ): Promise<{ [blockId: string]: SpellingError[] }> {
    const params = pageNumber !== undefined ? { page: pageNumber } : {}
    const response = await this.client.post(`/pdf/${pdfId}/check-spelling`, {}, { params })
    return response.data.errors
  }

  /**
   * Get spelling suggestions for a word
   */
  async getSpellingSuggestions(word: string): Promise<string[]> {
    const response = await this.client.post('/spell/suggestions', { word })
    return response.data.suggestions
  }

  /**
   * Replace text in the PDF
   */
  async replaceText(
    pdfId: string,
    blockId: string,
    newText: string,
    preserveStyle: boolean = true
  ): Promise<{ success: boolean }> {
    const response = await this.client.post(`/pdf/${pdfId}/replace-text`, {
      blockId,
      newText,
      preserveStyle,
    })
    return response.data
  }

  /**
   * Insert new text in the PDF
   */
  async insertText(
    pdfId: string,
    pageNumber: number,
    text: string,
    x: number,
    y: number,
    options?: RenderOptions
  ): Promise<{ success: boolean }> {
    const response = await this.client.post(`/pdf/${pdfId}/insert-text`, {
      pageNumber,
      text,
      x,
      y,
      options,
    })
    return response.data
  }

  /**
   * Delete a text block
   */
  async deleteText(pdfId: string, blockId: string): Promise<{ success: boolean }> {
    const response = await this.client.delete(`/pdf/${pdfId}/text-block/${blockId}`)
    return response.data
  }

  /**
   * Save and download the modified PDF
   */
  async exportPDF(pdfId: string): Promise<Blob> {
    const response = await this.client.get(`/pdf/${pdfId}/export`, {
      responseType: 'blob',
    })
    return response.data
  }

  /**
   * Get page dimensions
   */
  async getPageDimensions(
    pdfId: string,
    pageNumber: number
  ): Promise<{ width: number; height: number }> {
    const response = await this.client.get(`/pdf/${pdfId}/page/${pageNumber}/dimensions`)
    return response.data
  }

  /**
   * Rotate page
   */
  async rotatePage(
    pdfId: string,
    pageNumber: number,
    rotation: number
  ): Promise<{ success: boolean }> {
    const response = await this.client.post(`/pdf/${pdfId}/page/${pageNumber}/rotate`, {
      rotation,
    })
    return response.data
  }
}

export const pdfAPI = new PDFEditorAPI()
