

def restart_server():
    url = 'http://localhost:5000/api/system/restart'
    requests.post(url)