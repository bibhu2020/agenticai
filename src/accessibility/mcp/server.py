# mcp/server.py
import os
import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page
import textwrap
import math

load_dotenv()

mcp = FastMCP("accessibility_server", version="1.1.0")

# Path to axe script (must exist next to this file or set AXE_JS_PATH env)
DEFAULT_AXE_PATH = os.path.join(os.path.dirname(__file__), "axe.min.js")
AXE_JS_PATH = os.environ.get("AXE_JS_PATH", DEFAULT_AXE_PATH)

# ---------- Helper: start browser, load page ----------
async def _open_page(url: str, timeout: int = 30000, wait_until: str = "load"):
    """
    Launch Playwright chromium, open url, return (playwright, browser, context, page).
    Caller must close browser and playwright.
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(args=["--no-sandbox"], headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url, timeout=timeout, wait_until=wait_until)
    # allow some dynamic content to settle
    await asyncio.sleep(0.5)
    return playwright, browser, context, page

# ---------- Helper: inject axe and run ----------
async def _ensure_axe(page: Page):
    if not os.path.exists(AXE_JS_PATH):
        raise FileNotFoundError(f"axe.min.js not found at {AXE_JS_PATH}. Download axe-core and place it there.")
    with open(AXE_JS_PATH, "r", encoding="utf-8") as f:
        axe_source = f.read()
    # Add axe to page
    await page.add_init_script(axe_source)
    # also evaluate once to be safe
    await page.evaluate("() => { window.__axe_injected = typeof axe !== 'undefined'; }")
    ok = await page.evaluate("() => typeof axe !== 'undefined'")
    if not ok:
        # attempt to inject directly
        await page.evaluate(axe_source + "\n() => {}")
    # final check
    ok2 = await page.evaluate("() => typeof axe !== 'undefined'")
    if not ok2:
        raise RuntimeError("Failed to inject axe into page")

async def _run_axe(page: Page, tags: Optional[List[str]] = None, rules: Optional[Dict[str, Any]] = None):
    """
    Run axe.run with wcag2a and wcag2aa tags by default.
    Returns axe JSON result.
    """
    tags = tags or ["wcag2a", "wcag2aa"]
    config = {"runOnly": {"type": "tag", "values": tags}}
    if rules:
        config["rules"] = rules
    # axe.run returns a Promise; evaluate and return JSON-serializable result
    result = await page.evaluate(
        """(conf) => {
            return axe.run(document, conf);
        }""",
        config,
    )
    return result

# ---------- Custom JS checks (run inside page) ----------
HEADINGS_JS = """() => {
  const headings = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6')).map(h => ({tag:h.tagName.toLowerCase(), text:h.innerText.trim().slice(0,200)}));
  const hasH1 = headings.some(h=>h.tag==='h1');
  let last = 0;
  const orderProblems = [];
  for (let i=0;i<headings.length;i++){
    const lvl = parseInt(headings[i].tag.slice(1));
    if (last !== 0 && (lvl - last) > 1) orderProblems.push({index:i, tag:headings[i].tag, prev:last});
    last = lvl;
  }
  return {headings, hasH1, orderProblems};
}"""

LANG_JS = """() => {
  const html = document.documentElement;
  const lang = html ? html.getAttribute('lang') : null;
  return {lang, dir: html ? html.getAttribute('dir') : null};
}"""

IMAGES_JS = """() => {
  const imgs = Array.from(document.images).map(i => ({src:i.currentSrc||i.src, alt:i.getAttribute('alt'), role:i.getAttribute('role'), ariaHidden:i.getAttribute('aria-hidden')}));
  const missingAlt = imgs.filter(i => (i.alt === null || i.alt === '') && i.ariaHidden !== 'true');
  return {count: imgs.length, missingAlt, sample: missingAlt.slice(0,10)};
}"""

FORMS_JS = """() => {
  const inputs = Array.from(document.querySelectorAll('input,textarea,select')).map(el=>{
    const id = el.id;
    const label = id ? (document.querySelector("label[for='"+id+"']") ? document.querySelector("label[for='"+id+"']").innerText : null) : (el.closest('label') ? el.closest('label').innerText : null);
    const ariaLabel = el.getAttribute('aria-label');
    const ariaLabelledBy = el.getAttribute('aria-labelledby');
    const name = el.getAttribute('name');
    return {tag:el.tagName.toLowerCase(), type:el.type||null, id, name, label: label ? label.trim().slice(0,200) : null, ariaLabel, ariaLabelledBy};
  });
  const missing = inputs.filter(i => !i.label && !i.ariaLabel && !i.ariaLabelledBy);
  return {inputsCount: inputs.length, missing, sample: missing.slice(0,10)};
}"""

ARIA_JS = """() => {
  // detect common ARIA misuse: role mismatch, duplicate ids referenced by aria-labelledby, missing required aria attributes
  const issues = [];
  const all = Array.from(document.querySelectorAll('[role], [aria-labelledby], [aria-label], [aria-hidden], [aria-live]'));
  for (const el of all) {
    const role = el.getAttribute('role');
    if (role && role === 'img' && !el.getAttribute('aria-label') && !el.querySelector('img')) {
      issues.push({type:'role-img-missing-name', outer: el.outerHTML.slice(0,200)});
    }
  }
  // duplicate id references
  const labels = {};
  Array.from(document.querySelectorAll('[id]')).forEach(e => { labels[e.id] = (labels[e.id]||0)+1; });
  Object.keys(labels).filter(k => labels[k]>1).forEach(k => issues.push({type:'duplicate-id', id:k, count:labels[k]}));
  return {count: all.length, issues: issues.slice(0,50)};
}"""

KEYBOARD_JS = """() => {
  // collect focusable elements
  const focusable = Array.from(document.querySelectorAll('a[href], button, input, textarea, select, [tabindex]'))
    .filter(el => !el.hasAttribute('disabled') && el.getAttribute('tabindex') !== '-1');
  // capture natural tab order (by DOM order)
  const tabOrder = focusable.map(el => ({tag: el.tagName.toLowerCase(), id: el.id||null, class: el.className||null, tabindex: el.getAttribute('tabindex')||null}));
  // detect tabindex>0 (bad practice)
  const positiveTabindex = focusable.filter(el => el.hasAttribute('tabindex') && parseInt(el.getAttribute('tabindex')||'0')>0).map(e=>({tag:e.tagName,id:e.id}));
  return {focusableCount: focusable.length, tabOrder: tabOrder.slice(0,200), positiveTabindex};
}"""

VIDEO_JS = """() => {
  const videos = Array.from(document.querySelectorAll('video,audio'));
  const out = [];
  for (const v of videos) {
    const tracks = Array.from(v.querySelectorAll('track')).map(t=>({kind:t.kind, srclang:t.srclang, label:t.label}));
    // look for external transcript links nearby
    let transcript = null;
    const next = v.nextElementSibling;
    if (next && /transcript|caption|captions/i.test(next.innerText||'')) transcript = next.innerText.trim().slice(0,300);
    out.push({tag:v.tagName.toLowerCase(), hasTracks: tracks.length>0, tracks, transcript});
  }
  return {count: videos.length, videos: out};
}"""

CONTRAST_JS = """() => {
  function luminance(r,g,b){
    const a = [r,g,b].map(v=>{ v=v/255; return v<=0.03928? v/12.92: Math.pow((v+0.055)/1.055,2.4);});
    return 0.2126*a[0]+0.7152*a[1]+0.0722*a[2];
  }
  function parseRGB(colorStr){
    const m = colorStr.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)/);
    return m ? [parseInt(m[1]),parseInt(m[2]),parseInt(m[3])] : null;
  }
  const candidates = Array.from(document.querySelectorAll('body *')).filter(el => (el.innerText||'').trim().length>0).slice(0,400);
  const issues = [];
  for (const el of candidates){
    const style = window.getComputedStyle(el);
    const color = parseRGB(style.color);
    let bg = null;
    let cur = el;
    while(cur && cur!==document){
      const b = window.getComputedStyle(cur).backgroundColor;
      if (b && b!=='rgba(0, 0, 0, 0)' && b!=='transparent') { bg = parseRGB(b); break; }
      cur = cur.parentElement;
    }
    if (!bg) bg = [255,255,255];
    if (!color) continue;
    const L1 = luminance(color[0],color[1],color[2]);
    const L2 = luminance(bg[0],bg[1],bg[2]);
    const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    const fontSize = parseFloat(style.fontSize) || 12;
    const fontWeight = style.fontWeight;
    const large = fontSize >= 18 || (fontSize >= 14 && (fontWeight === '700' || parseInt(fontWeight||'0')>=700));
    const pass = large ? ratio >= 3.0 : ratio >= 4.5;
    if (!pass) issues.push({text: (el.innerText||'').slice(0,120), ratio: Number(ratio.toFixed(2)), fontSize, large});
  }
  return {checked: candidates.length, issues: issues.slice(0,200)};
}"""

SEMANTICS_JS = """() => {
  // check for landmark elements and semantic usage
  const landmarks = {};
  ['header','main','nav','footer','aside','form'].forEach(k => landmarks[k] = document.querySelectorAll(k).length);
  // detect skip link
  const skip = Array.from(document.querySelectorAll('a[href]')).some(a => /skip|skip to content/i.test(a.innerText||''));
  return {landmarks, hasSkipLink: skip};
}"""

# ---------- Tool definitions ----------
@mcp.tool()
async def run_axe_audit(url: str, timeout: int = 30000):
    """
    Run axe-core on the page and return the full axe result (violations, passes, incomplete, etc).
    This is the primary automated scanner and is required for broad WCAG coverage.
    """
    playwright = browser = context = page = None
    try:
        playwright, browser, context, page = await _open_page(url, timeout=timeout)
        await _ensure_axe(page)
        axe_result = await _run_axe(page, tags=["wcag2a", "wcag2aa"])
        return {"url": url, "axe": axe_result}
    except Exception as e:
        return {"url": url, "error": str(e)}
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

# Individual custom checks (wrap the JS above)
async def _eval_js_on_page(url: str, js: str, timeout: int = 30000):
    playwright = browser = context = page = None
    try:
        playwright, browser, context, page = await _open_page(url, timeout=timeout)
        res = await page.evaluate(js)
        return {"url": url, "result": res}
    except Exception as e:
        return {"url": url, "error": str(e)}
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

@mcp.tool()
async def check_headings(url: str):
    return await _eval_js_on_page(url, HEADINGS_JS)

@mcp.tool()
async def check_language(url: str):
    return await _eval_js_on_page(url, LANG_JS)

@mcp.tool()
async def check_images(url: str):
    return await _eval_js_on_page(url, IMAGES_JS)

@mcp.tool()
async def check_forms(url: str):
    return await _eval_js_on_page(url, FORMS_JS)

@mcp.tool()
async def check_aria(url: str):
    return await _eval_js_on_page(url, ARIA_JS)

@mcp.tool()
async def check_keyboard(url: str):
    return await _eval_js_on_page(url, KEYBOARD_JS)

@mcp.tool()
async def check_videos(url: str):
    return await _eval_js_on_page(url, VIDEO_JS)

@mcp.tool()
async def check_contrast(url: str):
    return await _eval_js_on_page(url, CONTRAST_JS)

@mcp.tool()
async def check_semantics(url: str):
    return await _eval_js_on_page(url, SEMANTICS_JS)

# Aggregator / Full audit
@mcp.tool()
async def full_audit(url: str, timeout: int = 60000):
    """
    Runs axe + all custom checks and returns a comprehensive report with suggested remediation hints.
    """
    # Run axe and custom checks concurrently but within limit
    tasks = {
        "axe": asyncio.create_task(run_axe_audit(url, timeout=timeout)),
        "headings": asyncio.create_task(check_headings(url)),
        "language": asyncio.create_task(check_language(url)),
        "images": asyncio.create_task(check_images(url)),
        "forms": asyncio.create_task(check_forms(url)),
        "aria": asyncio.create_task(check_aria(url)),
        "keyboard": asyncio.create_task(check_keyboard(url)),
        "videos": asyncio.create_task(check_videos(url)),
        "contrast": asyncio.create_task(check_contrast(url)),
        "semantics": asyncio.create_task(check_semantics(url)),
    }
    results: Dict[str, Any] = {}
    for k, t in tasks.items():
        try:
            results[k] = await t
        except Exception as e:
            results[k] = {"error": str(e)}

    # Build summary: count axe violations of level 'serious' or 'critical' (if present), map to quick remediation hints
    summary = {"url": url, "total_axe_violations": 0, "by_impact": {}, "quick_fixes": []}
    try:
        axe_out = results.get("axe", {}).get("axe") or results.get("axe", {}).get("result")
        if axe_out and isinstance(axe_out, dict):
            violations = axe_out.get("violations", [])
            summary["total_axe_violations"] = len(violations)
            by_impact = {}
            for v in violations:
                impact = v.get("impact", "unknown")
                by_impact[impact] = by_impact.get(impact, 0) + 1
                # add concise remediation hint
                summary["quick_fixes"].append({
                    "id": v.get("id"),
                    "impact": impact,
                    "help": v.get("help"),
                    "nodes_sample": [n.get("html")[:200] for n in v.get("nodes", [])[:3]],
                    "why": v.get("description")
                })
            summary["by_impact"] = by_impact
    except Exception:
        pass

    # augment summary with simple counts from custom checks
    try:
        summary["missing_alt_count"] = len(results.get("images", {}).get("result", {}).get("missingAlt", [])) if results.get("images", {}).get("result") else None
    except Exception:
        summary["missing_alt_count"] = None
    try:
        summary["forms_missing_labels"] = len(results.get("forms", {}).get("result", {}).get("missing", [])) if results.get("forms", {}).get("result") else None
    except Exception:
        summary["forms_missing_labels"] = None
    try:
        summary["contrast_issues"] = len(results.get("contrast", {}).get("result", {}).get("issues", [])) if results.get("contrast", {}).get("result") else None
    except Exception:
        summary["contrast_issues"] = None

    # Return combined report
    return {"url": url, "summary": summary, "results": results}

# Run MCP server via stdio transport
if __name__ == "__main__":
    print("Starting Accessibility MCP server (stdio transport).")
    if not os.path.exists(AXE_JS_PATH):
        print(f"WARNING: axe.min.js not found at {AXE_JS_PATH}. Download axe-core (axe.min.js) and place it beside this file or set AXE_JS_PATH.")
    mcp.run(transport="stdio")
