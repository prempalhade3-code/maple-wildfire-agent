{
echo "========== PROJECT STRUCTURE =========="
find . -type f \
  -not -path '*/node_modules/*' \
  -not -path '*/.git/*' \
  -not -path '*/venv/*' \
  -not -path '*/.venv/*' \
  -not -path '*/__pycache__/*' \
  -not -path '*/dist/*' \
  -not -path '*/build/*' \
  -not -path '*/.next/*' \
  | sort

echo -e "\n========== README =========="
cat README.md 2>/dev/null

echo -e "\n========== PACKAGE.JSON (Node/JS) =========="
cat package.json 2>/dev/null

echo -e "\n========== REQUIREMENTS.TXT (Python) =========="
cat requirements.txt 2>/dev/null

echo -e "\n========== PYPROJECT.TOML =========="
cat pyproject.toml 2>/dev/null

echo -e "\n========== ENV EXAMPLE (no secrets) =========="
cat .env.example 2>/dev/null
cat .env.sample 2>/dev/null

echo -e "\n========== ENV VARIABLE NAMES ONLY (from .env, no values) =========="
if [ -f .env ]; then grep -oE '^[A-Z_]+' .env; fi

echo -e "\n========== TECH STACK / CONFIG FILES =========="
for f in docker-compose.yml Dockerfile tsconfig.json vite.config.* next.config.* tailwind.config.* fastapi_app.py manage.py wsgi.py asgi.py alembic.ini; do
  if [ -f "$f" ]; then
    echo "--- $f ---"
    cat "$f"
    echo ""
  fi
done

echo -e "\n========== GIT LOG (last 30 commits) =========="
git log --oneline -30 2>/dev/null

echo -e "\n========== GIT STATUS =========="
git status 2>/dev/null

echo -e "\n========== BACKEND ENTRYPOINT FILES =========="
for f in main.py app.py server.py index.js server.js app.js src/main.ts src/index.ts src/app.ts; do
  if [ -f "$f" ]; then
    echo "--- $f ---"
    cat "$f"
    echo ""
  fi
done

echo -e "\n========== API ROUTES / ENDPOINTS DIRECTORY =========="
find . -type d \( -iname "routes" -o -iname "api" -o -iname "endpoints" -o -iname "controllers" \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null

echo -e "\n========== MODELS / SCHEMA FILES =========="
find . -type f \( -iname "models.py" -o -iname "schema.py" -o -iname "schema.prisma" -o -iname "*.sql" \) \
  -not -path '*/node_modules/*' 2>/dev/null

echo -e "\n========== FRONTEND/UI DIRECTORY STRUCTURE =========="
find ./src ./client ./frontend ./ui -maxdepth 3 -type f 2>/dev/null | grep -v node_modules

echo -e "\n========== DONE =========="
} > context_dump.txt

echo "Context dumped to context_dump.txt"
wc -l context_dump.txt
