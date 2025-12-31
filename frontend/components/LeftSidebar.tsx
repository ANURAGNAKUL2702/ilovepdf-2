'use client'

import { EditorMode } from '@/types'
import clsx from 'clsx'

interface Tool {
  id: EditorMode
  name: string
  icon: JSX.Element
  description: string
}

interface LeftSidebarProps {
  currentMode: EditorMode
  onModeChange: (mode: EditorMode) => void
  disabled?: boolean
}

const tools: Tool[] = [
  {
    id: 'view',
    name: 'View',
    description: 'Navigate and view PDF',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
      </svg>
    ),
  },
  {
    id: 'edit-text',
    name: 'Edit Text',
    description: 'Select and edit existing text',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
      </svg>
    ),
  },
  {
    id: 'add-text',
    name: 'Add Text',
    description: 'Insert new text blocks',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
      </svg>
    ),
  },
  {
    id: 'organize-pages',
    name: 'Organize Pages',
    description: 'Reorder and manage pages',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    ),
  },
  {
    id: 'rotate-pages',
    name: 'Rotate Pages',
    description: 'Rotate page orientation',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
  },
]

export default function LeftSidebar({ currentMode, onModeChange, disabled }: LeftSidebarProps) {
  return (
    <aside className="w-60 bg-gray-50 border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Tools</h2>
      </div>

      <nav className="flex-1 p-2 space-y-1">
        {tools.map((tool) => (
          <button
            key={tool.id}
            onClick={() => onModeChange(tool.id)}
            disabled={disabled}
            className={clsx(
              'w-full flex items-start space-x-3 px-3 py-3 rounded-lg transition-all',
              'hover:bg-white hover:shadow-sm',
              currentMode === tool.id
                ? 'bg-primary-50 text-primary-700 border border-primary-200'
                : 'text-gray-700',
              disabled && 'opacity-50 cursor-not-allowed'
            )}
          >
            <div className={clsx(
              'flex-shrink-0 mt-0.5',
              currentMode === tool.id ? 'text-primary-600' : 'text-gray-500'
            )}>
              {tool.icon}
            </div>
            <div className="flex-1 text-left">
              <div className="font-medium text-sm">{tool.name}</div>
              <div className="text-xs text-gray-500 mt-0.5">{tool.description}</div>
            </div>
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="text-xs text-gray-500 space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Ready</span>
          </div>
          <p className="text-gray-400">Select a tool to start editing</p>
        </div>
      </div>
    </aside>
  )
}
