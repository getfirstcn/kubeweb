import urllib3
import certifi
http = urllib3.PoolManager(
    cert_file='/path/to/your/client_cert.pem',
    cert_reqs='CERT_REQUIRED',
    ca_certs='/path/to/your/certificate_bundle'

)
r = http.request('GET','http://www.baidu.com')
print(r.status)
print(r.data)