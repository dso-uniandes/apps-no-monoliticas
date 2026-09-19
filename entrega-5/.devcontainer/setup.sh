#!/bin/bash

echo "[*] Installing Python dependencies..."
pip install -r requirements.txt
pip install -r hda-requirements.txt

echo "[✓] Dev container setup completed successfully."
echo "[i] No se construyen imágenes ni se levanta infraestructura en el setup."
