import requests
import os
import sys
from urllib.parse import urljoin
base='http://127.0.0.1:5000'
s=requests.Session()
poss=['password','sam','1234','test123','student','password123','sam123','123456']
success=False
for pwd in poss:
    r=s.post(urljoin(base,'/login'), data={'username':'sam','password':pwd}, allow_redirects=False)
    if r.status_code in (302,303) and 'dashboard' in r.headers.get('Location',''):
        print('PASS', pwd)
        success=True
        break
if not success:
    print('NOLOGIN')
    sys.exit(0)
file_path='faces/sam_20260306_074631.jpg'
if not os.path.exists(file_path):
    print('MISSING', file_path)
    sys.exit(0)
with open(file_path,'rb') as f:
    files={'face':('sam_face.jpg', f, 'image/jpeg')}
    r=s.post(urljoin(base,'/enroll_face'), files=files, allow_redirects=False)
print('STATUS', r.status_code)
print('LOCATION', r.headers.get('Location'))
print('TEXT', r.text[:400])
