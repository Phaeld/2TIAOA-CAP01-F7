"""Create ignored local credentials once; never overwrite an existing .env."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
path = root / ".env"
if path.exists():
    raise SystemExit(".env já existe; mantido sem alterações.")
values = (root / ".env.example").read_text()
for name, size in [("CARDIOIA_SECRET", 48), ("CARDIOIA_DEMO_PASSWORD", 18), ("CARDIOIA_DEVICE_KEY", 32)]:
    values = values.replace(name + "=\n", name + "=" + secrets.token_urlsafe(size) + "\n")
with path.open("x") as file:
    file.write(values)
path.chmod(0o600)
print("Credenciais geradas no .env (ignorado pelo Git, permissão 600). Consulte-o localmente para login.")
