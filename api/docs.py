from __future__ import annotations

from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse


DOCS_THEME = """
<style>
  :root {
    color-scheme: light;
    --docs-bg: #f5f7f6;
    --docs-surface: #ffffff;
    --docs-soft: #edf1ef;
    --docs-text: #15231d;
    --docs-muted: #64736c;
    --docs-line: #dfe6e2;
    --docs-brand: #176b4d;
  }
  html[data-theme="dark"] {
    color-scheme: dark;
    --docs-bg: #08110d;
    --docs-surface: #111c17;
    --docs-soft: #1a2922;
    --docs-text: #edf7f1;
    --docs-muted: #91a59b;
    --docs-line: #26382f;
    --docs-brand: #56c894;
  }
  body { margin: 0; background: var(--docs-bg); }
  .swagger-ui { color: var(--docs-text); }
  .swagger-ui .topbar { background: #0f5139; }
  html[data-theme="dark"] .swagger-ui .topbar { background: #07110c; }
  .swagger-ui .info .title,
  .swagger-ui .info p,
  .swagger-ui .info li,
  .swagger-ui .info table,
  .swagger-ui .opblock-tag,
  .swagger-ui .opblock .opblock-summary-description,
  .swagger-ui .opblock-description-wrapper p,
  .swagger-ui .parameter__name,
  .swagger-ui .parameter__type,
  .swagger-ui .response-col_status,
  .swagger-ui .response-col_description,
  .swagger-ui .responses-inner h4,
  .swagger-ui .responses-inner h5,
  .swagger-ui .model-title,
  .swagger-ui .model,
  .swagger-ui label,
  .swagger-ui table thead tr td,
  .swagger-ui table thead tr th {
    color: var(--docs-text);
  }
  .swagger-ui .info a,
  .swagger-ui .model-toggle,
  .swagger-ui .expand-operation {
    color: var(--docs-brand);
  }
  .swagger-ui .scheme-container,
  .swagger-ui section.models,
  .swagger-ui .model-container {
    background: var(--docs-surface);
    box-shadow: none;
  }
  .swagger-ui .scheme-container,
  .swagger-ui section.models,
  .swagger-ui .opblock-tag,
  .swagger-ui .model-container {
    border-color: var(--docs-line);
  }
  .swagger-ui input,
  .swagger-ui select,
  .swagger-ui textarea {
    color: var(--docs-text);
    border-color: var(--docs-line);
    background: var(--docs-surface);
  }
  .swagger-ui .btn {
    color: var(--docs-text);
    border-color: var(--docs-line);
  }
  .swagger-ui .btn.authorize {
    color: var(--docs-brand);
    border-color: var(--docs-brand);
  }
  html[data-theme="dark"] .swagger-ui svg {
    fill: var(--docs-text);
  }
  .docs-home {
    position: fixed;
    right: 18px;
    bottom: 18px;
    z-index: 20;
    padding: 10px 14px;
    border: 1px solid var(--docs-line);
    border-radius: 999px;
    color: white;
    background: var(--docs-brand);
    box-shadow: 0 10px 30px rgba(0, 0, 0, .18);
    font: 700 12px system-ui, sans-serif;
    text-decoration: none;
  }
</style>
<script>
  (() => {
    const saved = localStorage.getItem("vispection_theme");
    const preferred = matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    document.documentElement.dataset.theme = saved || preferred;
  })();
</script>
"""


def themed_swagger_ui(openapi_url: str, title: str) -> HTMLResponse:
    swagger = get_swagger_ui_html(openapi_url=openapi_url, title=title)
    content = swagger.body.decode("utf-8")
    content = content.replace("</head>", f"{DOCS_THEME}</head>")
    content = content.replace(
        "</body>",
        '<a class="docs-home" href="/">← Ana sayfa</a></body>',
    )
    return HTMLResponse(content=content)
