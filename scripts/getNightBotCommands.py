import requests, json
from time import sleep

# THE EMPTY STRINGS NEED TO BE FILLED OUT BY YOU, YOU CAN GET THIS INFO FROM YOUR NIGHTBOT PANNEL, APPLICATION SETTINGS
client_id = ''
client_secret = ''




def getToken():
    payload = {
                'client_id': '{0}'.format(client_id),
                'client_secret': '{0}'.format(client_secret),
                'grant_type': 'client_credentials',
                'scope': 'commands'
            }
    response = requests.post('https://api.nightbot.tv/oauth2/token', data=payload)

    print(response.text)
    pure = json.loads(response.text)
    
    print("INFO: NightBot Token received.")
    return [pure['access_token']]
    
def revokeToken(k):
    payload = {
                'token':k
            }
    
    response = requests.post('https://api.nightbot.tv/oauth2/token/revoke', data=payload)
    
    print("INFO: NightBot Token deleted")
    
token = getToken()

print(token[0])



s = requests.Session()
s.headers.update({'Authorization' : 'Bearer ' + token[0]})
response = s.get('https://api.nightbot.tv/1/commands')


print(response.text)

sleep(2)

revokeToken(token)