from xml.etree import ElementTree
import requests


def new_token(username, password, tenant, server):
    response = requests.post(
        f'https://{server}/api/accesstoken/login?username={username}&password={password}&tenant={tenant}')
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"new_token failed with error code: {response.status_code}")
        print(response.request.url)
        raise SystemExit


def get_asset_title(server, token, ref):
    headers = {'Preservica-Access-Token': token}
    io_request = requests.get(f'https://{server}/api/entity/information-objects/{ref}', headers=headers)
    if io_request.status_code == 200:
        xml_response = str(io_request.content.decode('UTF-8'))
        entity_response = ElementTree.fromstring(xml_response)
        title = entity_response.find('.//{http://preservica.com/XIP/v6.0}Title')
        description = entity_response.find('.//{http://preservica.com/XIP/v6.0}Description')
        return title.text, description.text
    else:
        print(f"get_asset failed with error code: {io_request.status_code}")
        print(io_request.request.url)
        raise SystemExit


if __name__ == "__main__":
    username = "test@test.com"
    password = "xxx"
    tenant = "TEN"
    server = "us.preservica.com"
    accessToken = new_token(username, password, tenant, server)
    asset = get_asset_title(server, accessToken, "6a596701-75ae-45b7-933d-355787e25a28")
    print("Title: " + asset[0])
    print("Description: " + asset[1])
