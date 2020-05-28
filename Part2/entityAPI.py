import requests
import xml.etree.ElementTree


def __entity__(xml_data):
    entity_response = xml.etree.ElementTree.fromstring(xml_data)
    reference = entity_response.find('.//{http://preservica.com/XIP/v6.0}Ref')
    title = entity_response.find('.//{http://preservica.com/XIP/v6.0}Title')
    security_tag = entity_response.find('.//{http://preservica.com/XIP/v6.0}SecurityTag')
    description = entity_response.find('.//{http://preservica.com/XIP/v6.0}Description')
    parent = entity_response.find('.//{http://preservica.com/XIP/v6.0}Parent')
    if hasattr(parent, 'text'):
        parent = parent.text
    else:
        parent = None

    fragments = entity_response.findall(
        './/{http://preservica.com/EntityAPI/v6.0}Metadata/{http://preservica.com/EntityAPI/v6.0}Fragment')
    metadata = {}
    for fragment in fragments:
        metadata[fragment.text] = fragment.attrib['schema']

    return {'reference': reference.text, 'title': title.text if hasattr(title, 'text') else "",
            'description': description.text if hasattr(description, 'text') else "",
            'security_tag': security_tag.text, 'parent': parent, 'metadata': metadata}

class EntityAPI:
    """
        A client library for the Preservica Repository web services Entity API
        https://us.preservica.com/api/entity/documentation.html


        Attributes
        ----------
        username : str
            Preservica account username, usually an email address
        password : str
            Preservica account password
        tenant : str
            Tenant name for the Preservica account
        server : str
            The URL of the Preservica instance

        Methods
        -------
        asset(reference):
            Fetches the main XIP attributes for an asset by its reference

        folder(reference):
            Fetches the main XIP attributes for a folder by its reference
        """

    def __init__(self, username, password, tenant, server):
        self.username = username
        self.password = password
        self.tenant = tenant
        self.server = server
        self.token = self.__token__()

    def __token__(self):
        response = requests.post(
            f'https://{self.server}/api/accesstoken/login?username={self.username}&password={self.password}&tenant={self.tenant}')
        if response.status_code == 200:
            return response.json()['token']
        else:
            print(f"new_token failed with error code: {response.status_code}")
            print(response.request.url)
            raise SystemExit

    class Entity:
        def __init__(self, reference, title, description, security_tag, parent, metadata):
            self.reference = reference
            self.title = title
            self.description = description
            self.security_tag = security_tag
            self.parent = parent
            self.metadata = metadata
            self.type = None

        def __str__(self):
            return f"Ref:\t\t\t{self.reference}\nTitle:\t\t\t{self.title}\nDescription:\t{self.description}" \
                   f"\nSecurity Tag:\t{self.security_tag}\nParent:\t\t\t{self.parent}\n\n"

        def __repr__(self):
            return f"Ref:\t\t\t{self.reference}\nTitle:\t\t\t{self.title}\nDescription:\t{self.description}" \
                   f"\nSecurity Tag:\t{self.security_tag}\nParent:\t\t\t{self.parent}\n\n"

    class Folder(Entity):
        def __init__(self, reference, title, description, security_tag, parent, metadata):
            super().__init__(reference, title, description, security_tag, parent, metadata)
            self.type = "SO"

    class Asset(Entity):
        def __init__(self, reference, title, description, security_tag, parent, metadata):
            super().__init__(reference, title, description, security_tag, parent, metadata)
            self.type = "IO"

    class PagedSet:
        def __init__(self, results, has_more, total, next_page):
            self.results = results
            self.has_more = has_more
            self.total = total
            self.next_page = next_page

        def __str__(self):
            return self.results.__str__()

    def metadata(self, uri):
        headers = {'Preservica-Access-Token': self.token}
        request = requests.get(uri, headers=headers)
        if request.status_code == 200:
            xml_response = str(request.content.decode('UTF-8'))
            entity_response = xml.etree.ElementTree.fromstring(xml_response)
            content = entity_response.find('.//{http://preservica.com/XIP/v6.0}Content')
            return xml.etree.ElementTree.tostring(content[0], encoding='utf8', method='xml').decode()
        elif request.status_code == 401:
            self.token = self.__token__()
            return self.metadata(uri)
        else:
            print(f"metadata failed with error code: {request.status_code}")
            print(request.request.url)
            raise SystemExit

    def asset(self, reference):
        headers = {'Preservica-Access-Token': self.token}
        request = requests.get(f'https://{self.server}/api/entity/information-objects/{reference}', headers=headers)
        if request.status_code == 200:
            xml_response = str(request.content.decode('UTF-8'))
            entity = __entity__(xml_response)
            a = self.Asset(entity['reference'], entity['title'], entity['description'], entity['security_tag'], entity['parent'], entity['metadata'])
            return a
        elif request.status_code == 401:
            self.token = self.__token__()
            return self.asset(reference)
        else:
            print(f"asset failed with error code: {request.status_code}")
            print(request.request.url)
            raise SystemExit

    def folder(self, reference):
        headers = {'Preservica-Access-Token': self.token}
        request = requests.get(f'https://{self.server}/api/entity/structural-objects/{reference}', headers=headers)
        if request.status_code == 200:
            xml_response = str(request.content.decode('UTF-8'))
            entity = __entity__(xml_response)
            f = self.Folder(entity['reference'], entity['title'], entity['description'], entity['security_tag'], entity['parent'],
                           entity['metadata'])
            return f
        elif request.status_code == 401:
            self.token = self.__token__()
            return self.folder(reference)
        else:
            print(f"folder failed with error code: {request.status_code}")
            print(request.request.url)
            raise SystemExit

    def children(self, reference, maximum=100, next_page=None):
        headers = {'Preservica-Access-Token': self.token}
        if next_page is None:
            if reference is None:
                request = requests.get(f'https://{self.server}/api/entity/root/children?start={0}&max={maximum}',
                                       headers=headers)
            else:
                request = requests.get(
                    f'https://{self.server}/api/entity/structural-objects/{reference}/children?start={0}&max={maximum}',
                    headers=headers)
        else:
            request = requests.get(next_page, headers=headers)
        if request.status_code == 200:
            xml_response = str(request.content.decode('UTF-8'))
            entity_response = xml.etree.ElementTree.fromstring(xml_response)
            childs = entity_response.findall('.//{http://preservica.com/EntityAPI/v6.0}Child')
            result = set()

            next_url = entity_response.find('.//{http://preservica.com/EntityAPI/v6.0}Next')
            total_hits = entity_response.find('.//{http://preservica.com/EntityAPI/v6.0}TotalResults')

            for c in childs:
                if c.attrib['type'] == 'SO':
                    f = self.Folder(c.attrib['ref'], c.attrib['title'], None, None, reference, None)
                    result.add(f)
                else:
                    a = self.Asset(c.attrib['ref'], c.attrib['title'], None, None, reference, None)
                    result.add(a)
            has_more = True
            url = None
            if next_url is None:
                has_more = False
            else:
                url = next_url.text
            ps = self.PagedSet(result, has_more, total_hits.text, url)
            return ps
        elif request.status_code == 401:
            self.token = self.__token__()
            return self.children(reference, maximum=maximum, next_page=next_page)
        else:
            print(f"children failed with error code: {request.status_code}")
            print(request.request.url)
            raise SystemExit
