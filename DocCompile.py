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
# pandocでhtmlを作成

import glob

for fn in glob.glob(f'{TOP_FOLDER}/markdowns/*.md'):
    NAME = Path(fn).name
    NAME_NO_SUFFIX = re.sub(r'.md', '', NAME)

    os.system(f"""pandoc \
      -s {TOP_FOLDER}/markdowns/{NAME} \
      -f markdown \
      --metadata title="Practical Data Science & Engineering Vol.1" \
      -c {TOP_FOLDER}/var/github-pandoc.css \
      -o {TOP_FOLDER}/var/{NAME_NO_SUFFIX}.html""")
    #print(f"""pandoc -s {TOP_FOLDER}/markdowns/{NAME} -f markdown --metadata title="Practical Data Science & Engineering Vol.1" -c {TOP_FOLDER}/var/github-pandoc.css -o {TOP_FOLDER}/var/{NAME_NO_SUFFIX}.html""")
    lines = []

    in_div = False
    with open(f'{TOP_FOLDER}/var/{NAME_NO_SUFFIX}.html') as fp:
        for line in fp:
            line = line.strip()
            
            if '<div' in line:
                in_div = True
            if in_div and "src" in line and "img" in line:
                line = line.replace('<pre>', '')
                line = line.replace('<code>', '')
                line = line.replace('</pre>', '')
                line = line.replace('</code>', '')
                line = line.replace('&lt;', '<')
                line = line.replace('&quot;', '"')
                line = line.replace('&gt;', '>')
                line = re.sub(r'data-align', 'align', line)
                lines.append(line)
            elif '<style>' in line:
                print('try rewrite entities..')
                lines.append(line)
                lines.append('html * {font-family: YuMincho !important; }')
            elif 'data-align="center"' in line:
                line = re.sub(r'data-align', 'align', line)
                lines.append(line)
            elif '<body>' in line:
                lines.append(line)
                # lines.append("<header>C</header><footer>B</footer>")
            else:
                lines.append(line)
            
            if '</div>' in line:
                in_div = False

    rewrite_html = '\n'.join(lines)
    with open(f'{TOP_FOLDER}/var/{NAME_NO_SUFFIX}_01.html', 'w') as fp:
        fp.write(rewrite_html)

    PORT = 9222
    if '--pdf' in sys.argv:
        os.system(f'{TOP_FOLDER}/util/print-via-chrome.js 9222 {TOP_FOLDER}/var/{NAME_NO_SUFFIX}_01.html {TOP_FOLDER}/var/{NAME_NO_SUFFIX}.pdf')

