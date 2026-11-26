# build.py
import json
import os
import sys

# Ensure generator package can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator.css_styles import CSS_CONTENT
from generator.svg_icons import SVG_PIECES, UI_ICONS
from generator.js_engine import JS_ENGINE_CONTENT
from generator.js_managers import JS_MANAGERS_CONTENT
from generator.js_ui import JS_UI_CONTENT
from generator.html_layout import get_html_layout

def build():
    svg_pieces_json = json.dumps(SVG_PIECES)
    ui_icons_json = json.dumps(UI_ICONS)

    html_content = get_html_layout(
        css_content=CSS_CONTENT,
        js_engine=JS_ENGINE_CONTENT,
        js_managers=JS_MANAGERS_CONTENT,
        js_ui=JS_UI_CONTENT,
        svg_pieces_json=svg_pieces_json,
        ui_icons_json=ui_icons_json
    )

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "checkers_level_creator.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    file_size_kb = len(html_content) / 1024
    print(f"Successfully generated '{output_path}' ({file_size_kb:.2f} KB)")
    return output_path

if __name__ == "__main__":
    build()

