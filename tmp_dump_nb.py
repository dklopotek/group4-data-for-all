import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
path = sys.argv[1]
nb = json.load(open(path, "r", encoding="utf-8"))
for i, c in enumerate(nb["cells"]):
    print(f"---CELL {i} id={c.get('id','?')} type={c.get('cell_type','?')}---")
    src = "".join(c.get("source", []))
    print(src)
    print()
