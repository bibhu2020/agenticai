import os
import asyncio
from typing import Any, Dict, List, Optional
from playwright.async_api import async_playwright, Page

# Path to axe script
DEFAULT_AXE_PATH = os.path.join(os.path.dirname(__file__), "axe.min.js")
AXE_JS_PATH = os.environ.get("AXE_JS_PATH", DEFAULT_AXE_PATH)

class WebAuditor:
    """
    Encapsulates Playwright based accessibility auditing logic.
    """

    async def _open_page(self, url: str, timeout: int = 30000, wait_until: str = "load"):
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(args=["--no-sandbox"], headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url, timeout=timeout, wait_until=wait_until)
            await asyncio.sleep(0.5) # Settle
        except Exception as e:
            await context.close()
            await browser.close()
            await playwright.stop()
            raise e
            
        return playwright, browser, context, page

    async def _ensure_axe(self, page: Page):
        if not os.path.exists(AXE_JS_PATH):
            raise FileNotFoundError(f"axe.min.js not found at {AXE_JS_PATH}")
        with open(AXE_JS_PATH, "r", encoding="utf-8") as f:
            axe_source = f.read()
        await page.add_init_script(axe_source)
        # Ensure it loaded
        await page.evaluate("() => { window.__axe_injected = typeof axe !== 'undefined'; }")
        
    async def _run_axe(self, page: Page, tags: Optional[List[str]] = None):
        tags = tags or ["wcag2a", "wcag2aa"]
        return await page.evaluate("""(tags) => {
            return axe.run(document, {runOnly: {type: 'tag', values: tags}});
        }""", tags)

    async def full_audit(self, url: str) -> Dict[str, Any]:
        playwright = browser = context = page = None
        results = {}
        
        try:
            playwright, browser, context, page = await self._open_page(url)
            
            # 1. Axe Audit
            try:
                await self._ensure_axe(page)
                axe_res = await self._run_axe(page)
                results["axe"] = axe_res
            except Exception as e:
                results["axe_error"] = str(e)
                
            # 2. Simple Custom Checks (simplified for brevity here, can expand later)
            results["title"] = await page.title()
            
            # Map Axe violations to a simpler summary
            violations = results.get("axe", {}).get("violations", [])
            simple_violations = []
            for v in violations:
                simple_violations.append({
                    "id": v.get("id"),
                    "impact": v.get("impact"),
                    "description": v.get("description"),
                    "help": v.get("help"),
                    "nodes_count": len(v.get("nodes", []))
                })
            
            results["summary"] = {
                "violation_count": len(violations),
                "violations": simple_violations
            }
            
            return {"url": url, "success": True, "data": results}

        except Exception as e:
            return {"url": url, "success": False, "error": str(e)}
        finally:
            if context: await context.close()
            if browser: await browser.close()
            if playwright: await playwright.stop()
