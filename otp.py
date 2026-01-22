import requests
import json
import random
import concurrent.futures
from flask import Flask, request, render_template_string, jsonify

# --- ⚠️ AUTHENTICATION SETTINGS ⚠️ ---
MAUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJNXzZDMkZSS1k4MiIsInJvbGUiOiJ1c2VyIiwiYWNjZXNzX3BhdGgiOlsiL2Rhc2hib2FyZCJdLCJleHBpcnkiOjE3NjkxOTk0NTgsImNyZWF0ZWQiOjE3NjkxMTMwNTgsIjJvbzkiOiJNc0giLCJleHAiOjE3NjkxOTk0NTgsImlhdCI6MTc2OTExMzA1OCwic3ViIjoiTV82QzJGUktZODIifQ.IdaOkIf09zobtxACP4u7TlDUaUcD_oh_HH53bs1mEIc"
COOKIE_VALUE = "PASTE_NEW_COOKIE_HERE" 
# -------------------------------------

app = Flask(__name__)
app.secret_key = "xz_sms_secret_v3_turbo"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XZ SMS - TURBO Fetcher</title>
    <style>
        :root { --primary: #0f172a; --accent: #ef4444; --bg: #f1f5f9; --success: #10b981; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: #334155; padding: 20px; }
        .container { max-width: 650px; margin: 0 auto; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); }
        h2 { color: var(--primary); margin-top: 0; text-align: center; }
        
        .form-grid { display: grid; gap: 15px; margin-bottom: 20px; }
        label { font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 5px; }
        input[type="text"], input[type="number"] { width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; font-size: 1rem; }
        
        .options { display: flex; gap: 20px; background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }
        .checkbox-item { display: flex; align-items: center; gap: 8px; cursor: pointer; font-size: 0.9rem; }
        
        button { width: 100%; padding: 14px; background: var(--accent); color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 1rem; transition: all 0.2s; }
        button:hover { background: #dc2626; transform: translateY(-1px); }
        button:disabled { background: #94a3b8; cursor: wait; transform: none; }

        #copyAllBtn { background: var(--success); margin-top: 15px; display: none; }
        #copyAllBtn:hover { background: #059669; }

        .log-box { background: #1e293b; color: #10b981; font-family: monospace; padding: 15px; border-radius: 8px; margin-top: 20px; height: 150px; overflow-y: auto; font-size: 0.85rem; border: 1px solid #334155; }
        .log-error { color: #ef4444; }
        .log-warn { color: #f59e0b; }
        
        .result-item { background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 10px; margin-top: 10px; border-radius: 6px; font-family: monospace; font-size: 1.2rem; display: flex; justify-content: space-between; align-items: center; }
        .copy-btn { background: white; border: 1px solid #bfdbfe; color: #3b82f6; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; cursor: pointer; width: auto; }
    </style>
</head>
<body>

<div class="container">
    <h2>🚀 XZ SMS TURBO V4</h2>
    
    <div class="form-grid">
        <div>
            <label>Range Code (e.g. 225014081XXX)</label>
            <input type="text" id="range" placeholder="Enter range code..." required>
        </div>
        
        <div class="options">
            <label class="checkbox-item">
                <input type="checkbox" id="is_national"> Is National
            </label>
            <label class="checkbox-item">
                <input type="checkbox" id="remove_plus"> Remove Plus (+)
            </label>
        </div>

        <div>
            <label>Quantity</label>
            <input type="number" id="quantity" value="5" min="1" max="50">
        </div>
    </div>

    <button id="startBtn" onclick="startFetch()">⚡ Get Numbers Fast</button>

    <button id="copyAllBtn" onclick="copyAllNumbers()">📋 Copy All Numbers</button>

    <div id="results"></div>
    <div class="log-box" id="logs">Ready to turbo fetch...</div>
</div>

<script>
    let fetchedNumbersCache = []; 

    async function startFetch() {
        const btn = document.getElementById('startBtn');
        const copyAllBtn = document.getElementById('copyAllBtn');
        const logs = document.getElementById('logs');
        const results = document.getElementById('results');
        
        const range = document.getElementById('range').value;
        const qty = document.getElementById('quantity').value;
        const isNational = document.getElementById('is_national').checked;
        const removePlus = document.getElementById('remove_plus').checked;

        if(!range) return alert("Please enter a range");

        btn.disabled = true;
        btn.innerText = "🚀 Speed Fetching...";
        results.innerHTML = "";
        copyAllBtn.style.display = "none"; 
        fetchedNumbersCache = []; 
        logs.innerHTML = "<div>⏳ Launching parallel requests...</div>";

        try {
            const response = await fetch('/api/fetch', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    range: range,
                    quantity: parseInt(qty),
                    is_national: isNational,
                    remove_plus: removePlus
                })
            });
            
            const data = await response.json();
            
            logs.innerHTML = data.logs.map(l => {
                if(l.includes("❌")) return `<div class='log-error'>${l}</div>`;
                if(l.includes("⚠️")) return `<div class='log-warn'>${l}</div>`;
                return `<div>${l}</div>`;
            }).join("");

            if(data.numbers.length > 0) {
                fetchedNumbersCache = data.numbers; 
                copyAllBtn.style.display = "block"; 
                
                data.numbers.forEach(num => {
                    results.innerHTML += `
                        <div class="result-item">
                            <span>${num}</span>
                            <button class="copy-btn" onclick="navigator.clipboard.writeText('${num}')">Copy</button>
                        </div>`;
                });
            } else {
                 logs.innerHTML += "<div>⚠️ No numbers found in this batch.</div>";
            }

        } catch (e) {
            logs.innerHTML += `<div class='log-error'>❌ Network Error: ${e.message}</div>`;
        }
        
        btn.disabled = false;
        btn.innerText = "⚡ Get Numbers Fast";
    }

    function copyAllNumbers() {
        if(fetchedNumbersCache.length === 0) return;
        const allText = fetchedNumbersCache.join("\\n");
        navigator.clipboard.writeText(allText).then(() => {
            const btn = document.getElementById('copyAllBtn');
            const originalText = btn.innerText;
            btn.innerText = "✅ Copied!";
            setTimeout(() => btn.innerText = originalText, 2000);
        });
    }
</script>
</body>
</html>
"""

def get_headers(range_val):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]
    return {
        "authority": "stexsms.com",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "mauthtoken": MAUTH_TOKEN,
        "cookie": COOKIE_VALUE,
        "origin": "https://stexsms.com",
        "referer": f"https://stexsms.com/mdashboard/getnum?range={range_val}",
        "user-agent": random.choice(user_agents)
    }

# --- WORKER FUNCTION FOR PARALLEL EXECUTION ---
def fetch_worker(session, url, payload, headers):
    try:
        r = session.post(url, json=payload, headers=headers, timeout=5)
        
        if r.status_code == 200:
            try:
                js = r.json()
                num = js.get('data', {}).get('number') or js.get('number')
                if num:
                    return (f"✅ Found: {num}", num)
                else:
                    return (f"⚠️ Empty/Invalid: {str(js)[:40]}...", None)
            except:
                if "<title>" in r.text:
                    title = r.text.split('<title>')[1].split('</title>')[0]
                    return (f"❌ Server HTML: '{title}'", None)
                return (f"❌ Bad JSON: {r.text[:30]}", None)
        elif r.status_code in [401, 403]:
            return ("❌ AUTH FAILED: Check Cookie/Token", None)
        else:
            return (f"❌ HTTP {r.status_code}", None)
    except Exception as e:
        return (f"❌ Error: {str(e)}", None)

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/fetch', methods=['POST'])
def fetch_api():
    d = request.json
    logs = []
    found = []
    
    url = "https://stexsms.com/mapi/v1/mdashboard/getnum/number"
    payload = {
        "range": d['range'],
        "is_national": d['is_national'],
        "remove_plus": d['remove_plus']
    }
    
    quantity = min(d['quantity'], 50) # Cap at 50 to prevent freezing

    # Use a Session for connection pooling (Faster Handshakes)
    session = requests.Session()

    # ThreadPoolExecutor runs requests in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Create a list of future tasks
        futures = [
            executor.submit(
                fetch_worker, 
                session, 
                url, 
                payload, 
                get_headers(d['range'])
            ) 
            for _ in range(quantity)
        ]
        
        # Gather results as they complete
        for future in concurrent.futures.as_completed(futures):
            log_msg, number = future.result()
            logs.append(log_msg)
            if number:
                found.append(number)

    return jsonify({"logs": logs, "numbers": found})

if __name__ == '__main__':
    print("✅ V4 TURBO Running at http://localhost:5000")

    app.run(port=5000, debug=True)
