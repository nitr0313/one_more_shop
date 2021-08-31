from copy import deepcopy
import decimal
from lxml.etree import LxmlError, iterparse, LxmlSyntaxError, parse
from pprint import pprint
import json
from dataclasses import dataclass
import requests
import os
from datetime import datetime, time
from abc import ABC
from decimal import Decimal
from typing import Tuple
import csv


@dataclass
class Group:
    code: str
    title: str
    parent_code: str = None
    etim: str = None

    def __hash__(self) -> int:
        return int(self.code)

@dataclass(frozen=False)
class ItemPrice:
    SenderPrdCode: str
    ProductName: str
    ItemsPerUnit: int
    UOM: str
    QTY: int
    Price2: Decimal
    RetailPrice: Decimal
    QtyLots: list = lambda: list()
    _pk: int = None

    def __post_init__(self):
        object.__setattr__(self, "ItemsPerUnit", int(self.ItemsPerUnit))
        object.__setattr__(self, "QTY", Decimal(self.QTY))
        object.__setattr__(self, "Price2", Decimal(self.Price2))
        object.__setattr__(self, "RetailPrice", Decimal(self.RetailPrice))
        if self.QtyLots is not None:
            object.__setattr__(self, "QtyLots", self.QtyLots.split(";"))
    
    @property
    def pk(self) -> int:
        return self._pk

    @pk.setter
    def pk(self, obj: int) -> None:
        self._pk = int(obj)

    @property
    def code(self) -> str:
        return self.SenderPrdCode
    
    @property
    def price(self) -> Decimal:
        return self.Price2

    @property
    def base_price(self) -> Decimal:
        return self.RetailPrice 

    @property
    def quantity_lots(self) -> list:
        return self.QtyLots

    @property
    def quantity_min(self) -> int:
        return self.ItemsPerUnit

    @property
    def quantity_unit(self) -> str:
        return self.UOM

    @property
    def quantity(self) -> str:
        return self.QTY


    def as_dict(self) -> dict:
        return dict(
            code = self.SenderPrdCode,
            title = self.ProductName,
            quantity_min = int(self.ItemsPerUnit),
            quantity_unit = self.UOM,
            quantity = int(self.QTY),
            price = Decimal(self.Price2),
            base_price = Decimal(self.RetailPrice),
            quantity_lots = self.QtyLots,
        )


class CsvParser:

    def __init__(self, file_name) -> None:
        self.file_name = file_name
        self.lvl0 = set()
        self.lvl1 = set()
        self.lvl2 = set()
        self.lvl3 = set()
        self.lvl4 = set()

    def run(self):
        with open(self.file_name, 'r', newline='', encoding='1251') as fl:
            csv_d = csv.DictReader(fl,delimiter=';')
            for line in csv_d.reader:
                # print(line) # ['2', 'Электроустановочные изделия','24', 'Электроустановочные устройства различного назначения', '426', '', '', '', '', 'EC002247', 'Элемент программы для людей с ограниченными возможностями для электроустановочных устройств']
                self.processing(line)

    def processing(self, line):
        lvl0 = line[0:2] # '2', 'Электроустановочные изделия'
        lvl1 = line[2:4] # '24', 'Электроустановочные устройства различного назначения'
        lvl2 = line[4:6] # '426', ''
        lvl3 = line[6:8] # '', ''
        lvl4 = line[8:] # '', 'EC002247', 'Элемент программы для людей с ограниченными возможностями для электроустановочных устройств'
        etim = None
        parent_code = None
        for elem, lvl in zip((lvl0, lvl1, lvl2, lvl3), (self.lvl0, self.lvl1, self.lvl2, self.lvl3)):
            if elem[1] == '':                
                etim = lvl4[-2]
                title = lvl4[-1]
                lvl4 = []
                lvl.add(Group(code=elem[0], title=title, parent_code=parent_code, etim=etim))
                break
            lvl.add(Group(code=elem[0], title=elem[1], parent_code=parent_code, etim=etim))
            parent_code = elem[0]
        if lvl4:
            code = lvl4[-3]
            etim = lvl4[-2]
            title = lvl4[-1]
            self.lvl4.add(Group(code=code, title=title, parent_code=parent_code, etim=etim))

    
    def get_result(self):
        result = dict(
            lvl0=self.lvl0,
            lvl1=self.lvl1,
            lvl2=self.lvl2,
            lvl3=self.lvl3,
            lvl4=self.lvl4,
        )
        return result

class RSXmlParser(ABC):
    
    def __init__(self, file_name) -> None:
        self.file_name = file_name
        self.__context = None
        self.__result = dict()

    def get_items(self) -> dict:
        return self.__result

    def get_result(self) -> dict:
        return self.__result

    def run(self):
        self.__context = self.__create_context()
        return self.__context
    
    def __create_context(self):
        return iterparse(self.file_name, tag='DocDetail', events = ('end', ))

    def _fast_iter(self, context, process, *args, **kwargs):
        """
        http://lxml.de/parsing.html#modifying-the-tree
        Based on Liza Daly's fast_iter
        http://www.ibm.com/developerworks/xml/library/x-hiperfparse/
        See also http://effbot.org/zone/element-iterparse.htm
        """
        for event, elem in context:
            process(elem, *args, **kwargs)
            elem.clear()
            for ancestor in elem.xpath('ancestor-or-self::*'):
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        del context

    def __process_element(self, elem):
        raise NotImplementedError


class RSXmlParserPricat(RSXmlParser):
    """
        <EAN />
        <SenderPrdCode>1401410</SenderPrdCode>
        <ReceiverPrdCode />
        <ProductName>Кабель КПСЭнг(А)-FRHF 1х2х0.75 300В (бухта) (м) ИВКЗ 00-00014448</ProductName>
        <UOM>MTR</UOM>
        <AnalitCat>НОВ</AnalitCat>
        <ItemsPerUnit>1</ItemsPerUnit>
        <QTY>7699.0000</QTY>
        <SumQTY>7699.0000</SumQTY>
        <ProductStatus>Активно</ProductStatus>
        <Brand>ИВКЗ</Brand>

        <Price2>27.00</Price2>
        <CustPrice>22.50</CustPrice>
        <RetailPrice>27.00</RetailPrice>
        <RetailCurrency>rub</RetailCurrency>
        
        <VendorProdNum>00-00014448</VendorProdNum>
        <SupOnhandDetail />
        <Multiplicity>1</Multiplicity>
        <QtyLots>15;29;55;7600</QtyLots>
        <ItemId>2756322</ItemId>

    Args:
        RSXmlParser ([type]): [description]
    """

    default_data = dict(
        SenderPrdCode = "",
        ProductName = "",
        ItemsPerUnit = "",
        UOM = "",
        QTY = "",
        Price2 = "",
        RetailPrice = "",
        QtyLots = "",
    )
    def __init__(self, file_name):
        super().__init__(file_name)
        self.__result = dict()

    def run(self):
        self.__context = super().run()
        super()._fast_iter(self.__context, process=self.__process_element)

    def __process_element(self, elem):
        self.elem_data = deepcopy(self.default_data)
        for child in elem:
            if child.tag in self.elem_data:
                self.elem_data[child.tag] = child.text
        self.__result[self.elem_data["SenderPrdCode"]] = ItemPrice(**self.elem_data)
    
    def get_result(self) -> dict:
        return dict(
            prices=self.__result
        )


class RSXmlParserPRODAT(RSXmlParser):
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
        super().__init__(file_name=file_name)
        self.__result = dict()
        self.__groups = dict() # {'g_code':'ProdGroup'}
        self.__features = dict()  #  {'FeatureCode':{FeatureName:'f_name',FeatureUom: 'f_uom',FeatureValue:'f_value' }}

    def run(self):
        self.__context = super().run()
        super()._fast_iter(self.__context, process=self.__process_element)
        self.__parse_groups_and_features()

    def __parse_groups_and_features(self):
        for v in self.__result.values():
            group = Group(code=v.get('ParentProdCode'), title=v.get('ParentProdGroup'))
            child_group = Group(
                code=v.get('ProductCode'),
                title=v.get('ProductGroup'),
                parent_code=group.code
                )
            self.__groups[group.code] = group
            self.__groups[child_group.code] = child_group
            features = v.get('Features')
            for feauter in features:
                self.__features[feauter['FeatureCode']] = feauter

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
                        dict( ((c.tag, c.text) for c in ch) ))
            elif child.tag == 'Image':
                if not len(child):
                    continue
                self.elem_data['Image'] = child[0].text # [ x.text for x in child ][0]
            elif child.tag == 'Video':
                if not len(child):
                    continue
                self.elem_data['Video'] = child[0].text
        self.__result[self.elem_data["SenderPrdCode"]] = deepcopy(self.elem_data)

    def get_result(self) -> dict:
        return dict(
            groups=self.__groups,
            items=self.__result,
            features=self.__features
        )


def download_image(url, path):
    if not url or url is None:
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
    if os.path.isfile(full_path) and os.path.exists(full_path):
        # print(f'Картинка уже загружена: {full_path}')
        return full_path
    resp = requests.get(url)
    if resp.status_code != 200:
        return 
    with open(full_path, 'wb') as fl:
        fl.write(resp.content)
    return full_path


def timeit(foo):
    def wrapped(*args, **kwargs):
        start = datetime.now()
        res = foo(*args, **kwargs)
        print(f'time of execute {foo} = {datetime.now() - start}')
        return res
    return wrapped


@timeit
def get_xml_parser(data_file: str):
    """
    Выбирает парсер для конкретного файла


    Args:
        data_file (str): Файл в формате XML

    Returns:
        [tuple]: кортеж из двух значений - первое тип докуммента, второе парсер для его обработки
    """
    xml_types = dict(
        PRODAT=RSXmlParserPRODAT,
        PRICAT=RSXmlParserPricat
    )
    try:
        context = list(iterparse(data_file, tag='DocType', events = ('end', )))
        xml_type = context[0][1].text
        xml_parser = xml_types.get(xml_type, None)
        return xml_type, xml_parser(file_name=data_file)
    except FileNotFoundError:
        print(f'Файл {data_file} не найден')
    except LxmlSyntaxError:
        print(f'Ошибка синтаксиса xml, не тот файл')
    except (StopIteration, IndexError, TypeError) as e:
        print(f'Значение не найдено, не тот файл {e}')
    except Exception as e:
        print(f'Не предвиденная ошибка {e}')
    return None, None


@timeit
def get_parser(data_file: str):
    """
    Выбирает парсер для конкретного файла
    Args:
        data_file (str): Файл в формате XML or csv

    Returns:
        [tuple]: кортеж из двух значений - первое тип докуммента, второе парсер для его обработки
    """
    parser_type = dict(
        PRODAT=RSXmlParserPRODAT,
        PRICAT=RSXmlParserPricat,
        CAT_CSV=CsvParser,
    )
    if data_file.endswith('csv'):
        return 'CAT_CSV', parser_type['CAT_CSV'](file_name=data_file)
    try:
        index = 0
        for line in open(data_file, 'r'):
            # line = line.decode("utf-8")
            if 'DocType' in line:
                break
            if index > 5:
                raise StopIteration
            index += 1
        xml_type: str = line.strip()[9:-10]
        xml_parser = parser_type.get(xml_type, None)
        return xml_type, xml_parser(file_name=data_file)
    except FileNotFoundError:
        print(f'Файл {data_file} не найден')
    except (StopIteration, IndexError, TypeError) as e:
        print(f'Значение не найдено, не тот файл {e}')
    except Exception as e:
        print(f'Не предвиденная ошибка {e}')
    return None, None


def create_path():
    dt = datetime.now().strftime('%Y.%m.%d').split('.')
    return os.path.join(*dt)


if __name__ == '__main__':
    # print(create_path())
    # exit()
    # result = download_image(url = 'https://rs24.ru/ctlg/edi/DKC/119/11920/11920_2.jpeg', path=create_path)
    # print(result)
    # exit()
    # fl_xml = 'trash_data\\data\\data.xml'
    # print(get_xml_parser2(fl_xml))
    # fl_xml = 'trash_data\\data\\pricat_.xml'
    # print(get_xml_parser2(fl_xml))
    # exit()
    parser = CsvParser('trash_data\\categores.csv')
    parser.run()
    result = parser.get_result()
    pprint(result)
    # parser = RSXmlParserPRODAT(fl_xml)
    # parser.run()
    # res = parser.get_items()
    # groups = parser.get_groups()
