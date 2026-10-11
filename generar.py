"""Uso: python generar.py  ->  crea docs/index.html a partir de resenas/*.md"""
import re, json, html, shutil, pathlib
R = pathlib.Path(__file__).parent
def parse(p):
    m = re.match(r"---\n(.*?)\n---\n(.*)", p.read_text(encoding="utf-8"), re.S)
    d = {}
    for l in m[1].splitlines():
        if ":" in l:
            k, v = l.split(":", 1); d[k.strip()] = v.strip()
    out, par = [], []
    def flush():
        if par: out.append("<p>" + html.escape(" ".join(par)) + "</p>"); par.clear()
    for l in m[2].splitlines():
        s = l.strip()
        if s==":::spoilers": flush(); out.append("<details><summary>⚠️ Con spoilers · toca para abrir</summary>")
        elif s==":::": flush(); out.append("</details>")
        elif s.startswith("# "): flush(); out.append(f"<h2>{html.escape(s[2:])}</h2>")
        elif s.startswith("## "): flush(); out.append(f"<h3>{html.escape(s[3:])}</h3>")
        elif s.startswith("> "): flush(); out.append(f"<blockquote>{html.escape(s[2:])}</blockquote>")
        elif s: par.append(s)
        else: flush()
    flush()
    d["html"] = "".join(out); d["id"] = p.stem
    d["calificacion"] = float(d.get("calificacion", 0) or 0)
    d["sent"] = [x.strip().split("=") for x in d.get("sentimientos", "").split(",") if "=" in x]
    return d
libros = sorted((parse(p) for p in (R / "resenas").glob("*.md")), key=lambda b: b.get("reseñado", ""), reverse=True)
(R / "docs").mkdir(exist_ok=True)
if (R / "portadas").exists(): shutil.copytree(R / "portadas", R / "docs/portadas", dirs_exist_ok=True)
tpl = (R / "plantilla.html").read_text(encoding="utf-8")
(R / "docs/index.html").write_text(tpl.replace("__DATA__", json.dumps(libros, ensure_ascii=False)), encoding="utf-8")
print(f"Listo: {len(libros)} reseña(s) en docs/index.html")
