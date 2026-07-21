"""OpsPilot AI: small browser demo with deterministic demo mode and OpenAI mode."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from openai import OpenAI

HOST = os.getenv("OPSPILOT_HOST", "127.0.0.1")
PORT = int(os.getenv("OPSPILOT_PORT", "8000"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")

DEMO_PROCEDURE = Path(__file__).with_name("example_procedure.md").read_text(encoding="utf-8")


def demo_plan(procedure: str) -> dict:
    """Return a safe, transparent sample result without making an API call."""
    return {
        "objective": "Avaliar a vibração anormal da bomba e definir a próxima ação segura.",
        "prerequisites": [
            "Confirmar autorização de acesso e condição segura do equipamento.",
            "Consultar o procedimento aprovado e o limite de vibração aplicável ao local.",
            "Usar os EPIs e instrumentos previstos para a inspeção.",
        ],
        "checklist": [
            {"step": "Isolar ou proteger a área conforme o procedimento local.", "status": "A revisar"},
            {"step": "Inspecionar visualmente a bomba e registrar ruídos, vazamentos e vibração.", "status": "A revisar"},
            {"step": "Medir e comparar a vibração com o limite aprovado.", "status": "A revisar"},
            {"step": "Registrar evidências e comunicar a condição ao responsável.", "status": "A revisar"},
        ],
        "risks": [
            "Não executar a inspeção se houver risco de contato com partes móveis ou energia não isolada.",
            "Não declarar normalidade sem consultar o limite aprovado do equipamento.",
        ],
        "verification": [
            "Evidência registrada: leitura, horário, equipamento e condição observada.",
            "Responsável confirma se a bomba pode retornar à operação ou precisa de intervenção.",
        ],
        "escalation": "Se a vibração permanecer acima do limite aprovado, interromper a operação conforme o procedimento e escalar para manutenção/engenharia.",
        "source_note": f"Resultado de demonstração baseado no texto fornecido ({len(procedure)} caracteres).",
    }


def ai_plan(procedure: str) -> dict:
    if not os.getenv("OPENAI_API_KEY"):
        return demo_plan(procedure)

    client = OpenAI()
    response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": (
                    "You are OpsPilot AI. Transform technical procedures into a safe, "
                    "reviewable operations plan. Return only valid JSON with keys "
                    "objective, prerequisites, checklist, risks, verification, escalation. "
                    "Checklist must be an array of objects with step and status. "
                    "Do not invent unavailable facts; mark uncertainty for human review."
                ),
            },
            {"role": "user", "content": procedure},
        ],
    )
    result = json.loads(response.output_text)
    result["source_note"] = f"Gerado por {MODEL}; revisão humana obrigatória."
    return result


PAGE = r"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>OpsPilot AI</title>
  <style>
    :root { --ink:#162235; --muted:#66758a; --line:#dce5ef; --blue:#1769e0; --soft:#f5f8fc; --green:#16794a; }
    * { box-sizing:border-box; } body { margin:0; color:var(--ink); font:15px/1.5 Inter,Segoe UI,Arial,sans-serif; background:linear-gradient(135deg,#eef5ff,#f8fbff 55%,#f1faf7); }
    header { padding:28px max(22px, calc((100% - 1120px)/2)); display:flex; justify-content:space-between; align-items:center; }
    .brand { font-weight:800; font-size:22px; letter-spacing:-.4px; } .brand span { color:var(--blue); } .pill { color:var(--green); background:#e7f7ee; padding:7px 12px; border-radius:999px; font-size:12px; font-weight:700; } .teleprompter-link { color:#fff; background:var(--blue); padding:9px 13px; border-radius:9px; text-decoration:none; font-weight:800; font-size:13px; }
    main { max-width:1120px; margin:12px auto 60px; padding:0 22px; } h1 { max-width:760px; font-size:42px; line-height:1.08; letter-spacing:-1.5px; margin:28px 0 12px; } .lead { max-width:720px; color:var(--muted); font-size:17px; margin-bottom:28px; }
    .grid { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:20px; align-items:start; } .card { background:#fff; border:1px solid var(--line); border-radius:18px; padding:22px; box-shadow:0 12px 30px #1d4e8910; } h2 { margin:0 0 8px; font-size:18px; } label { display:block; color:var(--muted); font-size:13px; font-weight:700; margin:14px 0 7px; } textarea { width:100%; min-height:245px; resize:vertical; border:1px solid var(--line); border-radius:12px; padding:13px; font:14px/1.5 inherit; color:var(--ink); } textarea:focus { outline:3px solid #1769e020; border-color:var(--blue); }
    .actions { display:flex; gap:10px; margin-top:14px; align-items:center; } button { border:0; border-radius:10px; padding:11px 16px; font-weight:800; cursor:pointer; } .primary { background:var(--blue); color:#fff; } .secondary { background:#edf3fa; color:var(--ink); } button:disabled { opacity:.6; cursor:wait; } .hint { color:var(--muted); font-size:12px; }
    .empty { color:var(--muted); border:1px dashed var(--line); border-radius:12px; padding:24px; text-align:center; } .result { display:none; } .result.visible { display:block; } .section { margin-top:18px; } .section h3 { font-size:13px; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); margin:0 0 8px; } ul { margin:0; padding-left:20px; } li { margin:7px 0; } .check { display:flex; gap:9px; align-items:flex-start; padding:9px 0; border-bottom:1px solid #edf1f5; } .check input { margin-top:5px; accent-color:var(--blue); } .status { color:var(--muted); font-size:12px; margin-left:auto; white-space:nowrap; } .escalate { background:#fff7e6; border:1px solid #f0d28b; border-radius:12px; padding:12px; } .note { color:var(--muted); font-size:12px; margin-top:18px; }
    @media (max-width:800px) { h1 { font-size:34px; } .grid { grid-template-columns:1fr; } }
  </style>
</head>
<body>
  <header><div class="brand"><span>Ops</span>Pilot AI</div><div><a class="teleprompter-link" href="/teleprompter">Abrir teleprompter</a> <span class="pill">Human review required</span></div></header>
  <main>
    <h1>De procedimento técnico a plano de ação.</h1>
    <p class="lead">Cole um procedimento, incidente ou nota de manutenção. O OpsPilot organiza o contexto em checklist, riscos, verificação e escalonamento.</p>
    <div class="grid">
      <section class="card">
        <h2>1. Contexto operacional</h2>
        <label for="procedure">Procedimento ou incidente</label>
        <textarea id="procedure"></textarea>
        <div class="actions"><button class="primary" id="generate">Gerar plano</button><button class="secondary" id="load">Carregar exemplo</button></div>
        <div class="hint" id="mode">Modo demo: nenhum documento é enviado.</div>
      </section>
      <section class="card">
        <h2>2. Plano revisável</h2>
        <div class="empty" id="empty">O plano aparecerá aqui depois da análise.</div>
        <div class="result" id="result"></div>
      </section>
    </div>
  </main>
  <script>
    const procedure = document.querySelector('#procedure');
    const result = document.querySelector('#result'); const empty = document.querySelector('#empty'); const generate = document.querySelector('#generate');
    const example = %EXAMPLE%; procedure.value = example;
    document.querySelector('#load').onclick = () => procedure.value = example;
    const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
    function list(items) { return `<ul>${(items || []).map(item => `<li>${esc(typeof item === 'string' ? item : item.step)}</li>`).join('')}</ul>`; }
    function render(plan) {
      const checks = (plan.checklist || []).map((item, i) => `<label class="check"><input type="checkbox" id="c${i}"><span>${esc(item.step || item)}</span><span class="status">${esc(item.status || 'A revisar')}</span></label>`).join('');
      result.innerHTML = `<div><strong>${esc(plan.objective)}</strong></div><div class="section"><h3>Pré-requisitos</h3>${list(plan.prerequisites)}</div><div class="section"><h3>Checklist executável</h3>${checks}</div><div class="section"><h3>Riscos</h3>${list(plan.risks)}</div><div class="section"><h3>Verificação</h3>${list(plan.verification)}</div><div class="section"><h3>Escalonamento</h3><div class="escalate">${esc(plan.escalation)}</div></div><div class="note">${esc(plan.source_note)}</div>`;
      empty.style.display='none'; result.classList.add('visible');
    }
    generate.onclick = async () => { if (!procedure.value.trim()) return; generate.disabled=true; generate.textContent='Analisando…'; try { const r=await fetch('/api/plan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({procedure:procedure.value})}); const data=await r.json(); if(!r.ok) throw new Error(data.error); render(data); document.querySelector('#mode').textContent=data.source_note.includes('demonstração')?'Modo demo: resultado local para gravação.':'Modo OpenAI: revisão humana obrigatória.'; } catch(e) { result.innerHTML=`<div class="escalate">Erro: ${esc(e.message)}</div>`; empty.style.display='none'; result.classList.add('visible'); } finally { generate.disabled=false; generate.textContent='Gerar plano'; } };
  </script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/teleprompter":
            body = Path(__file__).with_name("teleprompter.html").read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path != "/":
            self._json(404, {"error": "Not found"})
            return
        body = PAGE.replace("%EXAMPLE%", json.dumps(DEMO_PROCEDURE, ensure_ascii=False))
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/plan":
            self._json(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            procedure = str(payload.get("procedure", "")).strip()
            if not procedure:
                raise ValueError("Informe um procedimento ou incidente.")
            self._json(200, ai_plan(procedure))
        except Exception as exc:  # Surface a useful message in the demo UI.
            self._json(400, {"error": str(exc)})

    def log_message(self, format: str, *args) -> None:
        print(f"[OpsPilot] {format % args}")


if __name__ == "__main__":
    print(f"OpsPilot AI em http://{HOST}:{PORT}")
    print("Modo demo ativo" if not os.getenv("OPENAI_API_KEY") else f"Modo OpenAI ativo ({MODEL})")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
