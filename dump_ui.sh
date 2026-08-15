{
echo "========== FRONTEND PACKAGE.JSON =========="
cat frontend/package.json

echo -e "\n========== TAILWIND CONFIG =========="
cat frontend/tailwind.config.js

echo -e "\n========== GLOBALS.CSS =========="
cat frontend/styles/globals.css

echo -e "\n========== _app.tsx =========="
cat frontend/pages/_app.tsx

echo -e "\n========== index.tsx =========="
cat frontend/pages/index.tsx

echo -e "\n========== platform.tsx =========="
cat frontend/pages/platform.tsx

echo -e "\n========== product.tsx =========="
cat frontend/pages/product.tsx

echo -e "\n========== why-maple.tsx =========="
cat frontend/pages/why-maple.tsx

echo -e "\n========== DONE =========="
} > ui_dump.txt

wc -l ui_dump.txt
