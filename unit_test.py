from requests_toolbelt import MultipartEncoder
import requests

m = MultipartEncoder(
    fields={'yaml_file': ('Test.zip', open('Test.zip', 'rb'), 'text/plain')}
    )
#r = requests.post('http://10.70.8.120:9090/tm/yardstick', data=m,
#                  headers={'Content-Type': m.content_type})

s = requests.Session()
a = requests.adapters.HTTPAdapter(max_retries=3)
s.mount('http://', a)
r = s.post('http://0.0.0.0:9090/tm/yardstick', data=m, headers={'Content-Type': m.content_type})
print r.status_code
if r.status_code != 200:
    raise ValueError('Fail Test')