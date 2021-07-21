from decimal import Decimal
import os
from shop.utils import download_image
from .models import Category, Item, SpecItem, SpecValue

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
    for code, group in categores.items():
        if not Category.objects.filter(code=code).exists():
            if group.parent_code and group.parent_code is not None and not Category.objects.filter(code=group.parent_code).exists():
                cat = Category(title=categores[group.parent_code].name,
                    code=group.parent_code,
                    parent=None)
                cat.save()
            cat = Category(title=group.name,
                    code=group.code,
                    parent=None if group.parent_code is None else Category.objects.get(code=group.parent_code))
            cat.save()

def create_specs(specs: dict):
    """Создание характеристик товаров

    Args:
        specs (dict): [description]
    """
    for code, feature in specs.items():
        if not SpecItem.objects.filter(code=code).exists():
            spec = SpecItem(
                code=feature['FeatureCode'],
                title=feature['FeatureName'],
                uom=feature['FeatureUom'] if feature['FeatureUom'] is not None else ""
                )
            spec.save()

def create_items(items: dict):
    """Создание товаров

    Args:
        items (dict): [description]
    """
    for item_code, item_info in items.items():
        if Item.objects.filter(code=item_code).exists():
            continue # TODO Если уже есть возможно обновлять прайс?
        cat = Category.objects.get(code=item_info['ProductCode'])
        file_path = os.path.join('media', 'items', item_info['SenderPrdCode'])
        image_url = item_info.get('Image', False)
        image_path = download_image(image_url, path=file_path)
        if image_path is not None:
            image_path = os.path.join(*image_path.split('\\')[1:])
        item = Item(
                code=item_info['SenderPrdCode'],
                category=cat,
                title=item_info['ProductName'],
                description='',
                price=Decimal('0.0'),
                photo=image_path,
                in_stock=True if item_info['ProductStatus'] == 'Активно' else False,
                on_delete = False,
                quantity_min=item_info["ItemsPerUnit"],
                brand=item_info['Brand']
            )
        item.save()
        print(f"Добавлен {item.title}")
         # ПОдключение характеристик
        for spec in item_info['Features']:
            if spec['FeatureValue'] is None:
                continue
            spec_item = SpecItem.objects.get(code=spec['FeatureCode'])
            spec_value = SpecValue(item=item, spec_item=spec_item, value=spec['FeatureValue'])
            spec_value.save()
        
       
def set_analogs_and_related(items: dict):
    """Устанавливает для каждого прредмета
    аналоги и сопуствующие товары

    Args:
        items (dict): [description]
    """
    for item_code, item_info in items.items():
        item = Item.objects.get(code=item_code)
        analog = item_info.get('Analog', False)
        related = item_info.get('RelatedProd', False)
        if analog:
            item.set_analogs(analog)
        if related:
            item.set_related(related)
        item.save()

