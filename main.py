from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import parse_qs


BASE_DIR = Path(__file__).resolve().parent
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
PATIENT_GRAPH_FILES = {
    "biguanides": BASE_DIR / "img" / "biguanides.png",
    "biguanide-dpp4-combos": BASE_DIR / "img" / "biguanide+dpp4_inhibitor_combos.png",
    "dpp4-inhibitors": BASE_DIR / "img" / "dpp4_inhibitors.png",
    "thiazolidinediones": BASE_DIR / "img" / "thiazolidinediones.png",
    "all": BASE_DIR / "img" / "all_medication.png",
}
GLOBAL_GRAPH_FILES = {
    "adherent-global": BASE_DIR / "img" / "adherent_global.png",
    "non-adherent-global": BASE_DIR / "img" / "non-adherent_global.png",
}
IMAGE_FILES = PATIENT_GRAPH_FILES | GLOBAL_GRAPH_FILES
GRAPH_LABELS = {
    "all": "Svi lijekovi",
    "biguanides": "Biguanides",
    "biguanide-dpp4-combos": "Biguanide + DPP4 Inhibitor Combos",
    "dpp4-inhibitors": "DPP4 inhibitors",
    "thiazolidinediones": "Thiazolidinediones",
}
GRAPH_DOT_CLASSES = {
    "all": "dot-red",
    "biguanides": "dot-red",
    "biguanide-dpp4-combos": "dot-red",
    "dpp4-inhibitors": "dot-green",
    "thiazolidinediones": "dot-red",
}
GRAPH_HOVER_TEXT = {
    "thiazolidinediones": "Model povećava vjerojatnost neadherencije jer pacijent pokazuje lošiji prethodni obrazac pokrivenosti terapijom, veće razmake između podizanja lijekova te nepovoljnije kliničke signale poput glukoze i HbA1c-a, što zajedno upućuje na veći rizik neredovitog uzimanja terapije.",
}
PATIENTS = [
    {"id": "ana-kovac", "name": "Ana Kovač", "status": "Neadherentan"},
    {"id": "marko-babic", "name": "Marko Babić", "status": "Neadherentan"},
    {"id": "petra-novak", "name": "Petra Novak", "status": "Adherentan"},
]


def get_patient(patient_id: str):
    for patient in PATIENTS:
        if patient["id"] == patient_id:
            return patient
    return None


def count_patients(status: str) -> int:
    return sum(1 for patient in PATIENTS if patient["status"] == status)


def render_patient_rows() -> str:
    rows = []
    for index, patient in enumerate(PATIENTS):
        dot_class = "dot-green" if patient["status"] == "Adherentan" else "dot-red"
        if index == 0:
            rows.append(
                f"""
                <a class="patient-row" href="/pacijent/{patient["id"]}">
                  <div class="patient-main">
                    <span class="status-dot {dot_class}"></span>
                    <h3>{patient["name"]}</h3>
                  </div>
                </a>
                """
            )
        else:
            rows.append(
                f"""
                <div class="patient-row">
                  <div class="patient-main">
                    <span class="status-dot {dot_class}"></span>
                    <h3>{patient["name"]}</h3>
                  </div>
                </div>
                """
            )
    return "".join(rows)


def render_layout(title: str, body: str, header_title: str | None = None) -> str:
    topbar_title = header_title or title
    return f"""<!DOCTYPE html>
<html lang="hr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    :root {{
      --bg-1: #eef5ef;
      --bg-2: #f4efe6;
      --panel: rgba(255, 255, 255, 0.82);
      --card: rgba(255, 255, 255, 0.94);
      --card-strong: rgba(247, 250, 245, 0.96);
      --text: #202b31;
      --muted: #66717b;
      --line: rgba(32, 43, 49, 0.1);
      --line-strong: rgba(32, 43, 49, 0.16);
      --accent: #2f7d5a;
      --accent-soft: #def0e6;
      --warn: #d9534f;
      --warn-soft: #f7dfdc;
      --shadow: 0 20px 50px rgba(35, 48, 58, 0.1);
      --shadow-soft: 0 12px 28px rgba(35, 48, 58, 0.07);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Georgia, "Times New Roman", serif;
      overflow-x: hidden;
      background:
        radial-gradient(circle at top left, rgba(47, 125, 90, 0.18), transparent 24%),
        radial-gradient(circle at top right, rgba(216, 164, 88, 0.18), transparent 20%),
        radial-gradient(circle at bottom left, rgba(62, 117, 180, 0.08), transparent 26%),
        linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 100%);
    }}

    body::before,
    body::after {{
      content: "";
      position: fixed;
      inset: auto;
      width: 420px;
      height: 420px;
      border-radius: 50%;
      filter: blur(18px);
      opacity: 0.18;
      pointer-events: none;
      z-index: 0;
    }}

    body::before {{
      top: -180px;
      right: -120px;
      background: #2f7d5a;
    }}

    body::after {{
      bottom: -200px;
      left: -140px;
      background: #d8a458;
    }}

    .shell {{
      position: relative;
      z-index: 1;
      max-width: 1140px;
      margin: 0 auto;
      padding: 28px 20px 48px;
    }}

    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;
      margin-bottom: 26px;
    }}

    h1 {{
      margin: 0 0 8px;
      font-size: clamp(2.15rem, 4.4vw, 3.7rem);
      line-height: 0.92;
      letter-spacing: -0.055em;
    }}

    .subtitle,
    .section-copy,
    .detail-copy,
    .back-link {{
      margin: 0;
      color: var(--muted);
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    }}

    .subtitle {{
      display: flex;
      align-items: center;
      gap: 14px;
      flex-wrap: wrap;
      margin-top: 8px;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }}

    .inline-option {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      color: var(--text);
      font-size: 0.94rem;
      font-weight: 700;
    }}

    .graph-legend {{
      display: grid;
      gap: 8px;
      margin-top: 12px;
    }}

    .graph-pill {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin-top: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: var(--card);
      border: 1px solid var(--line);
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      font-size: 0.92rem;
      font-weight: 700;
      color: var(--text);
      box-shadow: var(--shadow-soft);
    }}

    .graph-pill.red {{
      background: var(--warn-soft);
      border-color: rgba(217, 83, 79, 0.2);
    }}

    .graph-pill.green {{
      background: var(--accent-soft);
      border-color: rgba(47, 125, 90, 0.2);
    }}

    .doctor-pill {{
      padding: 12px 18px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.78);
      border: 1px solid rgba(47, 125, 90, 0.14);
      color: var(--accent);
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      font-weight: 700;
      white-space: nowrap;
      box-shadow: var(--shadow-soft);
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid rgba(255, 255, 255, 0.82);
      border-radius: 30px;
      padding: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(14px);
    }}

    .home-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
      margin-bottom: 22px;
    }}

    .home-card {{
      display: block;
      text-decoration: none;
      color: inherit;
      background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(246, 249, 247, 0.92));
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 24px;
      box-shadow: var(--shadow-soft);
      transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
      min-height: 180px;
    }}

    .home-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 18px 38px rgba(35, 48, 58, 0.09);
      border-color: var(--line-strong);
    }}

    .home-card-top {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 14px;
    }}

    .home-card-icon {{
      width: 48px;
      height: 48px;
      border-radius: 16px;
      display: grid;
      place-items: center;
      font-size: 1.25rem;
      background: rgba(47, 125, 90, 0.1);
      color: var(--accent);
    }}

    .home-card-title {{
      margin: 0;
      font-size: 1.2rem;
    }}

    .home-card-copy {{
      margin: 0;
      color: var(--muted);
      line-height: 1.5;
    }}

    .section-head {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
    }}

    .section-title {{
      margin: 0 0 6px;
      font-size: 1.45rem;
    }}

    .global-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }}

    .global-card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 16px;
    }}

    .list-panel {{
      display: grid;
      gap: 14px;
    }}

    .patient-row {{
      display: block;
      background: var(--card);
      border: 1px solid var(--line);
      border-left: 5px solid transparent;
      border-radius: 22px;
      padding: 18px;
      text-decoration: none;
      color: inherit;
      transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }}

    .patient-row:hover {{
      transform: translateY(-1px);
      box-shadow: 0 14px 30px rgba(35, 48, 58, 0.08);
      border-color: var(--line-strong);
    }}

    .patient-main {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .patient-row h3,
    .detail-title {{
      margin: 0;
      font-size: 1.12rem;
    }}

    .status-dot {{
      width: 14px;
      height: 14px;
      border-radius: 999px;
      flex: 0 0 14px;
      box-shadow: 0 0 0 6px rgba(0, 0, 0, 0.03);
    }}

    .dot-green {{
      background: #2f9e5b;
    }}

    .dot-red {{
      background: var(--warn);
    }}

    .back-link {{
      display: inline-flex;
      margin-bottom: 16px;
      text-decoration: none;
      color: var(--accent);
      font-weight: 700;
    }}

    .detail-head {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;
      margin-bottom: 16px;
    }}

    .graph-picker {{
      max-width: 340px;
      position: relative;
    }}

    .graph-picker label {{
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      font-size: 0.95rem;
      font-weight: 700;
    }}

    .dropdown {{
      position: relative;
    }}

    .dropdown-trigger {{
      width: 100%;
      padding: 13px 14px;
      border-radius: 16px;
      border: 1px solid var(--line-strong);
      background: linear-gradient(180deg, #ffffff 0%, #f9fbf8 100%);
      color: var(--text);
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      box-shadow: var(--shadow-soft);
    }}

    .dropdown-caret {{
      font-size: 0.85rem;
      color: var(--muted);
    }}

    .dropdown-menu {{
      position: absolute;
      top: calc(100% + 8px);
      left: 0;
      right: 0;
      display: none;
      background: white;
      border: 1px solid var(--line-strong);
      border-radius: 18px;
      box-shadow: 0 18px 36px rgba(35, 48, 58, 0.12);
      overflow: hidden;
      z-index: 10;
    }}

    .dropdown.open .dropdown-menu {{
      display: grid;
    }}

    .dropdown-option {{
      width: 100%;
      padding: 12px 14px;
      border: 0;
      background: transparent;
      text-align: left;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--text);
      font: inherit;
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      font-weight: 700;
    }}

    .dropdown-option:hover {{
      background: rgba(216, 241, 226, 0.4);
    }}

    .image-wrap {{
      overflow: hidden;
      border-radius: 24px;
      border: 1px solid var(--line);
      background: white;
      margin-top: 18px;
      box-shadow: var(--shadow-soft);
      padding: 12px;
      position: relative;
    }}

    .image-wrap img {{
      display: block;
      width: 100%;
      max-height: 520px;
      object-fit: contain;
      height: auto;
    }}

    .graph-tooltip {{
      position: absolute;
      inset: auto 16px 16px 16px;
      padding: 14px 16px;
      border-radius: 18px;
      background: rgba(32, 43, 49, 0.88);
      color: white;
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      font-size: 0.95rem;
      line-height: 1.55;
      opacity: 0;
      transform: translateY(8px);
      transition: opacity 160ms ease, transform 160ms ease;
      pointer-events: none;
      box-shadow: 0 16px 36px rgba(0, 0, 0, 0.22);
    }}

    .image-wrap:hover .graph-tooltip {{
      opacity: 1;
      transform: translateY(0);
    }}

    @media (max-width: 720px) {{
      .topbar,
      .detail-head {{
        flex-direction: column;
        align-items: flex-start;
      }}

      .home-grid,
      .global-grid {{
        grid-template-columns: 1fr;
      }}

      .graph-picker {{
        max-width: 100%;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <header class="topbar">
      <div>
        <h1>{topbar_title}</h1>
        <div class="subtitle">
          <span class="legend-item"><span class="status-dot dot-green"></span>Nerizični</span>
          <span class="legend-item"><span class="status-dot dot-red"></span>Rizični</span>
        </div>
      </div>
    </header>
    {body}
  </div>
</body>
</html>
"""


def render_home_page() -> str:
    body = f"""
    <div class="home-grid">
      <a class="home-card" href="/globalno">
        <div class="home-card-top">
          <div class="home-card-icon">G</div>
          <div>
            <h2 class="home-card-title">Globalno</h2>
            <p class="home-card-copy">Otvara pregled globalnih grafova za rizične i nerizične pacijente.</p>
          </div>
        </div>
      </a>

      <a class="home-card" href="/pacijenti">
        <div class="home-card-top">
          <div class="home-card-icon">P</div>
          <div>
            <h2 class="home-card-title">Pacijenti</h2>
            <p class="home-card-copy">Otvara popis pacijenata i njihove podatke.</p>
          </div>
        </div>
      </a>
    </div>
    """
    return render_layout("Početna", body)


def render_global_page() -> str:
    body = """
    <a class="back-link" href="/">← Početna</a>
    <section class="panel">
      <div class="section-head">
        <div>
          <h2 class="section-title">Globalno</h2>
          <p class="section-copy">Pregled globalnih grafova za rizične i nerizične pacijente.</p>
        </div>
      </div>
      <div class="global-grid">
        <article class="global-card">
          <div class="patient-main" style="margin-bottom: 10px;">
            <span class="status-dot dot-green"></span>
            <h3>Nerizični</h3>
          </div>
          <div class="image-wrap" style="margin-top: 0;">
            <img src="/img/adherent-global.png" alt="Globalni graf za nerizične pacijente" />
          </div>
        </article>
        <article class="global-card">
          <div class="patient-main" style="margin-bottom: 10px;">
            <span class="status-dot dot-red"></span>
            <h3>Rizični</h3>
          </div>
          <div class="image-wrap" style="margin-top: 0;">
            <img src="/img/non-adherent-global.png" alt="Globalni graf za rizične pacijente" />
          </div>
        </article>
      </div>
    </section>
    """
    return render_layout("Globalno", body)


def render_patients_page() -> str:
    body = f"""
    <a class="back-link" href="/">← Početna</a>
    <section class="panel">
      <div class="section-head">
        <div>
          <h2 class="section-title">Pacijenti</h2>
        </div>
      </div>
      <div class="list-panel">
        {render_patient_rows()}
      </div>
    </section>
    """
    return render_layout("Pacijenti", body)


def render_patient_page(patient: dict, selected_graph: str) -> str:
    dot_class = "dot-green" if patient["status"] == "Adherentan" else "dot-red"
    graph_label = GRAPH_LABELS[selected_graph]
    graph_tone = "green" if GRAPH_DOT_CLASSES[selected_graph] == "dot-green" else "red"
    graph_hover = GRAPH_HOVER_TEXT.get(selected_graph, "")
    graph_buttons = "".join(
        f'''
        <button type="button" class="dropdown-option" data-graph="{key}">
          <span class="status-dot {GRAPH_DOT_CLASSES[key]}"></span>
          <span>{label}</span>
        </button>
        '''
        for key, label in GRAPH_LABELS.items()
    )
    body = f"""
    <a class="back-link" href="/">← Natrag na popis pacijenata</a>
    <section class="panel" style="padding: 22px; max-width: 980px; margin: 0 auto;">
      <div class="detail-head">
        <div class="patient-main" style="align-items:flex-start; gap:16px;">
          <span class="status-dot {dot_class}" style="margin-top:8px;"></span>
          <div>
            <h2 class="detail-title" style="font-size: clamp(1.5rem, 2.6vw, 2.2rem);">{patient["name"]}</h2>
            <div class="graph-pill {graph_tone}">
              <span class="status-dot {GRAPH_DOT_CLASSES[selected_graph]}"></span>
              <span>{graph_label}</span>
            </div>
            <p class="detail-copy" style="margin-top:6px;">Odabrani podaci za prikaz lijeka i grafa.</p>
          </div>
        </div>
        <div class="graph-picker">
          <label for="graph-select">Odabir lijekova</label>
          <div class="dropdown" id="graph-dropdown">
            <button type="button" class="dropdown-trigger" id="graph-trigger">
              <span id="graph-current">{graph_label}</span>
              <span class="dropdown-caret">▾</span>
            </button>
            <div class="dropdown-menu" id="graph-menu">
              {graph_buttons}
            </div>
          </div>
        </div>
      </div>
      <div class="image-wrap">
        <img src="/img/{selected_graph}.png" alt="Graf {graph_label} za pacijenta {patient["name"]}" />
        {"<div class='graph-tooltip'>" + graph_hover + "</div>" if graph_hover else ""}
      </div>
    </section>
    <script>
      const dropdown = document.getElementById("graph-dropdown");
      const trigger = document.getElementById("graph-trigger");
      const menu = document.getElementById("graph-menu");
      trigger.addEventListener("click", () => {{
        dropdown.classList.toggle("open");
      }});
      menu.querySelectorAll("[data-graph]").forEach((button) => {{
        button.addEventListener("click", () => {{
          const url = new URL(window.location.href);
          url.searchParams.set("graph", button.dataset.graph);
          window.location.href = url.toString();
        }});
      }});
      document.addEventListener("click", (event) => {{
        if (!dropdown.contains(event.target)) {{
          dropdown.classList.remove("open");
        }}
      }});
    </script>
    """
    return render_layout(patient["name"], body, header_title="Podaci pacijenta")


class DemoHandler(BaseHTTPRequestHandler):
    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: Path, content_type: str) -> None:
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_not_found(self) -> None:
        body = b'{"error":"Not found"}'
        self.send_response(404)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html(render_home_page())
            return
        if parsed.path == "/globalno":
            self._send_html(render_global_page())
            return
        if parsed.path == "/pacijenti":
            self._send_html(render_patients_page())
            return
        if parsed.path.startswith("/pacijent/"):
            patient_id = parsed.path.removeprefix("/pacijent/")
            patient = get_patient(patient_id)
            if patient is not None:
                query = parse_qs(parsed.query)
                selected_graph = query.get("graph", ["all"])[0]
                if selected_graph not in PATIENT_GRAPH_FILES:
                    selected_graph = "all"
                self._send_html(render_patient_page(patient, selected_graph))
                return
        if parsed.path.startswith("/img/"):
            graph_key = parsed.path.removeprefix("/img/").removesuffix(".png")
            graph_path = IMAGE_FILES.get(graph_key)
            if graph_path is not None and graph_path.exists():
                self._send_file(graph_path, "image/png")
                return
        self._send_not_found()


def run():
    last_error = None
    for port in range(PORT, PORT + 20):
        try:
            server = HTTPServer((HOST, port), DemoHandler)
        except OSError as exc:
            last_error = exc
            continue
        print(f"AI4Health demo radi na http://{HOST}:{port}")
        server.serve_forever()
        return
    raise last_error or RuntimeError("Nema slobodnog porta")


if __name__ == "__main__":
    run()
