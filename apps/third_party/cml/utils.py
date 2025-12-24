import os
import logging
import importlib
from io import BytesIO
import six
import unicodedata
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

from .items import *
from .conf import settings
from .models import (
    # init_import_groups,
    # init_import_properties,
    init_import_catalog,
    # init_import_offers,
    # init_import_stock_balances,
    after_import_groups,
)


logger = logging.getLogger('cml.utils')


def _get_cleaned_text(element):
    try:
        text = element.text
    except:
        text = ''
    if text is None:
        return ''
    text = unicodedata.normalize('NFKC', text)  # custom
    return text.strip(' ')

_clean = _get_cleaned_text


class ImportManager(object):

    def __init__(self, file_path, mode=None):
        assert mode in ['import', 'offers', None]
        self.file_path = file_path
        self.tree = None
        self.item_processor = ItemProcessor()
        self.mode = mode
        self.is_full = None

    def import_all(self):
        # - в ImportManager всё как всегда, но
        #    1) убираем или редачим init_* вызовы;
        #    2) is_full;
        #    3) ???;

        try:
            self.tree = self._get_tree()
        except Exception:
            logger.error('Import all error!')
            return
        try:
            root = self.tree.getroot()
            self.p = root.tag.split('КоммерческаяИнформация')[0]
        except Exception:
            logger.error('Error in getting prefix!')
            return
        self.import_classifier()
        self.import_catalogue()
        self.import_offers_pack()
        self.import_orders()
        logger.info('Import success!')

    def _get_tree(self):
        if self.tree is not None:
            return self.tree
        if not os.path.exists(self.file_path):
            message = 'File not found {}'.format(self.file_path)
            logger.error(message)
            raise OSError(message)
        try:
            tree = ET.parse(self.file_path)
        except Exception as e:
            message = 'File parse error {}'.format(self.file_path)
            logger.error(message)
            raise e
        return tree

    def import_classifier(self):
        try:
            tree = self._get_tree()
        except Exception:
            logger.error('Import classifier error!')
            return
        classifier_element = tree.find(f'{self.p}Классификатор')
        if classifier_element is not None:
            if classifier_element.find(f'{self.p}Группы') is not None:
                # init_import_groups()
                self._parse_groups(classifier_element)
                after_import_groups()
            if classifier_element.find(f'{self.p}Свойства') is not None:
                # init_import_properties()
                self._parse_properties(classifier_element)

    def _parse_groups(self, current_element, parent_item=None):
        for group_element in current_element.findall(f'{self.p}Группы/{self.p}Группа'):
            group_item = Group(group_element)
            group_item.id = _clean(group_element.find(f'{self.p}Ид'))
            group_item.name = _clean(group_element.find(f'{self.p}Наименование'))
            if parent_item is not None:
                parent_item.groups.append(group_item)
            self._parse_groups(group_element, group_item)
            # processing only top level groups
            if parent_item is None:
                self.item_processor.process_item(group_item)

    def _parse_properties(self, current_element):
        for property_element in current_element.findall(f'{self.p}Свойства/{self.p}Свойство'):
            property_item = Property(property_element)
            property_item.id = _clean(property_element.find(f'{self.p}Ид'))
            property_item.name = _clean(property_element.find(f'{self.p}Наименование'))
            property_item.value_type = _clean(property_element.find(f'{self.p}ТипЗначений'))
            property_item.for_products = _clean(property_element.find(f'{self.p}ДляТоваров')) == 'true'
            self.item_processor.process_item(property_item)
            for variant_element in property_element.findall('{0}ВариантыЗначений/{0}{1}'.format(self.p, property_item.value_type)):
                variant = PropertyVariant(variant_element)
                variant.id = _clean(variant_element.find(f'{self.p}ИдЗначения'))
                variant.value = _clean(variant_element.find(f'{self.p}Значение'))
                variant.property_id = property_item.id
                self.item_processor.process_item(variant)

    def import_catalogue(self):
        try:
            tree = self._get_tree()
        except Exception:
            logger.error('Import catalogue error!')
            return
        catalogue_element = tree.find(f'{self.p}Каталог')
        if catalogue_element is not None:
            _only_changes = catalogue_element.get('СодержитТолькоИзменения', True)
            self.is_full = {
                'true': False,
                'false': True,
            }.get(_only_changes, False)
            if self.is_full is True:
                init_import_catalog()
            self._parse_products(catalogue_element)

    def _parse_products(self, current_element):
        for product_element in current_element.findall(f'{self.p}Товары/{self.p}Товар'):
            product_item = Product(product_element)
            product_item.id = _clean(product_element.find(f'{self.p}Ид'))
            product_item.name = _clean(product_element.find(f'{self.p}Наименование'))
            product_item.bar_code = _clean(product_element.find(f'{self.p}Штрихкод'))
            product_item.vendor_code = _clean(product_element.find(f'{self.p}Артикул'))
            product_item.description = _clean(product_element.find(f'{self.p}Описание'))

            sku_element = product_element.find(f'{self.p}БазоваяЕдиница')
            if sku_element is not None:
                sku_item = Sku(sku_element)
                sku_item.id = sku_element.get('Код')
                sku_item.name_full = sku_element.get('НаименованиеПолное')
                sku_item.international_abbr = sku_element.get('МеждународноеСокращение')
                sku_item.name = _clean(sku_element)
                product_item.sku_id = sku_item.id
                self.item_processor.process_item(sku_item)

            image_element = product_element.find(f'{self.p}Картинка')
            if image_element is not None:
                image_text = _clean(image_element)
                try:
                    image_filename = os.path.basename(image_text)
                except Exception:
                    image_filename = ''
                if image_filename:
                    product_item.image_path = os.path.join(settings.CML_UPLOAD_ROOT, image_filename)

            for group_id_element in product_element.findall(f'{self.p}Группы/{self.p}Ид'):
                product_item.group_ids.append(_clean(group_id_element))

            for property_element in product_element.findall(f'{self.p}ЗначенияСвойств/{self.p}ЗначенияСвойства'):
                property_id = _clean(property_element.find(f'{self.p}Ид'))
                property_variant_id = _clean(property_element.find(f'{self.p}Значение'))
                if property_variant_id:
                    product_item.properties.append((property_id, property_variant_id))

            for tax_element in product_element.findall(f'{self.p}СтавкиНалогов/{self.p}СтавкаНалога'):
                tax_item = Tax(tax_element)
                tax_item.name = _clean(tax_element.find(f'{self.p}Наименование'))
                try:
                    tax_item.value = Decimal(_clean(tax_element.find(f'{self.p}Ставка')))
                except:
                    tax_item.value = Decimal()
                self.item_processor.process_item(tax_item)
                product_item.tax_name = tax_item.name

            for additional_field_element in product_element.findall(f'{self.p}ЗначенияРеквизитов/{self.p}ЗначениеРеквизита'):
                additional_field = AdditionalField(additional_field_element)
                additional_field.name = _clean(additional_field_element.find(f'{self.p}Наименование'))
                additional_field.value = _clean(additional_field_element.find(f'{self.p}Значение'))
                product_item.additional_fields.append(additional_field)

            self.item_processor.process_item(product_item)

    def import_offers_pack(self):
        try:
            tree = self._get_tree()
        except Exception:
            logger.error('Import offers pack error!')
            return
        offers_pack_element = tree.find(f'{self.p}ПакетПредложений')
        if offers_pack_element is not None:
            _only_changes = offers_pack_element.get('СодержитТолькоИзменения', True)
            self.is_full = {
                'true': False,
                'false': True,
            }.get(_only_changes, False)
            # self.is_full = ...
            # init_import_offers()
            self._parse_price_types(offers_pack_element)
            self._parse_warehouses(offers_pack_element)
            self._parse_offers(offers_pack_element)
        else:
            offers_changes_element = tree.find(f'{self.p}ИзмененияПакетаПредложений')
            if offers_changes_element is not None:
                self.is_full = False
                # init_import_stock_balances()
                self._parse_offers(offers_changes_element)

    def _parse_price_types(self, current_element):
        for price_type_element in current_element.findall(f'{self.p}ТипыЦен/{self.p}ТипЦены'):
            price_type_item = PriceType(price_type_element)
            price_type_item.id = _clean(price_type_element.find(f'{self.p}Ид'))
            price_type_item.name = _clean(price_type_element.find(f'{self.p}Наименование'))
            price_type_item.currency = _clean(price_type_element.find(f'{self.p}Валюта'))
            price_type_item.tax_name = _clean(price_type_element.find(f'{self.p}Налог/{self.p}Наименование'))
            if _clean(price_type_element.find(f'{self.p}Налог/{self.p}УчтеноВСумме')) == 'true':
                price_type_item.tax_in_sum = True
            self.item_processor.process_item(price_type_item)

    def _parse_warehouses(self, current_element):
        for warehouse_element in current_element.findall(f'{self.p}Склады/{self.p}Склад'):
            warehouse_item = Warehouse(warehouse_element)
            warehouse_item.id = _clean(warehouse_element.find(f'{self.p}Ид'))
            warehouse_item.name = _clean(warehouse_element.find(f'{self.p}Наименование'))
            for contact_element in warehouse_element.findall(f'{self.p}Контакты/{self.p}Контакт'):
                contact_type = _clean(contact_element.find(f'{self.p}Тип'))
                contact_value = _clean(contact_element.find(f'{self.p}Значение'))
                if 'Почта' in contact_type:
                    warehouse_item.address = contact_value
                elif 'Телефон' in contact_type:
                    warehouse_item.phone = contact_value
            self.item_processor.process_item(warehouse_item)

    def _parse_offers(self, current_element):
        for offer_element in current_element.findall(f'{self.p}Предложения/{self.p}Предложение'):
            offer_item = Offer(offer_element)
            offer_item.id = _clean(offer_element.find(f'{self.p}Ид'))
            offer_item.additional_id = _clean(offer_element.find(f'{self.p}ИдХарактеристики'))
            offer_item.name = _clean(offer_element.find(f'{self.p}Наименование'))

            sku_element = offer_element.find(f'{self.p}БазоваяЕдиница')
            if sku_element is not None:
                sku_item = Sku(sku_element)
                sku_item.id = sku_element.get('Код')
                sku_item.name_full = sku_element.get('НаименованиеПолное')
                sku_item.international_abbr = sku_element.get('МеждународноеСокращение')
                sku_item.name = _clean(sku_element)
                offer_item.sku_id = sku_item.id
                self.item_processor.process_item(sku_item)

            for price_element in offer_element.findall(f'{self.p}Цены/{self.p}Цена'):
                price_item = Price(price_element)
                price_item.representation = _clean(price_element.find(f'{self.p}Представление'))
                price_item.price_type_id = _clean(price_element.find(f'{self.p}ИдТипаЦены'))
                price_item.price_for_sku = Decimal(_clean(price_element.find(f'{self.p}ЦенаЗаЕдиницу')))
                price_item.currency_name = _clean(price_element.find(f'{self.p}Валюта'))
                price_item.sku_name = _clean(price_element.find(f'{self.p}Единица'))
                price_item.sku_ratio = Decimal(_clean(price_element.find(f'{self.p}Коэффициент')))
                offer_item.prices.append(price_item)

            stock_elements = offer_element.findall(f'{self.p}Склад')
            if not stock_elements:
                stock_elements = offer_element.findall(f'{self.p}Склады')
            for stock_element in stock_elements:
                stock_item = StockBalance(stock_element)
                stock_item.warehouse_id = stock_element.get('ИдСклада')
                number = stock_element.get('КоличествоНаСкладе')
                number = int(number) if number else 0
                stock_item.number = number if number >= 0 else 0
                offer_item.stock_balances.append(stock_item)

            self.item_processor.process_item(offer_item)

    def import_orders(self):
        try:
            tree = self._get_tree()
        except Exception:
            logger.error('Import orders error!')
            return
        orders_elements = tree.find(f'{self.p}Документ')
        if orders_elements is not None:
            self._parse_orders(orders_elements)

    def _parse_orders(self, order_elements):
        for order_element in order_elements:
            order_item = Order(order_element)
            order_item.id = _clean(order_element.find(f'{self.p}Ид'))
            order_item.number = _clean(order_element.find(f'{self.p}Номер'))
            order_item.date = _clean(order_element.find(f'{self.p}Дата'))
            order_item.currency_name = _clean(order_element.find(f'{self.p}Валюта'))
            order_item.currency_rate = _clean(order_element.find(f'{self.p}Курс'))
            order_item.operation = _clean(order_element.find(f'{self.p}ХозОперация'))
            order_item.role = _clean(order_element.find(f'{self.p}Роль'))
            order_item.sum = _clean(order_element.find(f'{self.p}Сумма'))
            order_item.client.id = _clean(order_element.find(f'{self.p}Контрагенты/{self.p}Контрагент/{self.p}Ид'))
            order_item.client.name = _clean(order_element.find(f'{self.p}Контрагенты/{self.p}Контрагент/{self.p}Наименование'))
            order_item.client.full_name = _clean(
                                          order_element.find(f'{self.p}Контрагенты/{self.p}Контрагент/{self.p}ПолноеНаименование'))
            order_item.time = _clean(order_element.find(f'{self.p}Время'))
            order_item.comment = _clean(order_element.find(f'{self.p}Комментарий'))
            item_elements = order_element.find(f'{self.p}Товары/{self.p}Товар')
            if item_elements is not None:
                for item_element in item_elements:
                    order_item_item = OrderItem(item_element)
                    order_item_item.id = _clean(item_element.find(f'{self.p}Ид'))
                    order_item_item.name = _clean(item_element.find(f'{self.p}Наименование'))
                    sku_element = item_element.find(f'{self.p}БазоваяЕдиница')
                    if sku_element is not None:
                        order_item_item.sku.id = sku_element.get('Код')
                        order_item_item.sku.name = _clean(sku_element)
                        order_item_item.sku.name_full = sku_element.get('НаименованиеПолное')
                        order_item_item.sku.international_abbr = sku_element.get('МеждународноеСокращение')
                    order_item_item.price = _clean(item_element.find(f'{self.p}ЦенаЗаЕдиницу'))
                    order_item_item.quant = _clean(item_element.find(f'{self.p}Количество'))
                    order_item_item.sum = _clean(item_element.find(f'{self.p}Сумма'))
                    order_item.items.append(order_item_item)
            additional_field_elements = order_element.find(f'{self.p}ЗначенияРеквизитов/{self.p}ЗначениеРеквизита')
            if additional_field_elements is not None:
                for additional_field_element in additional_field_elements:
                    additional_field_item = AdditionalField(additional_field_element)
                    additional_field_item.name = _clean(item_element.find(f'{self.p}Наименование'))
                    additional_field_item.value = _clean(item_element.find(f'{self.p}Значение'))
            self.item_processor.process_item(order_item)


class ExportManager(object):

    def __init__(self):
        self.item_processor = ItemProcessor()
        self.root = ET.Element('КоммерческаяИнформация')
        self.root.set('ВерсияСхемы', '2.05')
        self.root.set('ДатаФормирования', six.text_type(datetime.now().date()))

    def get_xml(self):
        f = BytesIO()
        tree = ET.ElementTree(self.root)
        tree.write(f, encoding='windows-1251', xml_declaration=True)
        return f.getvalue()

    def export_all(self):
        self.export_orders()

    def export_orders(self):
        for order in self.item_processor.yield_item(Order):
            order_element = ET.SubElement(self.root, 'Документ')
            ET.SubElement(order_element, 'Ид').text = six.text_type(order.id)
            ET.SubElement(order_element, 'Номер').text = six.text_type(order.number)
            ET.SubElement(order_element, 'Дата').text = six.text_type(order.date.strftime('%Y-%m-%d'))
            ET.SubElement(order_element, 'Время').text = six.text_type(order.time.strftime('%H:%M:%S'))
            ET.SubElement(order_element, 'ХозОперация').text = six.text_type(order.operation)
            ET.SubElement(order_element, 'Роль').text = six.text_type(order.role)
            ET.SubElement(order_element, 'Валюта').text = six.text_type(order.currency_name)
            ET.SubElement(order_element, 'Курс').text = six.text_type(order.currency_rate)
            ET.SubElement(order_element, 'Сумма').text = six.text_type(order.sum)
            ET.SubElement(order_element, 'Комментарий').text = six.text_type(order.comment)
            clients_element = ET.SubElement(order_element, 'Контрагенты')
            client_element = ET.SubElement(clients_element, 'Контрагент')
            ET.SubElement(client_element, 'Ид').text = six.text_type(order.client.id)
            ET.SubElement(client_element, 'Наименование').text = six.text_type(order.client.name)
            ET.SubElement(client_element, 'Роль').text = six.text_type(order.client.role)
            ET.SubElement(client_element, 'ПолноеНаименование').text = six.text_type(order.client.full_name)
            ET.SubElement(client_element, 'Фамилия').text = six.text_type(order.client.last_name)
            ET.SubElement(client_element, 'Имя').text = six.text_type(order.client.first_name)
            address_element = ET.SubElement(clients_element, 'АдресРегистрации')
            ET.SubElement(clients_element, 'Представление').text = six.text_type(order.client.address)
            products_element = ET.SubElement(order_element, 'Товары')
            for order_item in order.items:
                product_element = ET.SubElement(products_element, 'Товар')
                ET.SubElement(product_element, 'Ид').text = six.text_type(order_item.id)
                ET.SubElement(product_element, 'Наименование').text = six.text_type(order_item.name)
                sku_element = ET.SubElement(product_element, 'БазоваяЕдиница ')
                sku_element.set('Код', order_item.sku.id)
                sku_element.set('НаименованиеПолное', order_item.sku.name_full)
                sku_element.set('МеждународноеСокращение', order_item.sku.international_abbr)
                sku_element.text = order_item.sku.name
                ET.SubElement(product_element, 'ЦенаЗаЕдиницу').text = six.text_type(order_item.price)
                ET.SubElement(product_element, 'Количество').text = six.text_type(order_item.quant)
                ET.SubElement(product_element, 'Сумма').text = six.text_type(order_item.sum)

    def flush(self):
        self.item_processor.flush_pipeline(Order)


class ItemProcessor(object):

    def __init__(self):
        self._project_pipelines = {}
        self._load_project_pipelines()

    def _load_project_pipelines(self):
        try:
            pipelines_module_name = settings.CML_PROJECT_PIPELINES
        except AttributeError:
            logger.info('Configure CML_PROJECT_PIPELINES in settings!')
            return
        try:
            pipelines_module = importlib.import_module(pipelines_module_name)
        except ImportError:
            return
        for item_class_name in PROCESSED_ITEMS:
            try:
                pipeline_class = getattr(pipelines_module, '{}Pipeline'.format(item_class_name))
            except AttributeError:
                continue
            self._project_pipelines[item_class_name] = pipeline_class()

    def _get_project_pipeline(self, item_class):
        item_class_name = item_class.__name__
        return self._project_pipelines.get(item_class_name, False)

    def process_item(self, item):
        _class = item.__class__.__name__
        _id = getattr(item, 'id', '')
        _name = getattr(item, 'name', '')
        project_pipeline = self._get_project_pipeline(item.__class__)
        if project_pipeline:
            try:
                project_pipeline.process_item(item)
            except Exception as e:
                # import ipdb; ipdb.set_trace()
                logger.error('Error processing of item {}: {}'.format(item.__class__.__name__, repr(e)))
                raise e  # custom
        # else:
        #     import ipdb; ipdb.set_trace()

    def yield_item(self, item_class):
        project_pipeline = self._get_project_pipeline(item_class)
        if project_pipeline:
            try:
                return project_pipeline.yield_item()
            except Exception as e:
                logger.error('Error yielding item {}: {}'.format(item_class.__name__, repr(e)))
                return []
        return []

    def flush_pipeline(self, item_class):
        project_pipeline = self._get_project_pipeline(item_class)
        if project_pipeline:
            try:
                project_pipeline.flush()
            except Exception as e:
                logger.error('Error flushing pipeline for item {}: {}'.format(item_class.__name__, repr(e)))
