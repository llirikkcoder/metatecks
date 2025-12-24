import logging
import time

from django.utils import timezone

from celery import shared_task

from .models import ExchangeParsing
from .sync import start_sync
from .utils import ImportManager


l = logging.getLogger('cml.tasks')


@shared_task
def make_import(parsing_obj_id, mode='import'):
    assert mode in ['import', 'offers']

    if mode == 'import':
        l.info('---------')

    l.info('[import] #%d/%s: start...', parsing_obj_id, mode)
    parsing = None

    try:
        # получаем объект ExchangeParsing + несколько проверок
        parsing = ExchangeParsing.objects.get(id=parsing_obj_id)
        if getattr(parsing, f'{mode}_was_imported') is True:
            raise Exception('File was already parsed')
        # - TODO: если уже был создан более новый объект, то тоже выходим, наверное

        # - TODO: берем стату, сохраняем в объект мб

        # проводим импорт файла в базу
        _file_path = getattr(parsing, f'{mode}_file_path')
        import_manager = ImportManager(_file_path, mode)
        import_manager.import_all()
        # import_manager.is_full = True

        l.info('[import] #%d/%s: import done!', parsing_obj_id, mode)

        # обновляем объект парсинга
        parsing.refresh_from_db()
        setattr(parsing, f'{mode}_was_imported', True)
        setattr(parsing, f'{mode}_imported_at', timezone.now())
        if mode == 'import':
            parsing.is_full = import_manager.is_full
        parsing.save()

        l.info('[import] #%d/%s: object updated', parsing_obj_id, mode)

        # запускаем парсинг файла offers.xml или синхронизацию с каталогом
        if mode == 'import':
            retry = False
            while True:
                parsing.refresh_from_db()
                if parsing.offers_xml_obj:
                    l.info('[import] #%d/%s: starting offers.xml parsing', parsing_obj_id, mode)
                    make_import.delay(parsing_obj_id, 'offers')
                    break
                elif retry is False:
                    time.sleep(10)
                    retry = True
                else:
                    raise Exception('No offers_xml_obj, return')

        elif mode == 'offers':
            l.info('[import] #%d/%s: starting sync with catalog', parsing_obj_id, mode)
            make_sync.delay(parsing_obj_id)

    except Exception as exc:
        err_message = repr(exc)
        l.error('[import] #%d/%s: import error: %s', parsing_obj_id, mode, err_message)
        if parsing:
            parsing.refresh_from_db()
            setattr(parsing, f'{mode}_error_message', err_message)
            parsing.save()


@shared_task
def make_sync(parsing_obj_id):
    l.info('[sync] #%d: start...', parsing_obj_id)
    parsing = None

    try:
        parsing = ExchangeParsing.objects.get(id=parsing_obj_id)
        if parsing.was_synced is True:
            raise Exception('Object was already synced')

        start_sync(is_full=parsing.is_full)

        parsing.refresh_from_db()
        parsing.was_synced = True
        parsing.synced_at = timezone.now()
        parsing.save()

        # TODO: берем стату, сохраняем в объект мб

        l.info('[sync] #%d: done!', parsing_obj_id)

    except Exception as exc:
        err_message = repr(exc)
        l.error('[sync] #%d: sync error: %s', parsing_obj_id, err_message)
        if parsing:
            parsing.refresh_from_db()
            parsing.sync_error_message = err_message
            parsing.save()
