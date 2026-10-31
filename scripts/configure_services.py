"""Prompt for service secrets locally, without displaying them or putting them in shell history."""
from pathlib import Path
from getpass import getpass
import re

root = Path(__file__).resolve().parents[1]
path = root / '.env'
if not path.exists():
    raise SystemExit('Execute primeiro: python3 scripts/setup_local.py')
text = path.read_text()
for name, label in [('GEMINI_API_KEY','Chave Gemini (Google AI Studio)'),('RENDER_API_KEY','API key Render (Account Settings > API Keys)')]:
    value = getpass(label+' [Enter mantém valor atual]: ').strip()
    if value:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+',value):
            raise SystemExit('Formato de chave inesperado; não foi salvo.')
        if re.search(r'^'+name+r'=.*$',text,flags=re.M):
            text=re.sub(r'^'+name+r'=.*$',name+'='+value,text,flags=re.M)
        else:
            text+='\n'+name+'='+value+'\n'
path.write_text(text)
path.chmod(0o600)
print('Configuração salva no .env local. Nenhuma chave foi exibida ou enviada ao Git.')
