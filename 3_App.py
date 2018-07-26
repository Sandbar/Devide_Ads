
import requests
import json

if __name__ == '__main__':
    condition = {'delt_name': 'bet4_ios_us', 'number': 5}
    res = requests.post('http://0.0.0.0:55555/', data=json.dumps(condition),
                        headers={'Content-Type': "application/json"})
    print(res.text)

