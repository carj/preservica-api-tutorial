
from EntityAPI.entityAPIP import EntityAPI

entity = EntityAPI(username="test@test.com", password="ABC1234", tenant="TEN", server="us.preservica.com")

asset = entity.asset("6a596701-75ae-45b7-933d-355787e25a28")
print(asset.title)
print(asset.description)
print(asset.security_tag)
print(asset.parent)

folder = entity.folder(asset.parent)
print(folder.title)
print(folder.description)
print(folder.parent)

while folder.parent is not None:
   folder = entity.folder(folder.parent)
   print(folder.title)


for metadata in asset.metadata:
    print(entity.metadata(metadata))


next_page = None
while True:
    root_folders = entity.children(None, maximum=10, next_page=next_page)
    for e in root_folders.results:
        print(f'{e.title} :  {e.reference}')
    if not root_folders.has_more:
        break
    else:
        next_page = root_folders.next_page

