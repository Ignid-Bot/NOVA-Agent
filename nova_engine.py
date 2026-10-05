from pathlib import Path
from datetime import datetime
import json
DATA_DIR=Path('data'); DATA_DIR.mkdir(exist_ok=True); DATA_FILE=DATA_DIR/'personal_transactions.json'
class NovaEngine:
 def __init__(self): self.transactions=self._load()
 def _load(self):
  if not DATA_FILE.exists():return []
  try:return json.loads(DATA_FILE.read_text(encoding='utf-8'))
  except:return []
 def _save(self):DATA_FILE.write_text(json.dumps(self.transactions,ensure_ascii=False,indent=2),encoding='utf-8')
 def add_transaction(self,tx):
  for x in self.transactions:
   if all(x.get(k)==tx.get(k) for k in ('date','type','description','amount')):
    return f"⚠️ Kemungkinan duplikat: {tx['description']} Rp{tx['amount']:,}".replace(',','.')
  tx['id']=f"TX-{len(self.transactions)+1:05d}"; tx['created_at']=datetime.now().isoformat(timespec='seconds'); self.transactions.append(tx); self._save()
  inc=sum(x['amount'] for x in self.transactions if x['type']=='Pendapatan'); exp=sum(x['amount'] for x in self.transactions if x['type']=='Pengeluaran')
  return f"✅ NOVA mencatat.\n🆔 {tx['id']}\n📅 {tx['date']}\n📌 {tx['type']}\n📝 {tx['description']}\n💰 Rp{tx['amount']:,}\n\n💵 Saldo berjalan: Rp{inc-exp:,}".replace(',','.')
