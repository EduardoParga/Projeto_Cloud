import json, os, sys, glob

candidates = []
candidates += glob.glob(os.path.join(os.getcwd(), "azurite_data__azurite_db_*.json"))
candidates += glob.glob(os.path.join(os.getcwd(), "azurite_data", "*azurite_db_*.json"))
candidates += glob.glob(os.path.join(os.getcwd(), "*azurite_db_*.json"))

if not candidates:
    print("Nenhum arquivo azurite_db json encontrado automaticamente. Rode:")
    print("Get-ChildItem -Recurse -Filter '*azurite_db_*.json' | Select-Object -First 50")
    sys.exit(1)

for path in candidates:
    print("\n==> analisando:", path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("  erro abrindo JSON:", e)
        continue

    names = []
    def walk(obj):
        if isinstance(obj, dict):
            for k,v in obj.items():
                if isinstance(v, str) and k.lower() in ("name","blobname","blob","file","filename"):
                    names.append(v)
                walk(v)
        elif isinstance(obj, list):
            for it in obj:
                walk(it)
    walk(data)

    if not names:
        print("  nenhum nome encontrado na varredura deste JSON.")
        continue

    longs = [(n, len(n)) for n in names if len(n) > 200]
    if longs:
        print("  Nomes muito longos (>200 chars):")
        for n,l in longs[:50]:
            print(f"   len={l}  {n[:300]}{'...' if l>300 else ''}")
    else:
        print("  Nenhum nome >200 chars encontrado neste JSON.")
    print("  Top 30 maiores nomes (len, prefixo):")
    for n in sorted(names, key=len, reverse=True)[:30]:
        l = len(n)
        print(f"   {l:4d}  {n[:300]}{'...' if l>300 else ''}")