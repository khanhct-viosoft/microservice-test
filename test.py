from requests_toolbelt import MultipartEncoder
import requests

m = MultipartEncoder(
    fields={'yaml_file': ('Test.zip', open('Test.zip', 'rb'), 'text/plain')}
    )
r = requests.post('http://10.76.239.20:9090/tm/yardstick', data=m,
                  headers={'Content-Type': m.content_type})
