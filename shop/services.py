from decimal import Decimal
import os
from shop.utils import download_image
from .models import Category, Item, SpecItem, SpecValue
from .utils import timeit, ItemPrice
from django.db.models import Q
from threading import Thread


@timeit
def create_categories(categories: dict):
    """Создание Категорий и подкатегорий
    Args:
        categories ([dict]): {GRoupCode:Group(dataclass (code: str, title: str, parent: Group))
    """
    # if not Category.objects.filter(title='Главная', code=0).exists():
    #     start_group = Category(title='Главная')
    #     start_group.save()
    # else:
        # start_group = Category.objects.get(title='Главная')
    print(f"Создание категорий - ВСЕГО {len(categories)} шт")
    exists_categories = Category.objects.all().values_list('code', flat=True)
    for code, group in categories.items():
        if code not in exists_categories:
            if group.parent_code and group.parent_code is not None and group.parent_code not in exists_categories:
                cat = Category(title=categories[group.parent_code].title,
                    code=group.parent_code,
                    parent=None)
                cat.save()
            cat = Category(title=group.title,
                    code=group.code,
                    parent=None if group.parent_code is None else Category.objects.get(code=group.parent_code))
            cat.save()

@timeit
def create_categories_from_csv(categories: dict):
    """Создает категории из dict

    Args:
        categories (dict): DICT(lvl0:[cat1,cat2,...], lvl1:... )
    """
    for lvl, groups in categories.items():
        print(lvl)
        exists_categories = Category.objects.all()
        for group in groups:
            if exists_categories.filter(code=group.code).exists():
                if  group.etim is not None:
                    cat = exists_categories.get(code=group.code)
                    cat.etim = group.etim
                    cat.save()
                continue
            Category.objects.create(
                title=group.title,
                code=group.code,
                parent=exists_categories.get(code=group.parent_code)
                    if group.parent_code is not None else None,
                etim=group.etim
                )


@timeit
def create_specs(specs: dict):
    """Создание характеристик товаров

    Args:
        specs (dict): [description]
    """
    print(f"Создание характеристик - ВСЕГО {len(specs)} шт")
    exists_specs = SpecItem.objects.all().values_list('code', flat=True)
    for code, feature in specs.items():
        if code not in exists_specs:
            spec = SpecItem(
                code=feature['FeatureCode'],
                title=feature['FeatureName'],
                uom=feature['FeatureUom'] if feature['FeatureUom'] is not None else ""
                )
            spec.save()

@timeit
def create_items(items: dict, new_categories:bool=False):
    """Создание товаров

    Args:
        items (dict): [description]
    """
    print(f"Создание товаров - ВСЕГО {len(items)} шт")
    items_for_create = []
    exists_items = Item.objects.all().values_list('code', flat=True)
    undefine_cat = Category.objects.get(code="0")
    all_cats = Category.objects.filter(etim__isnull=False)
    for item_code, item_info in items.items():
        if item_code in exists_items:
            continue 
        try:
            cat = all_cats.get(etim=item_info['ProductCode'])
        except Category.DoesNotExist:
            print(f"Ошибка нет такой категории: etim={item_info['ProductCode']}, code={item_info['SenderPrdCode']}")
            cat = undefine_cat
        file_path = os.path.join('media', 'items', item_info['SenderPrdCode'])
        image_url = item_info.get('Image', False)
        image_path = download_image(image_url, path=file_path)
        if image_path is not None:
            image_path = os.path.join(*image_path.split('\\')[1:])
        items_for_create.append(Item(
                        code=item_info['SenderPrdCode'],
                        category=cat,
                        title=item_info['ProductName'],
                        description='',
                        price=Decimal('0.0'),
                        base_price=Decimal('0.0'),
                        photo=image_path,
                        in_stock=True if item_info['ProductStatus'] == 'Активно' else False,
                        on_delete = False,
                        quantity_min=item_info["ItemsPerUnit"],
                        quantity_unit=item_info['UOM'],
                        brand=item_info['Brand']
                    ))
        # item.save()
         # ПОдключение характеристик
    Item.objects.bulk_create(items_for_create)

#@timeit
# def add_item_specs(items: dict):
#     from hashlib import md5
#     print(f"Создание характеристик товаров - ВСЕГО товаров {len(items)} шт\n \
#             Характеристик на товар в среднем 10-13")

#     items_in_db = Item.objects.filter(code__in=items.keys())
#     count_items = items_in_db.count()
#     exists_spec_values = set(SpecValue.objects.all().values_list('item', 'spec_item__code'))
#     all_specs = SpecItem.objects.all()
#     spec_objects = list()
#     for item in items_in_db:
#         temp_objects = [
#             SpecValue(
#                 item=item,
#                 spec_item=all_specs.get(code=spec['FeatureCode']),
#                 value=spec['FeatureValue'] if spec['FeatureValue'] is not None else ""
#                 )
#             for spec in items[item.code]["Features"] 
#             if (item.pk, spec['FeatureCode']) not in exists_spec_values
#         ]
        

#         # for spec in items[item.code]["Features"]:
#         #     if (item.pk, spec['FeatureCode']) in exists_spec_values:
#         #         continue
#         #     spec_item = all_specs.get(code=spec['FeatureCode'])
#         #     spec_value = SpecValue(
#         #         item=item,
#         #         spec_item=spec_item,
#         #         value=spec['FeatureValue'] if spec['FeatureValue'] is not None else ""
#         #         )
#         #     spec_objects.append(spec_value)
#         spec_objects.extend(temp_objects)
#         count_items -= 1
#         # print(f"Добавлены характеристики для {item.title} \n\t>> Осталось => {count_items}")
#         if len(spec_objects) > 300:
#             print(f'{len(spec_objects)} значений характеристик заливается в БД. ОСТАЛОСЬ обработать {count_items} товаров')
#             SpecValue.objects.bulk_create(spec_objects)
#             spec_objects = list()
#     # print(f'SpecValue.objects.bulk_create(spec_objects) => {len(spec_objects)=} значений характеристик заливается в БД')
#     SpecValue.objects.bulk_create(spec_objects)


class CreateObjects(Thread):
    def __init__(self, items_butch, data, all_specs, exists_spec_values, results, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items_butch = items_butch
        self.data = data
        self.all_specs = all_specs
        self.exists_spec_values = exists_spec_values
        self.__results = results

    def run(self):
        self.iterate_data()
        print(f'Обработана пачка из {len(self.items_butch)} - Результат {len(self.__results)} характеристик', flush=True)

    # def get_result(self):
    #     return self.__results

    def iterate_data(self):
        for item in self.items_butch:
            self.__results.extend(self.create_obj(item))

    def create_obj(self, item):
        return [
            SpecValue(
                item=item,
                spec_item=self.all_specs.get(code=spec['FeatureCode']),
                value=spec['FeatureValue'] if spec['FeatureValue'] is not None else ""
                )
            for spec in self.data[item.code]["Features"] 
            if (item.pk, spec['FeatureCode']) not in self.exists_spec_values
        ]


def chunks_generator(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]

@timeit
def add_item_specs(items: dict):
    print(f"Создание характеристик товаров - ВСЕГО товаров {len(items)} шт\n \
            Характеристик на товар в среднем 10-13")

    items_in_db = Item.objects.filter(code__in=items.keys())
    exists_spec_values = set(SpecValue.objects.all().values_list('item', 'spec_item__code'))
    all_specs = SpecItem.objects.all()
    spec_objects = list()
    threads = list()

    for items_butch in chunks_generator(items_in_db, 700):
        print(f"Добавляем в обработку список на {len(items_butch)} обьектов ", flush=True)
        threads.append(
            CreateObjects(
                items_butch=items_butch,
                data=items,
                all_specs=all_specs,
                exists_spec_values=exists_spec_values,
                results=spec_objects,
                )
            )
    
    for th in threads:
        print("Запуск", flush=True)
        th.start()

    print("Ждем создания объектов!", flush=True)

    for th in threads:
        th.join()

    # for th in threads:
    #     spec_objects.extend(th.get_result())

    print(f'SpecValue.objects.bulk_create(spec_objects) => {len(spec_objects)=} значений характеристик заливается в БД')
    SpecValue.objects.bulk_create(spec_objects)



@timeit      
def set_analogs_and_related(items: dict):
    """Устанавливает для каждого прредмета
    аналоги и сопуствующие товары

    Args:
        items (dict): [description]
    """
    print(f"Создание аналогов и сопутствующих товаров - ВСЕГО {len(items)} шт")
    
    for item_code, item_info in items.items():
        item = Item.objects.get(code=item_code)
        analog = item_info.get('Analog', False)
        related = item_info.get('RelatedProd', False)
        if analog:
            item.set_analogs(analog)
        if related:
            item.set_related(related)
        item.save()

@timeit
def update_prices(prices: dict[str: ItemPrice]):
    """Обновление цен на товары

    Args:
        prices (dict[str): [description]
    """
    print(f"Обновление цен - ВСЕГО {len(prices)} шт")

    item_codes = prices.keys()
    items_from_db = Item.objects.filter(code__in=item_codes)
    items_list = []
    for item in items_from_db:
        item.price = prices[item.code].price
        item.base_price = prices[item.code].price
        item.quantity_unit = prices[item.code].quantity_unit
        item.quantity_min = prices[item.code].quantity_min
        item.quantity = prices[item.code].quantity
        item.set_quantity_lots(prices[item.code].quantity_lots)
        items_list.append(item)
    Item.objects.bulk_update(items_list, fields=['price', 'base_price', 'quantity_unit', 'quantity_min', 'quantity_lots'])


def send_to_base(file_type: str, result: dict, what_update: dict):

    need_update_cats = what_update.get('update_categories', False)
    need_update_items = what_update.get('update_items', False)
    need_update_specs = what_update.get('update_specs', False)
    need_update_ar = what_update.get('update_analog_and_related', False)

    if file_type == 'PRODAT':
        groups = result['groups']
        features = result['features']
        if need_update_cats:
            create_categories(groups)

        if need_update_items:
            create_items(result['items'])

        if need_update_specs:
            create_specs(features)
            add_item_specs(result['items'])

        if need_update_ar:        
            set_analogs_and_related(result['items'])
    elif file_type == 'PRICAT':
        # result = parser.get_items()
        update_prices(result['prices'])
    elif file_type == 'CAT_CSV':
        print("RUN CREATE CATS")
        create_categories_from_csv(result)
    return