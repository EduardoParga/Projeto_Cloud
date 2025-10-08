#!/usr/bin/env bash
set -euo pipefail

# short wait for services
sleep 5

echo "[APP] running extract.py"
python extract.py || { echo "[APP] extract.py failed"; exit 1; }

echo "[APP] running extract_xml.py"
python extract_xml.py || { echo "[APP] extract_xml.py failed"; exit 1; }

echo "[APP] pipeline finished"
exit 0