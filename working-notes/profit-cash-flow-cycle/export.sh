#!/bin/zsh
# Rebuilds the SVGs, then exports PNG (2x) and PDF of each using headless Chrome.
cd "$(dirname "$0")"
python3 build.py
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for spec in "cycle-16x9 1920 1080" "cycle-square 1080 1080"; do
  set -- ${=spec}
  name=$1 w=$2 h=$3
  cat > "_$name.html" <<EOF
<!doctype html><meta charset="utf-8"><style>@page{size:${w}px ${h}px;margin:0}html,body{margin:0;padding:0}img{display:block;width:${w}px;height:${h}px}</style><img src="$name.svg">
EOF
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --window-size=$w,$h --screenshot="$PWD/$name.png" "file://$PWD/_$name.html" 2>/dev/null
  "$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$PWD/$name.pdf" "file://$PWD/_$name.html" 2>/dev/null
  rm "_$name.html"
done
ls -la *.png *.pdf
