from flask import Flask, request, render_template_string, jsonify
import ast
import operator as op

app = Flask(__name__)

# Safe evaluation of arithmetic expressions using ast
# Allowed operators
ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def safe_eval(expr: str):
    """Evaluate a mathematical expression safely.
    Supports +, -, *, /, %, **, parentheses and unary +/-."""

    def _eval(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[op_type](left, right)
            raise ValueError(f"Operator {op_type} not allowed")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                return ALLOWED_OPERATORS[op_type](operand)
            raise ValueError(f"Unary operator {op_type} not allowed")
        raise ValueError(f"Unsupported expression: {type(node)}")

    parsed = ast.parse(expr, mode='eval')
    return _eval(parsed)


TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Calculator</title>
  <style>
    :root{--bg:#0f1724;--card:#0b1220;--accent:#60a5fa;--text:#e6eef8}
    *{box-sizing:border-box}
    body{font-family:Inter,system-ui,Segoe UI,Roboto,'Helvetica Neue',Arial;background:linear-gradient(180deg,#071029 0%, #071a2b 100%);color:var(--text);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
    .card{width:420px;max-width:95%;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));border-radius:14px;padding:18px;box-shadow:0 6px 30px rgba(2,6,23,0.7)}
    .display{background:rgba(0,0,0,0.35);padding:14px;border-radius:10px;min-height:64px;display:flex;flex-direction:column;justify-content:center;align-items:flex-end}
    .small{opacity:0.6;font-size:13px;margin-bottom:6px}
    .big{font-size:28px;word-break:break-all}
    .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}
    button{padding:16px;border-radius:10px;border:0;background:rgba(255,255,255,0.03);color:var(--text);font-size:18px;cursor:pointer;box-shadow:inset 0 -2px 0 rgba(0,0,0,0.25)}
    button:active{transform:translateY(1px)}
    .op{background:linear-gradient(180deg, rgba(96,165,250,0.15), rgba(96,165,250,0.06));}
    .equals{grid-column:span 2;background:var(--accent);color:#012240;font-weight:700}
    .wide{grid-column:span 2}
    .history{margin-top:14px;max-height:120px;overflow:auto;padding:8px;border-radius:8px;background:rgba(255,255,255,0.02);font-size:14px}
    .hist-item{padding:6px;border-bottom:1px dashed rgba(255,255,255,0.03);display:flex;justify-content:space-between}
    .muted{opacity:0.65;font-size:13px}
    @media (max-width:420px){.card{padding:12px}.display{min-height:56px}.big{font-size:22px}}
  </style>
</head>
<body>
  <div class="card" role="application" aria-label="Calculator">
    <div class="display" id="display">
      <div class="small" id="mem">{{ memory }}</div>
      <div class="big" id="expr">0</div>
    </div>

    <div class="grid" role="group" aria-label="calculator buttons">
      <button onclick="press('C')">C</button>
      <button onclick="press('+/-')">+/-</button>
      <button onclick="press('%')">%</button>
      <button onclick="press('/')" class="op">÷</button>

      <button onclick="press('7')">7</button>
      <button onclick="press('8')">8</button>
      <button onclick="press('9')">9</button>
      <button onclick="press('*')" class="op">×</button>

      <button onclick="press('4')">4</button>
      <button onclick="press('5')">5</button>
      <button onclick="press('6')">6</button>
      <button onclick="press('-')" class="op">−</button>

      <button onclick="press('1')">1</button>
      <button onclick="press('2')">2</button>
      <button onclick="press('3')">3</button>
      <button onclick="press('+')" class="op">+</button>

      <button onclick="press('0')" class="wide">0</button>
      <button onclick="press('.')">.</button>
      <button onclick="evaluate()" class="equals">=</button>
    </div>

    <div class="history" id="history">
      {% for h in history %}
        <div class="hist-item"><div>{{ h.expr }}</div><div class="muted">= {{ h.result }}</div></div>
      {% endfor %}
    </div>
  </div>

<script>
  let exprEl = document.getElementById('expr');
  let memEl = document.getElementById('mem');
  let historyEl = document.getElementById('history');
  let expr = '';

  function refreshDisplay(){
    exprEl.textContent = expr === '' ? '0' : expr;
  }

  function press(val){
    if(val === 'C') { expr = ''; refreshDisplay(); return; }
    if(val === '+/-'){
      if(expr.startsWith('-')) expr = expr.slice(1); else expr = '-' + expr;
      refreshDisplay(); return;
    }
    expr += val;
    refreshDisplay();
  }

  async function evaluate(){
    if(expr.trim() === '') return;
    try{
      const res = await fetch('/eval', {
        method: 'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({expr})
      });
      const js = await res.json();
      if(js.ok){
        expr = String(js.result);
        // prepend to history visually
        const wrap = document.createElement('div');
        wrap.className = 'hist-item';
        wrap.innerHTML = `<div>${js.input}</div><div class="muted">= ${js.result}</div>`;
        historyEl.prepend(wrap);
        refreshDisplay();
      } else {
        alert('Error: ' + js.error);
      }
    } catch(e){
      alert('Network or server error');
    }
  }

  // keyboard support
  window.addEventListener('keydown', (ev)=>{
    const k = ev.key;
    if((/^[0-9]$/).test(k) || k === '+' || k === '-' || k === '*' || k === '/' || k === '%' || k === '.' ){
      press(k);
    } else if(k === 'Enter'){
      evaluate();
    } else if(k === 'Backspace'){
      expr = expr.slice(0, -1); refreshDisplay();
    } else if(k === 'c' || k === 'C'){
      press('C');
    }
  });

</script>
</body>
</html>
"""


@app.route('/')
def index():
    # initial memory and history (kept in-memory for demo; not persistent)
    memory = ''
    history = []
    return render_template_string(TEMPLATE, memory=memory, history=history)


@app.route('/eval', methods=['POST'])
def evaluate():
    data = request.get_json() or {}
    expr = data.get('expr', '')
    try:
        # Replace the unicode division/multiplication symbols in case front-end sends them
        cleaned = expr.replace('×', '*').replace('÷', '/')
        # Handle percent operator as modulo or percentage: interpret a%b as a % b
        # If user typed like '50%' we will convert to '(50/100)'
        if cleaned.endswith('%') and cleaned[:-1].strip().replace('.', '', 1).isdigit():
            cleaned = f"({cleaned[:-1]})/100"
        result = safe_eval(cleaned)
        return jsonify(ok=True, result=result, input=expr)
    except Exception as e:
        return jsonify(ok=False, error=str(e))


if __name__ == '__main__':
    app.run(debug=True)
