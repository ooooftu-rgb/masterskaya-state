import json, os, urllib.parse, urllib.request, sys
from pathlib import Path
from datetime import datetime, timezone
root=Path(__file__).resolve().parent
queue=json.loads((root/"queue.json").read_text(encoding="utf-8"))
state=json.loads((root/"state.json").read_text(encoding="utf-8"))
remaining=[x for x in queue if x["id"] not in state["sent"]]
if not remaining:
    print("Queue empty; no publication."); sys.exit(0)
post=remaining[0]
url="https://ooooftu-rgb.github.io/masterskaya-state/promo/60/?"+urllib.parse.urlencode(dict(utm_source="telegram",utm_medium="organic",utm_campaign="autopilot",utm_content=post["id"]))
message=f'{post["title"]}\n\n{post["text"]}\n\n{url}'
token=os.getenv("TELEGRAM_BOT_TOKEN","")
chat=os.getenv("TELEGRAM_CHAT_ID","")
if os.getenv("PROMO_DRY_RUN")=="1" or not token or not chat:
    print("PREVIEW ONLY. Telegram not configured or dry run enabled.\n"+message);sys.exit(0)
payload=urllib.parse.urlencode({"chat_id":chat,"text":message}).encode()
try:
    with urllib.request.urlopen(urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",data=payload),timeout=30) as r:
        result=json.load(r)
    if not result.get("ok"): raise ValueError("Telegram returned error")
except Exception as e:
    print("Publication failed: "+type(e).__name__,file=sys.stderr);sys.exit(1)
state["sent"].append(post["id"])
state["last_run"]=datetime.now(timezone.utc).isoformat()
(root/"state.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Published post "+post["id"])
