# PDF Editor Frontend

A production-grade web application for editing PDFs with advanced text manipulation capabilities.

## Features

- **PDF Upload & Preview**: Upload PDF files and view them page-by-page with high-quality rendering using PDF.js
- **Text Selection & Editing**: Click on text blocks to select and double-click to edit
- **Property Panel**: Adjust font size, line spacing, and text alignment in real-time
- **Page Navigation**: Navigate through multi-page documents with zoom controls
- **Multiple Tools**: View, edit text, add text, organize pages, and rotate pages
- **Responsive Layout**: Three-panel layout (sidebar, canvas, properties) for optimal workflow
- **Layout Preservation**: Maintains original font, spacing, and alignment during edits

## Technology Stack

- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS for precise alignment and responsive design
- **PDF Rendering**: PDF.js for client-side PDF rendering
- **API Communication**: Axios for backend integration
- **State Management**: React hooks for local state management

## Prerequisites

- Node.js 18.0 or higher
- npm or yarn package manager

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables (optional):
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Building for Production

Build the application:
```bash
npm run build
```

Start the production server:
```bash
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles and custom CSS
│   ├── layout.tsx         # Root layout component
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── PDFEditor.tsx     # Main editor orchestrator
│   ├── TopNavBar.tsx     # Top navigation with upload/save/export
│   ├── LeftSidebar.tsx   # Tool selection sidebar
│   ├── PDFCanvas.tsx     # PDF rendering and text overlays
│   ├── PageNavigation.tsx # Page and zoom controls
│   └── RightPropertiesPanel.tsx # Text property controls
├── lib/                   # Utility libraries
│   └── api.ts            # API service layer for backend calls
├── types/                 # TypeScript type definitions
│   └── index.ts          # Shared types and interfaces
├── public/               # Static assets
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── postcss.config.js     # PostCSS configuration
└── next.config.js        # Next.js configuration
```

## Component Hierarchy

```
PDFEditor (Main Orchestrator)
├── TopNavBar
│   ├── Upload Button
│   ├── Save Button
│   └── Export Button
├── LeftSidebar
│   └── Tool Buttons (View, Edit Text, Add Text, etc.)
├── Main Canvas Area
│   ├── PageNavigation (Controls)
│   └── PDFCanvas
│       ├── PDF Rendering Layer (Canvas)
│       └── Text Overlay Layer (Interactive)
└── RightPropertiesPanel
    ├── Font Family (Read-only)
    ├── Font Size Selector
    ├── Line Spacing Selector
    ├── Text Alignment Controls
    └── Block Information Display
```

## User Interaction Flow

### 1. Upload PDF
1. User clicks "Upload PDF" button in top navigation
2. File picker opens, user selects PDF file
3. PDF is uploaded to backend API
4. Backend returns PDF ID and metadata
5. First page is rendered in canvas area

### 2. View and Navigate
1. User can navigate pages using Previous/Next buttons
2. User can jump to specific page using page input
3. User can zoom in/out using zoom controls
4. Canvas updates to show current page at current zoom level

### 3. Select and Edit Text
1. User selects "Edit Text" tool from left sidebar
2. User clicks on text block in canvas
3. Text block is highlighted with blue outline
4. Properties panel shows text block properties
5. User double-clicks to enter edit mode
6. Textarea appears with editable text
7. User edits text, presses Ctrl+Enter or clicks away to save
8. Changes are sent to backend API
9. Canvas updates with new text

### 4. Adjust Properties
1. With text block selected, user can:
   - Adjust font size using slider or preset buttons
   - Change line spacing from dropdown
   - Set text alignment (left, center, right, justified)
2. Properties are updated in real-time
3. Changes are sent to backend API

### 5. Save and Export
1. User clicks "Save" to persist changes
2. User clicks "Export" to download modified PDF
3. Backend generates updated PDF with all edits
4. File is downloaded to user's device

## CSS Strategy for Precision Alignment

### Grid Layout
- Uses CSS Grid with `grid-template-columns: 240px 1fr 280px`
- Fixed widths for sidebars, flexible canvas area
- Ensures consistent layout across screen sizes

### Absolute Positioning for Text Overlays
- Text blocks use `position: absolute` overlaid on canvas
- Coordinates calculated from backend text extraction
- Scaled with zoom level: `position * zoom`
- Maintains pixel-perfect alignment

### Typography Precision
- Font sizes scaled with zoom: `fontSize * zoom`
- Line heights calculated based on line spacing setting
- Text alignment enforced using CSS text-align property

### Responsive Behavior
- Canvas scrolls when content exceeds viewport
- Sidebars maintain fixed width
- Zoom controls allow adaptation to different screen sizes

## API Integration

The frontend communicates with the backend API through the `pdfAPI` service:

### Key API Endpoints

- `POST /api/pdf/upload` - Upload PDF file
- `GET /api/pdf/:id/text-blocks` - Extract text blocks with coordinates
- `GET /api/pdf/:id/metadata` - Get PDF metadata (page count, dimensions)
- `POST /api/pdf/:id/replace-text` - Replace text in a block
- `POST /api/pdf/:id/insert-text` - Insert new text at coordinates
- `DELETE /api/pdf/:id/text-block/:blockId` - Delete text block
- `GET /api/pdf/:id/export` - Export modified PDF
- `POST /api/spell/suggestions` - Get spelling suggestions

### Data Flow

```
Frontend                    Backend API
   |                           |
   |-- Upload PDF ------------>|
   |<-- PDF ID, Metadata ------|
   |                           |
   |-- Extract Text Blocks --->|
   |<-- Text Blocks Array -----|
   |                           |
   |-- User Edits Text ------->|
   |<-- Confirmation ----------|
   |                           |
   |-- Export PDF ------------>|
   |<-- PDF Blob --------------|
```

## Customization

### Adding New Tools

1. Define tool in `LeftSidebar.tsx`:
```typescript
{
  id: 'my-tool',
  name: 'My Tool',
  description: 'Description',
  icon: <YourIconSVG />
}
```

2. Add to `EditorMode` type in `types/index.ts`
3. Implement tool behavior in `PDFEditor.tsx`

### Styling

- Customize colors in `tailwind.config.js`
- Modify global styles in `app/globals.css`
- Component-specific styles use Tailwind utility classes

## Performance Optimization

- PDF.js worker runs in separate thread
- Canvas rendering uses requestAnimationFrame
- Text overlays only rendered for current page
- Lazy loading of pages (future enhancement)

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Limited (desktop experience recommended)

## Known Limitations

- Backend API endpoints are currently mocked for demonstration
- Authentication not implemented (per requirements)
- Payment system not included (per requirements)
- Watermarking not implemented (per requirements)

## Future Enhancements

- Undo/redo functionality
- Collaborative editing
- Advanced text formatting (bold, italic, underline)
- Image insertion and manipulation
- Form field support
- Digital signatures
- Comments and annotations

## Troubleshooting

### PDF.js Worker Error
If you see worker-related errors, ensure the worker URL is correctly configured in `PDFCanvas.tsx`.

### API Connection Issues
Check that the `NEXT_PUBLIC_API_URL` environment variable points to your backend API.

### Build Errors
Clear the `.next` cache and rebuild:
```bash
rm -rf .next
npm run build
```

## Contributing

1. Follow TypeScript best practices
2. Use functional components with hooks
3. Maintain component modularity
4. Add prop types and documentation
5. Test on multiple browsers

## License

Part of the ilovepdf-2 project.
