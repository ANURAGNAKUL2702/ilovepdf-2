'use client'

import { TextBlock, RenderOptions } from '@/types'
import { useState } from 'react'

export type PropertyValue = string | number | boolean | { type: string; margin: number }

interface RightPropertiesPanelProps {
  selectedBlock: TextBlock | null
  onPropertyChange: (property: keyof RenderOptions, value: PropertyValue) => void
}

// Available font families for future enhancements
// const FONT_FAMILIES = [
//   'Helvetica',
//   'Times-Roman',
//   'Courier',
//   'Arial',
//   'Georgia',
//   'Verdana',
// ]

const FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 28, 32, 36, 48, 72]

const LINE_SPACINGS = [
  { label: 'Single', value: 1.0 },
  { label: '1.15', value: 1.15 },
  { label: '1.5', value: 1.5 },
  { label: 'Double', value: 2.0 },
]

const ALIGNMENTS = [
  { id: 'left', label: 'Left', icon: '⬅' },
  { id: 'center', label: 'Center', icon: '↔' },
  { id: 'right', label: 'Right', icon: '➡' },
  { id: 'justified', label: 'Justify', icon: '⬌' },
]

export default function RightPropertiesPanel({
  selectedBlock,
  onPropertyChange,
}: RightPropertiesPanelProps) {
  const [fontSize, setFontSize] = useState(selectedBlock?.fontSize || 12)
  const [lineSpacing, setLineSpacing] = useState(1.0)
  const [alignment, setAlignment] = useState('left')

  const handleFontSizeChange = (newSize: number) => {
    setFontSize(newSize)
    onPropertyChange('fontSize', newSize)
  }

  const handleLineSpacingChange = (newSpacing: number) => {
    setLineSpacing(newSpacing)
    onPropertyChange('lineSpacing', newSpacing)
  }

  const handleAlignmentChange = (newAlignment: string) => {
    setAlignment(newAlignment)
    onPropertyChange('alignment', { type: newAlignment, margin: 0 })
  }

  return (
    <aside className="w-70 bg-gray-50 border-l border-gray-200 flex flex-col overflow-y-auto">
      <div className="p-4 border-b border-gray-200 bg-white">
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">
          Properties
        </h2>
      </div>

      {!selectedBlock ? (
        <div className="p-6 text-center">
          <div className="text-gray-400 mb-2">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <p className="text-sm text-gray-500">No text block selected</p>
          <p className="text-xs text-gray-400 mt-2">
            Click on a text block to view and edit its properties
          </p>
        </div>
      ) : (
        <div className="flex-1 p-4 space-y-6">
          {/* Font Family */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2 uppercase tracking-wider">
              Font Family
            </label>
            <input
              type="text"
              value={selectedBlock.fontName}
              readOnly
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md bg-gray-100 text-gray-600 cursor-not-allowed"
              title="Font family is read-only to preserve original styling"
            />
            <p className="text-xs text-gray-500 mt-1">Read-only (preserves original font)</p>
          </div>

          {/* Font Size */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2 uppercase tracking-wider">
              Font Size
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="number"
                value={fontSize}
                onChange={(e) => handleFontSizeChange(Number(e.target.value))}
                min="8"
                max="72"
                className="w-20 px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <input
                type="range"
                value={fontSize}
                onChange={(e) => handleFontSizeChange(Number(e.target.value))}
                min="8"
                max="72"
                className="flex-1"
              />
            </div>
            <div className="flex flex-wrap gap-1 mt-2">
              {FONT_SIZES.map((size) => (
                <button
                  key={size}
                  onClick={() => handleFontSizeChange(size)}
                  className={`px-2 py-1 text-xs rounded ${
                    fontSize === size
                      ? 'bg-primary-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>

          {/* Line Spacing */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2 uppercase tracking-wider">
              Line Spacing
            </label>
            <select
              value={lineSpacing}
              onChange={(e) => handleLineSpacingChange(Number(e.target.value))}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              {LINE_SPACINGS.map((spacing) => (
                <option key={spacing.value} value={spacing.value}>
                  {spacing.label}
                </option>
              ))}
            </select>
          </div>

          {/* Text Alignment */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-2 uppercase tracking-wider">
              Text Alignment
            </label>
            <div className="grid grid-cols-2 gap-2">
              {ALIGNMENTS.map((align) => (
                <button
                  key={align.id}
                  onClick={() => handleAlignmentChange(align.id)}
                  className={`px-3 py-2 text-sm rounded-md border flex items-center justify-center space-x-2 ${
                    alignment === align.id
                      ? 'bg-primary-600 text-white border-primary-600'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <span>{align.icon}</span>
                  <span>{align.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Selected Block Info */}
          <div className="pt-6 border-t border-gray-200">
            <h3 className="text-xs font-medium text-gray-700 mb-3 uppercase tracking-wider">
              Block Information
            </h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-500">Page:</span>
                <span className="text-gray-700 font-medium">{selectedBlock.pageNumber + 1}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Position:</span>
                <span className="text-gray-700 font-medium">
                  ({Math.round(selectedBlock.x0)}, {Math.round(selectedBlock.y0)})
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Size:</span>
                <span className="text-gray-700 font-medium">
                  {Math.round(selectedBlock.x1 - selectedBlock.x0)} ×{' '}
                  {Math.round(selectedBlock.y1 - selectedBlock.y0)}
                </span>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-200">
                <span className="text-gray-500 block mb-1">Text Content:</span>
                <div className="bg-gray-100 p-2 rounded text-gray-700 max-h-24 overflow-y-auto">
                  {selectedBlock.text}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
