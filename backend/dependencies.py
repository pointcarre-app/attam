"""
Dead simple dependency manager for templates
"""

from typing import Literal, Union


def get_deps_from(from_: Union[Literal["local"], Literal["cdn"]]):
    """
    Returns dict with CDN or relative URLs based on environment
    Call this in your templates: {{ get_deps().tailwind_css }}
    """

    # Check if we're in Capacitor mode

    if from_ == "local":
        # Relative URLs for Capacitor
        return {
            # CSS
            # TODO:sel So actually need internet for google fonts
            "google_fonts": "/static/dependencies/google_fonts.css",
            "google_fonts_pan": "/static/dependencies/google_fonts_pan.css",
            "open_dyslexic_css": "/static/dependencies/open_dyslexic_regular.css",
            "tailwind_js": "/static/dependencies/tailwindcssbrowser@4.js",
            "daisyui_css": "/static/dependencies/daisyui@5.css",
            "daisyui_themes_css": "/static/dependencies/daisyUI@5themes.css",
            "app_root_css": "/static/dependencies/root.css",
            "app_global_css": "/static/dependencies/global.css",
            # "app_dock_css": "/static/common/css/dock.css",
            "entry_js": "/static/ganger/entry.js",
            "ganger_js": "/static/ganger/ganger.js",
            "courses_js": "/static/ganger/courses.js",
            "katex_css": "/static/dependencies/katex.css",
            "katex_js": "/static/dependencies/katex.js",
            "katex_autorender_js": "/static/dependencies/katex-autorender.js",
            # "app_styles_css": "/static/common/css/styles.css",
        }
    elif from_ == "cdn":
        # CDN URLs for production
        return {
            # CSS
            "google_fonts": "https://fonts.googleapis.com/css2?family=Lexend:wght@300..900&family=Outfit:wght@300..900&family=EB+Garamond:ital,wght@0,400..800;1,400..800&family=Dancing+Script:wght@400..700&family=Lora:ital,wght@0,400..700;1,400..700&family=JetBrains+Mono:ital,wght@0,400..800;1,400..800&display=swap",
            "google_fonts_pan": "https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700&family=Crimson+Text:wght@400;600&family=Inter:wght@400;600;700&family=Lora:wght@400;600&family=Rajdhani:wght@400;600;700&family=Merriweather:wght@400;700&family=Work+Sans:wght@400;600;700&family=Source+Serif+4:wght@400;600&family=Rubik:wght@400;600;700&family=Spectral:wght@400;600&display=swap",
            "open_dyslexic_css": "https://cdn.jsdelivr.net/npm/open-dyslexic@1.0.3/open-dyslexic-regular.min.css",
            "tailwind_js": "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4",
            "daisyui_css": "https://cdn.jsdelivr.net/npm/daisyui@5",
            "daisyui_themes_css": "https://cdn.jsdelivr.net/npm/daisyui@5/themes.css",
            "app_root_css": "/static/dependencies/root.css",
            "app_global_css": "/static/dependencies/global.css",
            # "app_dock_css": "/static/common/css/dock.css",
            "entry_js": "/static/ganger/entry.js",
            "ganger_js": "/static/ganger/ganger.js",
            "courses_js": "/static/ganger/courses.js",
            "katex_css": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css",
            "katex_js": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js",
            "katex_autorender_js": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js",
            # "app_styles_css": "/static/common/css/styles.css",
        }

    else:
        raise ValueError(f"Invalid source: {from_}")
