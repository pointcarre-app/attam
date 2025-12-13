# CHANGELOG


## v0.0.3

- **Multi-Format File Support**
    - Extension-based routing for different file types
    - Support for `.md`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
    - Graceful handling of unsupported file types

- **Image Viewer**
    - New `image_viewer.html` template for image display
    - Centered, responsive image viewing with max-height constraints
    - Image metadata display (filename, path, format)
    - DaisyUI stats component for file information

- **Static File Management**
    - Updated lifespan to copy `trames/` folder to `backend/static/`
    - Automatic synchronization of trames on server startup
    - Images and files served through FastAPI static mount

- **Routing Improvements**
    - File extension detection via `Path.suffix`
    - Clean separation of markdown and image handling logic
    - Extensible architecture for adding new file types


## v0.0.2

- **Architecture Refactor**
    - Abstracted piece rendering logic from templates to Python
    - Created `prepare_piece_for_rendering()` and `prepare_trame_for_rendering()` functions
    - Modular piece templates in `backend/templates/pieces/`
        - `title.html`, `paragraph.html`, `unordered_list.html`
        - `code.html`, `table.html`, `unknown.html`
    - Created `_rendered_content.html` partial template for reusable content rendering

- **Dynamic Markdown Editor**
    - Two-column layout: markdown source (left) + rendered preview (right)
    - Integrated SimpleMDE markdown editor (read-only mode)
    - Responsive grid layout (stacks on mobile, side-by-side on desktop)
    
- **Live Processing**
    - `POST /trame/process` endpoint for dynamic markdown processing
    - Temporary file handling with context managers
    - Returns rendered HTML partial for dynamic content replacement
    - Real-time preview updates via JavaScript

- **UI Improvements**
    - DaisyUI toast notifications (success/error)
    - Process button with visual feedback
    - Auto-dismissing toasts with fade animations
    - Improved template maintainability

- **Technical**
    - djlint formatting directives for JavaScript blocks
    - Separated concerns: Python logic vs template rendering
    - Clean namespace for global JavaScript objects (cmEditor*, mdEditor)


## v0.0.1

- Python 3.13.7
    - FastAPI 0.118.0 
    - Pydantic 2.12.5 
- Core FastAPI setup
    - `/` inline HTML welcome page
    - `/health` health check endpoint
    - `/template` Jinja2 template demo with index.html
- Trame system (markdown reader)
    - `/trame/path/{trame_path:path}` dynamic markdown rendering
    - `/trame/debug` debug view for trame attributes
    - Responsive trame.html template (DaisyUI + Tailwind)
    - Support for titles, paragraphs, lists, code blocks, tables
- Dependencies manager (local/CDN)
    - Google Fonts, Open Dyslexic, Tailwind, DaisyUI, KaTeX
- Static files served at `/static`
