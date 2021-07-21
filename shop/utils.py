from copy import deepcopy
from lxml.etree import iterparse
from pprint import pprint
import json
from dataclasses import dataclass
import requests
import os
from datetime import datetime

@dataclass
class Group:
    code: str
    name: str
    parent_code: str = None


class XmlParserPRODAT:
    """Парсер Файла PRODAT от Рyсского света

    Returns:
        [type]: [description]
    """
    default_data = dict(
        ProductName = "",
        ProductStatus = "",
        EAN = "",
        SenderPrdCode = "",
        ReceiverPrdCode = "",
        UOM = "",
        ItemsPerUnit = 0,
        Multiplicity = 0,
        ParentProdCode = "",
        ParentProdGroup = "",
        ProductGroup = "",
        VendorProdNum = "",
        Brand = "",
        Dimension = dict(),
        Features = [],
        ProductCode = '',
        # Video = ''
    )

    def __init__(self, file_name) -> None:
        self.file_name = file_name
        self.__context = None
        self.__result = dict()
        self.__groups = dict() # {'g_code':'ProdGroup'}
        self.__features = dict()  #  {'FeatureCode':{FeatureName:'f_name',FeatureUom: 'f_uom',FeatureValue:'f_value' }}

    def get_items(self) -> dict:

        return self.__result

    def get_groups(self) -> dict:
        """[summary]

        Returns:
            dict: {GRoupCode:Group(dataclass (code: str, name: str, parent: Group)), ...}}
        """
        return self.__groups
    
    def get_features(self):
        """[summary]

        Returns:
            dict: {'FeatureCode':
                    {'FeatureCode':code,
                    'FeatureName':name,
                    'FeatureUom':Uom,
                    'FeatureValue':value},
                    ...
                }
        """
        return self.__features

    def run(self):
        self.__context = self.__create_context()
        self.__fast_iter(self.__context)
        self.__parse_groups_and_features()

    def __parse_groups_and_features(self):
        for v in self.__result.values():
            group = Group(code=v.get('ParentProdCode'), name=v.get('ParentProdGroup'))
            child_group = Group(
                code=v.get('ProductCode'),
                name=v.get('ProductGroup'),
                parent_code=group.code
                )
            self.__groups[group.code] = group
            self.__groups[child_group.code] = child_group
            features = v.get('Features')
            for feauter in features:
                self.__features[feauter['FeatureCode']] = feauter

    def __create_context(self):
        return iterparse(self.file_name, tag='DocDetail', events = ('end', ))

    def __process_element(self, elem):
        self.elem_data = deepcopy(self.default_data)
        for child in elem:
            if child.tag in self.elem_data and child.tag != 'Dimension':
                self.elem_data[child.tag] = child.text
            elif child.tag == 'Dimension':
                self.elem_data['Dimension'][child.tag] = dict(
                    ((ch.tag, ch.text) for ch in child)
                    )
            elif child.tag == 'Weight':
                self.elem_data[child.tag] = dict(
                    ((ch.tag, ch.text) for ch in child)
                    )
            elif child.tag in ['RelatedProd', 'Analog']:
                self.elem_data[child.tag] = [ch.text for ch in child]
            elif child.tag.startswith('FeatureETIMDetails'):
                for ch in child:
                    self.elem_data['Features'].append(
                        dict( ((c.tag, c.text) for c in ch) )
                        )
            elif child.tag == 'Image':
                if not len(child):
                    continue
                self.elem_data['Image'] = child[0].text # [ x.text for x in child ][0]
            elif child.tag == 'Video':
                if not len(child):
                    continue
                self.elem_data['Video'] = child[0].text
        self.__result[self.elem_data["SenderPrdCode"]] = deepcopy(self.elem_data)

    def __fast_iter(self, context, *args, **kwargs):
        """
        http://lxml.de/parsing.html#modifying-the-tree
        Based on Liza Daly's fast_iter
        http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
        See also http://effbot.org/zone/element-iterparse.htm
        """
        for event, elem in context:

            self.__process_element(elem, *args, **kwargs)
            elem.clear()
            for ancestor in elem.xpath('ancestor-or-self::*'):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        del context


def download_image(url, path):
    if not url or url is None:
        return
    resp = requests.get(url)
    if resp.status_code != 200:
        return 
    if not isinstance(path, str):
        try:
            path = path()
        except Exception:
            path = create_path()
    try:
        os.makedirs(path)
    except FileExistsError:
        ...
    except Exception as e:
        print(f"Другая ошибка {e}")
    full_path = os.path.join(path, url.split('/')[-1])
    with open(full_path, 'wb') as fl:
        fl.write(resp.content)
    return full_path


def create_path():
    dt = datetime.now().strftime('%Y.%m.%d').split('.')
    return os.path.join(*dt)


if __name__ == '__main__':
    # print(create_path())
    # exit()
    # result = download_image(url = 'https://rs24.ru/ctlg/edi/DKC/119/11920/11920_2.jpeg', path=create_path)
    # print(result)
    # exit()
    fl_xml = 'trash_data\\data\\data.xml'
    parser = XmlParserPRODAT(fl_xml)
    parser.run()
    res = parser.get_items()
    groups = parser.get_groups()
