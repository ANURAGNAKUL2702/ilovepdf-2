# PDF Editor Architecture Documentation

## Component Hierarchy Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          PDFEditor (Root)                            │
│  - Manages global state (file, mode, page, zoom, text blocks)       │
│  - Orchestrates communication between all child components           │
│  - Handles API calls to backend                                      │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
┌───────────────────┐ ┌────────────────┐ ┌──────────────────────┐
│   TopNavBar       │ │  Main Content  │ │ RightPropertiesPanel │
│                   │ │    Container   │ │                      │
│ - Upload Button   │ │                │ │ - Font Family        │
│ - Save Button     │ │                │ │ - Font Size          │
│ - Export Button   │ │                │ │ - Line Spacing       │
│ - Product Name    │ │                │ │ - Text Alignment     │
└───────────────────┘ └────┬───────────┘ │ - Block Info         │
                           │             └──────────────────────┘
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
    ┌──────────────┐ ┌─────────────────────────────────┐
    │ LeftSidebar  │ │    Canvas Container             │
    │              │ │                                 │
    │ - View       │ │  ┌───────────────────────────┐  │
    │ - Edit Text  │ │  │    PageNavigation         │  │
    │ - Add Text   │ │  │  - Previous/Next          │  │
    │ - Organize   │ │  │  - Page Input             │  │
    │ - Rotate     │ │  │  - Zoom Controls          │  │
    │ - Status     │ │  └───────────────────────────┘  │
    └──────────────┘ │                                 │
                     │  ┌───────────────────────────┐  │
                     │  │      PDFCanvas            │  │
                     │  │                           │  │
                     │  │  ┌─────────────────────┐  │  │
                     │  │  │ Canvas Layer        │  │  │
                     │  │  │ (PDF Rendering)     │  │  │
                     │  │  └─────────────────────┘  │  │
                     │  │                           │  │
                     │  │  ┌─────────────────────┐  │  │
                     │  │  │ Text Overlay Layer  │  │  │
                     │  │  │ (Interactive Boxes) │  │  │
                     │  │  └─────────────────────┘  │  │
                     │  └───────────────────────────┘  │
                     └─────────────────────────────────┘
```

## Component Responsibilities

### PDFEditor (Main Orchestrator)
**File**: `components/PDFEditor.tsx`

**State Management**:
- `file`: Current PDF file
- `pdfId`: Backend identifier for uploaded PDF
- `mode`: Current editor mode (view, edit-text, add-text, etc.)
- `currentPage`: Current page number (0-indexed)
- `totalPages`: Total number of pages in PDF
- `zoom`: Current zoom level (0.5 - 2.0)
- `textBlocks`: Array of text blocks with coordinates
- `selectedBlock`: Currently selected text block
- `isLoading`: Loading state for async operations

**Responsibilities**:
1. File upload and management
2. Mode switching coordination
3. State synchronization across components
4. API calls to backend
5. Error handling and loading states

**Key Methods**:
- `handleFileUpload()`: Upload PDF and initialize state
- `handleSave()`: Save all edits to backend
- `handleExport()`: Export modified PDF
- `handleModeChange()`: Switch between editing modes
- `handlePageChange()`: Navigate to different page
- `handleZoomChange()`: Adjust zoom level
- `handleTextBlockSelect()`: Select text block for editing
- `handleTextBlockEdit()`: Update text content
- `handlePropertyChange()`: Update text properties

---

### TopNavBar
**File**: `components/TopNavBar.tsx`

**Props**:
- `onFileUpload`: Callback when file is selected
- `onSave`: Callback to save changes
- `onExport`: Callback to export PDF
- `hasFile`: Whether a file is loaded

**Responsibilities**:
1. Display product branding
2. Handle file selection via input
3. Trigger save operation
4. Trigger export operation
5. Show/hide action buttons based on state

**Layout**:
```
┌────────────────────────────────────────────────────────┐
│ PDF Editor | Professional PDF Editing Tool   [Upload] │
│                                              [Save]    │
│                                              [Export]  │
└────────────────────────────────────────────────────────┘
```

---

### LeftSidebar
**File**: `components/LeftSidebar.tsx`

**Props**:
- `currentMode`: Active editor mode
- `onModeChange`: Callback when mode changes
- `disabled`: Whether tools are disabled (no file loaded)

**Tools**:
1. **View**: Navigate and view PDF (default mode)
2. **Edit Text**: Select and modify existing text blocks
3. **Add Text**: Insert new text at clicked position
4. **Organize Pages**: Reorder and manage pages
5. **Rotate Pages**: Rotate page orientation

**Responsibilities**:
1. Display available tools
2. Highlight active tool
3. Disable tools when no file loaded
4. Show status indicator

**Layout**:
```
┌─────────────────┐
│ TOOLS           │
├─────────────────┤
│ 👁  View        │
│ ✏  Edit Text    │ ← Active
│ ➕  Add Text    │
│ 📄  Organize    │
│ 🔄  Rotate      │
├─────────────────┤
│ ● Ready         │
└─────────────────┘
```

---

### PDFCanvas
**File**: `components/PDFCanvas.tsx`

**Props**:
- `file`: PDF file to render
- `currentPage`: Page number to display
- `zoom`: Zoom level for rendering
- `textBlocks`: Array of text blocks for current page
- `selectedBlockId`: ID of selected block
- `onTextBlockSelect`: Callback when block is clicked
- `onTextBlockEdit`: Callback when text is edited
- `mode`: Current editor mode

**Responsibilities**:
1. Render PDF pages using PDF.js
2. Display text block overlays
3. Handle text block selection (click)
4. Handle text block editing (double-click)
5. Show loading state
6. Show empty state when no file

**Rendering Layers**:
1. **Canvas Layer**: PDF.js renders PDF to HTML canvas
2. **Overlay Layer**: Absolutely positioned divs for each text block

**Text Overlay Positioning**:
```typescript
style={{
  position: 'absolute',
  left: `${block.x0 * zoom}px`,
  top: `${block.y0 * zoom}px`,
  width: `${(block.x1 - block.x0) * zoom}px`,
  height: `${(block.y1 - block.y0) * zoom}px`,
}}
```

---

### PageNavigation
**File**: `components/PageNavigation.tsx`

**Props**:
- `currentPage`: Current page number
- `totalPages`: Total number of pages
- `zoom`: Current zoom level
- `onPageChange`: Callback when page changes
- `onZoomChange`: Callback when zoom changes

**Controls**:
1. Previous page button (◀)
2. Page input field (editable)
3. Total pages display (of X)
4. Next page button (▶)
5. Zoom out button (−)
6. Zoom level dropdown
7. Zoom in button (+)
8. Reset zoom button

**Zoom Levels**: 50%, 75%, 100%, 125%, 150%, 200%

**Layout**:
```
┌────────────────────────────────────────────────────────┐
│ ◀ Page [1] of 10 ▶    − [100%] +  Reset   Zoom: 100% │
└────────────────────────────────────────────────────────┘
```

---

### RightPropertiesPanel
**File**: `components/RightPropertiesPanel.tsx`

**Props**:
- `selectedBlock`: Currently selected text block
- `onPropertyChange`: Callback when property is modified

**Controls**:
1. **Font Family**: Read-only input (preserves original font)
2. **Font Size**: Number input + slider + preset buttons
3. **Line Spacing**: Dropdown (Single, 1.15, 1.5, Double)
4. **Text Alignment**: Buttons (Left, Center, Right, Justified)
5. **Block Info**: Display position, size, content

**Layout**:
```
┌─────────────────────┐
│ PROPERTIES          │
├─────────────────────┤
│ Font Family         │
│ [Helvetica    ] 🔒  │
│                     │
│ Font Size           │
│ [12] ═══════●═══    │
│ [8][10][12][14]...  │
│                     │
│ Line Spacing        │
│ [Single      ▼]     │
│                     │
│ Text Alignment      │
│ [⬅ Left][Center]   │
│ [Right][Justify]    │
│                     │
│ Block Information   │
│ Page: 1             │
│ Position: (100, 50) │
│ Size: 200 × 20      │
│ Text: "Sample..."   │
└─────────────────────┘
```

---

## Data Flow Architecture

### 1. File Upload Flow
```
User Action → TopNavBar → PDFEditor → Backend API
                                    ↓
                          Response (PDF ID, Metadata)
                                    ↓
                        Update State (file, pdfId, totalPages)
                                    ↓
                          PDFCanvas renders first page
```

### 2. Text Selection Flow
```
User Click → PDFCanvas (text overlay)
                ↓
        onTextBlockSelect(block)
                ↓
        PDFEditor updates selectedBlock state
                ↓
    ┌───────────┴───────────┐
    ↓                       ↓
PDFCanvas shows         RightPropertiesPanel
selection highlight     displays block properties
```

### 3. Text Editing Flow
```
User Double-Click → PDFCanvas
                        ↓
            Edit mode activated (textarea)
                        ↓
            User edits text
                        ↓
        User presses Ctrl+Enter or clicks away
                        ↓
            onTextBlockEdit(blockId, newText)
                        ↓
        PDFEditor updates local state
                        ↓
        API call to save change
                        ↓
        Backend persists change
```

### 4. Property Change Flow
```
User adjusts property → RightPropertiesPanel
                              ↓
                    onPropertyChange(property, value)
                              ↓
                    PDFEditor updates state
                              ↓
                ┌─────────────┴─────────────┐
                ↓                           ↓
        Updates selectedBlock      Updates textBlocks array
                ↓                           ↓
        API call to backend         PDFCanvas re-renders
```

---

## API Integration Layer

### API Service (`lib/api.ts`)

**Class**: `PDFEditorAPI`

**Methods**:
- `uploadPDF(file)`: Upload PDF and get ID
- `extractTextBlocks(pdfId, page?)`: Get text blocks
- `getPDFMetadata(pdfId)`: Get PDF info
- `checkSpelling(pdfId, page?)`: Check spelling
- `replaceText(pdfId, blockId, newText)`: Replace text
- `insertText(pdfId, page, text, x, y, options)`: Insert text
- `deleteText(pdfId, blockId)`: Delete text
- `exportPDF(pdfId)`: Download modified PDF
- `rotatePage(pdfId, page, rotation)`: Rotate page

**Configuration**:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
```

---

## Type System

### Core Types (`types/index.ts`)

**TextBlock**:
```typescript
interface TextBlock {
  id: string              // Unique identifier
  text: string           // Text content
  x0, y0, x1, y1: number // Bounding box coordinates
  pageNumber: number     // Page index (0-based)
  fontName: string       // Font family
  fontSize: number       // Font size in points
  fontFlags: number      // Bold, italic flags
  color: string          // Text color
  lineNumber: number     // Line number in page
  blockNumber: number    // Block number in page
}
```

**RenderOptions**:
```typescript
interface RenderOptions {
  fontName?: string
  fontSize?: number
  color?: string
  bold?: boolean
  italic?: boolean
  lineSpacing?: number
  alignment?: TextAlignment
}
```

**EditorState**:
```typescript
interface EditorState {
  mode: EditorMode
  currentPage: number
  zoom: number
  selectedTextBlock: TextBlock | null
  textBlocks: TextBlock[]
  editOperations: EditOperation[]
  pdfFile: File | null
  pdfMetadata: PDFMetadata | null
}
```

---

## CSS Architecture

### Layout Strategy

**Three-Column Grid**:
```css
.editor-layout {
  display: grid;
  grid-template-columns: 240px 1fr 280px;
  height: 100vh;
}
```

**Responsive Considerations**:
- Fixed sidebar widths for tool consistency
- Flexible canvas area adapts to remaining space
- Scrollable canvas when content exceeds viewport

### Text Overlay Precision

**Absolute Positioning**:
```css
.text-overlay {
  position: absolute;
  cursor: text;
  transition: background-color 0.2s;
}
```

**Hover State**:
```css
.text-overlay:hover {
  background-color: rgba(59, 130, 246, 0.1);
}
```

**Selected State**:
```css
.text-overlay.selected {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
  background-color: rgba(59, 130, 246, 0.1);
}
```

### Tailwind Configuration

**Custom Grid**:
```javascript
gridTemplateColumns: {
  'editor': '240px 1fr 280px',
}
```

**Custom Colors**:
```javascript
colors: {
  primary: {
    50: '#f0f9ff',
    600: '#0ea5e9',
    700: '#0369a1',
  }
}
```

---

## Event Flow Summary

### Upload → Preview → Select → Edit → Save

```
┌─────────────┐
│   Upload    │ User clicks Upload button
│    PDF      │ File picker opens
└──────┬──────┘ User selects PDF file
       ↓
┌─────────────┐
│   Preview   │ PDF rendered to canvas
│    Page     │ Text blocks overlaid
└──────┬──────┘ Page navigation available
       ↓
┌─────────────┐
│   Select    │ User clicks text block
│    Text     │ Properties panel updates
└──────┬──────┘ Block highlighted
       ↓
┌─────────────┐
│    Edit     │ User double-clicks block
│    Text     │ Textarea appears
└──────┬──────┘ User edits and saves
       ↓
┌─────────────┐
│    Save     │ Changes sent to backend
│   Export    │ Modified PDF generated
└─────────────┘ User downloads file
```

---

## Performance Considerations

1. **PDF.js Worker**: Runs in separate thread to prevent UI blocking
2. **Canvas Rendering**: Uses hardware-accelerated canvas API
3. **Lazy Rendering**: Only current page rendered (others on-demand)
4. **Text Overlay Filtering**: Only show overlays for current page
5. **Debounced API Calls**: Batch property updates to reduce requests
6. **Memoization**: React.memo for components that don't need frequent updates

---

## Security Considerations

1. **File Validation**: Only accept PDF MIME type
2. **Size Limits**: Enforce max file size (configured on backend)
3. **CORS**: Properly configured for API requests
4. **XSS Prevention**: All text content sanitized before rendering
5. **HTTPS**: Use secure connections in production

---

## Accessibility Features

1. **Keyboard Navigation**: Tab through tools and controls
2. **ARIA Labels**: Screen reader support for buttons
3. **Focus Indicators**: Visible focus states for keyboard users
4. **Alt Text**: Descriptive text for icons
5. **Color Contrast**: WCAG AA compliant color ratios

---

## Testing Strategy

### Unit Tests
- Test individual component rendering
- Test event handlers and callbacks
- Test API service methods
- Test type utilities

### Integration Tests
- Test file upload flow
- Test text selection and editing
- Test page navigation
- Test property changes
- Test save and export

### E2E Tests
- Test complete user workflows
- Test error scenarios
- Test browser compatibility
- Test responsive behavior

---

## Deployment

### Environment Variables
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

### Build Command
```bash
npm run build
```

### Deployment Targets
- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify
- Docker container
- Traditional web server (nginx, Apache)

---

This architecture provides a solid foundation for a production-grade PDF editing application with clean separation of concerns, maintainable code structure, and excellent user experience.
