

import json
import requests
from flask import Flask, request
from generate_new_pts import GenerateNewPTs
import pickle
import os


app = Flask(__name__)


def test():
    with open('last_pt.pkl', 'rb') as fopen:
        pt = pickle.load(fopen)
        return pt


@app.route('/index.html', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        rdelt_name = request.values.get('delt_name')
        rsize = int(request.values.get('size'))
        gnpt = GenerateNewPTs()
        gnpt.logger.info('delt_name:'+rdelt_name+','+'size:'+str(rsize))
        ad_ids = gnpt.find_ads_in_report(rdelt_name)
        pts = []
        for ad_id in ad_ids:
            if len(pts) >= rsize:
                break
            orign_pt = gnpt.find_a_ads(ad_id)
            # orign_pt = test()
            if orign_pt is not None:
                # orign_pt = {'pt': orign_pt}
                res = requests.post(gnpt.get_prob_address,
                                    data=json.dumps({'type': 'density', 'pt': orign_pt['pt']}), headers={'Content-Type': "application/json"})
                # res = requests.post('http://172.20.150.160:5000/', data=json.dumps({'type': 'density', 'pt': orign_pt['pt']}),
                #                     headers={'Content-Type': "application/json"})
                value_prob = eval(res.text)
                pt = gnpt.main(orign_pt, value_prob, int(os.environ['num']))
                pts.extend(pt)
        return json.dumps(pts[:rsize])
    else:
        # kv = json.loads(request.data)
        # gnpt = GenerateNewPTs()
        # orign_pt = test()
        # orign_pt = {'pt': orign_pt}
        # res = requests.post('http://172.20.150.160:5000/', data=json.dumps({'type': 'density', 'pt': orign_pt['pt']}),
        #                     headers={'Content-Type': "application/json"})
        # value_prob = eval(res.text)
        # if 'number' in kv:
        #     pt = gnpt.main(orign_pt, value_prob, kv['number'])
        # else:
        #     pt = gnpt.main(orign_pt, value_prob)
        # return json.dumps(pt)
        return 'POST!!!'


if __name__ == '__main__':
    app.run('0.0.0.0', port=55555)

