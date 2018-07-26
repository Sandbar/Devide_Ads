

import json
import requests
from flask import Flask, request
import pandas as pd


app = Flask(__name__)


def test():
    behaviors = pd.read_csv('behaviors_id_count.txt')
    behaviors.columns = ['id', 'count']
    behaviors['rate'] = behaviors['count'].apply(lambda x: x / sum(behaviors['count']))
    behaviors['sign'] = 1
    rate = {}
    com_rate = {}
    for index in range(len(behaviors)):
        rate[behaviors.iloc[index]['id']] = behaviors.iloc[index]['rate']
    com_rate['behaviors'] = rate
    interests = pd.read_csv('interests_id_count.txt')
    interests.columns = ['id', 'count']
    interests['rate'] = interests['count'].apply(lambda x: x / sum(interests['count']))
    rate = {}
    for index in range(len(interests)):
        rate[interests.iloc[index]['id']] = interests.iloc[index]['rate']
    com_rate['interests'] = rate
    return com_rate


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        kv = json.loads(request.data)
        com_features = test()
        return json.dumps(com_features)
    else:
        # return []
        return 'Second NO POST!!!!'


if __name__ == '__main__':
    app.run('0.0.0.0', port=44444)
    # test()
