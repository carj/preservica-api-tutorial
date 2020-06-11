
from EntityAPI.entityAPI import EntityAPI
import csv
from xml.etree import ElementTree


entity = EntityAPI(username="test@test.com", password="123444", tenant="PREVIEW", server="preview.preservica.com")


parent = "249c989a-84b2-467a-819a-941d8bee4976"
with open('folders.csv', newline='') as csvfile:
      reader = csv.reader(csvfile)
      for row in reader:
            entity.create_folder(row[0], row[1], row[2], parent)


folder = entity.create_folder("title", "description", "open", "249c989a-84b2-467a-819a-941d8bee4976")
folder.title = "new title"
entity.save(folder)

folder = entity.folder("0b0f0303-6053-4d4e-a638-4f6b81768264")
folder.title = "New Folder Title"
folder.description = "New Folder Description"
folder = entity.save(folder)
entity.add_identifier(folder, "ISBN", "122333333")

asset = entity.asset("9bad5acf-e7ce-458a-927d-2d1e7f15974d")
asset.title = "New Asset Title"
asset.description = "New Asset Description"
asset = entity.save(asset)


asset = entity.asset("9bad5acf-e7ce-458a-927d-2d1e7f15974d")
entity.add_identifier(asset, "ISBN", "978-3-16-148410-0")
entity.add_identifier(asset, "DOI", "https://doi.org/10.1109/5.771073")
entity.add_identifier(asset, "URN", "urn:isan:0000-0000-2CEA-0000-1-0000-0000-Y")

e = entity.identifier("ISBN", "978-3-16-148410-0")
for e in entity.identifier("ISBN", "978-3-16-148410-0"):
      print(e.type, e.reference, e.title)



folder = entity.folder("723f6f27-c894-4ce0-8e58-4c15a526330e")

xml = "<person:Person  xmlns:person='https://www.person.com/person'>" \
      "<person:Name>James Carr</person:Name>" \
      "<person:Phone>01234 100 100</person:Phone>" \
      "<person:Email>test@test.com</person:Email>" \
      "<person:Address>Abingdon, UK</person:Address>" \
      "</person:Person>"

folder = entity.add_metadata(folder, "https://www.person.com/person", xml)

folder = entity.folder("723f6f27-c894-4ce0-8e58-4c15a526330e")   # call into the API

for url, schema in folder.metadata.items():
      if schema == "https://www.person.com/person":
            xml_string = entity.metadata(url)                    # call into the API
            xml_document = ElementTree.fromstring(xml_string)
            postcode = ElementTree.Element('{https://www.person.com/person}Postcode')
            postcode.text = "OX14 3YS"
            xml_document.append(postcode)
            xml_string = ElementTree.tostring(xml_document, encoding='UTF-8', xml_declaration=True).decode("utf-8")
            entity.update_metadata(folder, schema, xml_string)   # call into the API


with open("C:\\DublinCore.xml", 'r', encoding="UTF-8") as md:
      asset = entity.add_metadata(asset, "http://purl.org/dc/elements/1.1/", md)
