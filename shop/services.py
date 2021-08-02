from decimal import Decimal
import os
from shop.utils import download_image
from .models import Category, Item, SpecItem, SpecValue
from .utils import timeit, ItemPrice
from django.db.models import Q

@timeit
def create_categores(categores: dict):
    """Создание Категорий и подкатегорий
    Args:
        categores ([dict]): {GRoupCode:Group(dataclass (code: str, name: str, parent: Group))
    """
    # if not Category.objects.filter(title='Главная', code=0).exists():
    #     start_group = Category(title='Главная')
    #     start_group.save()
    # else:
        # start_group = Category.objects.get(title='Главная')
    print(f"Создание категорий - ВСЕГО {len(categores)} шт")
    exists_categories = Category.objects.all().values_list('code', flat=True)
    for code, group in categores.items():
        if code not in exists_categories:
            if group.parent_code and group.parent_code is not None and group.parent_code not in exists_categories:
                cat = Category(title=categores[group.parent_code].name,
                    code=group.parent_code,
                    parent=None)
                cat.save()
            cat = Category(title=group.name,
                    code=group.code,
                    parent=None if group.parent_code is None else Category.objects.get(code=group.parent_code))
            cat.save()

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
def create_items(items: dict):
    """Создание товаров

    Args:
        items (dict): [description]
    """
    print(f"Создание товаров - ВСЕГО {len(items)} шт")
    items_for_create = []
    exists_items = Item.objects.all().values_list('code', flat=True)
    for item_code, item_info in items.items():
        if item_code in exists_items:
            continue
        # if Item.objects.filter(code=item_code).exists():
        #     continue # TODO Если уже есть возможно обновлять прайс?
        
        cat = Category.objects.get(code=item_info['ProductCode'])
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

@timeit
def add_item_specs(items: dict):
    print(f"Создание характеристик товаров - ВСЕГО товаров {len(items)} шт\n \
            Характеристик на товар в среднем 10-13")

    items_in_db = Item.objects.filter(code__in=items.keys())
    count_items = items_in_db.count()
    exists_spec_values = SpecValue.objects.all().values_list('item', 'spec_item__code')
    spec_objects = list()
    for item in items_in_db:
        item.save()
        for spec in items[item.code]["Features"]:
            if (item.pk, spec['FeatureCode']) in exists_spec_values:
                continue
            spec_item = SpecItem.objects.get(code=spec['FeatureCode'])
            spec_value = SpecValue(
                item=item,
                spec_item=spec_item,
                value=spec['FeatureValue'] if spec['FeatureValue'] is not None else ""
                )
            spec_objects.append(spec_value)
            #spec_value.save()
        count_items -= 1
        print(f"Добавлены характеристики для {item.title} \n\t>> Осталось => {count_items}")
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
    Item.objects.bulk_update(items_list, field=['price', 'base_price', 'quantity_unit', 'quantity_min', 'set_quantity_lots'])
