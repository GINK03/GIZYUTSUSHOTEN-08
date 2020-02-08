#!/usr/bin env python3
import shutil
import sys
import re
from pathlib import Path
import os
# 参考: https://note.nkmk.me/mac-pandoc-markdown-pdf-japanese/
# 参考2: https://weasyprint.readthedocs.io/en/stable/install.html
# 参考3: https://gist.github.com/dashed/6714393#file-github-pandoc-css
# 参考4: https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-printToPDF

FILE = Path(__name__).name
TOP_FOLDER = Path(__name__).resolve().parent
# 1. pandocでhtmlを作成
os.system(f"""pandoc \
  -s README01.md \
  -f markdown \
  # -t epub3 \
  --metadata title="Practical Data Science & Engineering Vol.1" \
  -c {TOP_FOLDER}/var/github-pandoc.css -o \
  {TOP_FOLDER}/var/output.html""")

lines = []
with open(f'{TOP_FOLDER}/var/output.html') as fp:
    for line in fp:
        line = line.strip()

        if '<style>' in line:
            print('try rewrite entities..')
            lines.append(line)
            lines.append('html * {font-family: YuMincho !important; }')
        elif 'data-align="center"' in line:
            line = re.sub(r'data-align', 'align', line)
            lines.append(line)
        elif '<body>' in line:
            lines.append(line)
            #lines.append("<header>C</header><footer>B</footer>")

        else:
            lines.append(line)

rewrite_html = '\n'.join(lines)
with open(f'{TOP_FOLDER}/var/output_re_01.html', 'w') as fp:
    fp.write(rewrite_html)

PORT = 9222
os.system(f'{TOP_FOLDER}/util/print-via-chrome.js 9222 {TOP_FOLDER}/var/output_re_01.html {TOP_FOLDER}/var/output.pdf')


#chrome_path = shutil.which('google-chrome')
#if chrome_path is None:
#    chrome_path = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'
#os.system(f'{chrome_path} --headless --print-to-pdf="var/output.pdf" var/output_re_01.html')

if '--pdf' in sys.argv:
    os.system('cat var/output_re_01.html | weasyprint - var/output.pdf -s var/github-pandoc.css')
