import json
import sys
import os
from slugify import slugify

sys.path.append(os.getcwd())

with open('./data/all.json') as json_file:
    items = json.load(json_file)
    for i in items:
        out_file = slugify(i['Tên Sản phẩm'])
        content = ''
        for k, v in i.items():
            content += f"{k}: {v}\n"

        with open(f'./data/{out_file}.txt', 'w') as f:
            f.write(content)
            f.close()