from pathlib import Path
import json
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'Backend'))
from cardioia.main import create_app

(root / 'docs/openapi.json').write_text(json.dumps(create_app().openapi(), indent=2, ensure_ascii=False)+'\n')
print('docs/openapi.json atualizado')
