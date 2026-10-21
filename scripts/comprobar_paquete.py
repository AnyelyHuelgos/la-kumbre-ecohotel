"""Verificacion local de archivos antes de subir el codigo a GitHub.
No imprime secretos; devuelve solo el archivo y numero de linea potencialmente inseguro.
"""
from pathlib import Path
import ast
import re
import sys

root=Path(__file__).resolve().parents[1]
settings=root/'sitio/settings.py'
text=settings.read_text(encoding='utf-8')
alerts=[]
for path in sorted(root.rglob('*')):
    if not path.is_file() or path.suffix.lower() not in {'.py', '.js', '.html', '.css', '.md', '.txt', '.example'}:continue
    relative=path.relative_to(root).as_posix()
    if any(part in {'.git','.venv','venv','env','node_modules','__pycache__'} for part in path.relative_to(root).parts):continue
    data=path.read_text('utf-8',errors='replace')
    for i,line in enumerate(data.splitlines(),1):
        if relative=='sitio/settings.py':
            if re.search(r'(?i)^\s*#.*(?:PASSWORD|SECRET_KEY)\s*[=:]',line):alerts.append((relative,i,'credencial antigua comentada'))
            if re.search(r'^\s*(?:SECRET_KEY|EMAIL_HOST_PASSWORD)\s*=\s*[\x27\x22]',line):alerts.append((relative,i,'credencial escrita directamente'))
    if path.suffix=='.py':
        try:ast.parse(data,filename=relative)
        except SyntaxError as e:alerts.append((relative,e.lineno,'error sintactico'))
for name in ['.env','db.sqlite3']:
    if (root/name).exists():print('Aviso: archivo local privado presente; verifica .gitignore:',name)
if alerts:
    for path,line,reason in alerts:print(f'REVISAR {path}:{line} ({reason})')
    sys.exit(1)
print('Comprobacion basica OK. No sustituye una auditoria de seguridad completa ni elimina secretos de Git history.')
