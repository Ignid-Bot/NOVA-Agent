import os,re
from datetime import datetime
from telegram import Update
from telegram.ext import Application,CommandHandler,MessageHandler,ContextTypes,filters
from nova_engine import NovaEngine
TOKEN=os.getenv('TELEGRAM_BOT_TOKEN'); engine=NovaEngine()
def parse_amount(text):
 s=text.lower().replace('rp','').replace('idr','').replace('.','').replace(',','.').strip(); m=re.search(r'(\d+(?:\.\d+)?)\s*(juta|jt|ribu|rb|k)?',s)
 if not m:return None
 v=float(m.group(1)); u=m.group(2)
 if u in ('juta','jt'):v*=1_000_000
 elif u in ('ribu','rb','k'):v*=1_000
 return int(v)
def parse_text(text):
 a=parse_amount(text)
 if a is None:return None
 low=text.lower(); income=['gaji','bonus','thr','pendapatan','penghasilan','tambahan dari kerja']
 return {'date':datetime.now().strftime('%Y-%m-%d'),'type':'Pendapatan' if any(w in low for w in income) else 'Pengeluaran','description':text.strip(),'source':'Telegram','amount':a,'status':'FINAL'}
async def start(update,context):
 await update.message.reply_text('🤖 NOVA aktif.\n\nContoh:\n• jajan 50k\n• beli kabel cas 60k\n• gaji 5 juta\n• bonus 500k')
async def help_cmd(update,context): await update.message.reply_text('Ketik transaksi natural, contoh: jajan 50k atau gaji 5 juta.')
async def message(update,context):
 tx=parse_text(update.message.text or '')
 if not tx:return await update.message.reply_text('⚠️ Belum terbaca. Coba: jajan 50k')
 await update.message.reply_text(engine.add_transaction(tx))
def main():
 if not TOKEN: raise RuntimeError('TELEGRAM_BOT_TOKEN belum diset.')
 app=Application.builder().token(TOKEN).build(); app.add_handler(CommandHandler('start',start)); app.add_handler(CommandHandler('help',help_cmd)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,message)); app.run_polling()
if __name__=='__main__':main()
