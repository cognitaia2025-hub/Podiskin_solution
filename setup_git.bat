@echo off
cd /d "C:\Users\Salva\OneDrive\Escritorio\PodoskiSolution"

echo === Agregando archivos ===
git add .

echo.
echo === Estado actual ===
git status

echo.
echo === Haciendo commit ===
git commit -m "Initial commit"

echo.
echo === Agregando remoto ===
git remote add origin https://github.com/cognitaia2025-hub/Podiskin_solution.git

echo.
echo === Cambiando a rama main ===
git branch -M main

echo.
echo === Subiendo a GitHub ===
git push -u origin main

pause
