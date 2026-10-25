import sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from backend.llm import get_llm

llm = get_llm()
t = time.time()
out = llm.json("Reply with JSON only.", 'Return {"ok": true, "word": "hello"}',
               schema={"type": "object", "properties": {"ok": {"type": "boolean"},
                       "word": {"type": "string"}}, "required": ["ok", "word"]},
               max_tokens=40)
print(out, f"({time.time()-t:.1f}s incl. model load)")
