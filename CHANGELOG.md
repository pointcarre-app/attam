# CHANGELOG


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
