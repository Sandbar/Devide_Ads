

import json
import requests
from flask import Flask, request
from generate_new_pts import GenerateNewPTs


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        kv = json.loads(request.data)
        gnpt = GenerateNewPTs()
        if 'delt_name' in kv:
            orign_pt = gnpt.find_a_ads(kv['delt_name'])
        else:
            orign_pt = gnpt.find_a_ads()
        res = requests.post('http://0.0.0.0:44444/', data=json.dumps(orign_pt), headers={'Content-Type': "application/json"})
        value_prob = eval(res.text)
        if 'number' in kv:
            pt = gnpt.main(orign_pt, value_prob, kv['number'])
        else:
            pt = gnpt.main(orign_pt, value_prob)
        return json.dumps(pt)
    else:
        return 'NO POST!!!!'


if __name__ == '__main__':
    app.run('0.0.0.0', port=55555)

