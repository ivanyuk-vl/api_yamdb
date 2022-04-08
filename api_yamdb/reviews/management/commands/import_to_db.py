import csv

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand


def application_existence_check(app_name):
    """Проверка существования указанного приложения"""
    for app_class in apps.get_app_configs():
        if app_name == app_class.name:
            return app_class
    raise LookupError('Указанное приложение не найдено.')


def model_existence_check(app_class, model_name):
    """Проверка существования указанной модели в приложении"""
    for model_class in app_class.get_models():
        if model_name == model_class.__name__:
            return model_class
    raise LookupError('Указанная модель в приложении не найдена')


def clear_model(model_class):
    """Очистка модели от данных"""
    try:
        objects = model_class.objects.all()
        objects.delete()
    except Exception as ex:
        raise Exception(f'При очистке модели от данных '
                        f'возникла ошибка: {ex}')


def create_objects(model_class, file_path):
    """Запись данных из файла"""
    with open(file_path, encoding='UTF-8') as file:
        csv_reader = csv.DictReader(file)
        model_fields = [field.name
                        for field in model_class._meta.fields]

        if not set(csv_reader.fieldnames) <= set(model_fields):
            raise ValidationError('Набор полей в файле превышает'
                                  'набор полей модели')

        objs = []
        for value in csv_reader:
            try:
                # создать экземпляр объекта из строки файла
                objs.append(model_class(**dict(value)))
            except Exception as ex:
                raise Exception('Ошибка создания'
                                f'экземпляра объекта: {ex}')
        try:
            # записать объекты в базу
            obj = model_class.objects.bulk_create(objs, len(objs))
            return obj
        except Exception as ex:
            raise Exception(f'Ошибка звписи объектов в базу: {ex}')


class Command(BaseCommand):
    help = 'Загрузка данных в модель из csv-файлов'

    def add_arguments(self, parser):
        parser.add_argument('app', type=str, help='Приложение')
        parser.add_argument('model', type=str, help='Модель')
        parser.add_argument('--filename', type=str, help='Имя файла')
        parser.add_argument('--clear',
                            action='store_const', const=True,
                            help='Удалить данные из модели')

    def handle(self, *args, **options):
        """Обработчик команды"""
        app_class = application_existence_check(options['app'])
        model_class = model_existence_check(app_class, options['model'])

        if options['clear'] is not None:
            clear_model(model_class)
            self.stdout.write('Очистка модели от данных успешно выполнена.')
        else:
            # собрать путь к файлу
            # если имя файла не было передано параметром ищем файл
            # по имени модели
            file_path = (
                settings.TEST_DATA_DIR
                + (options['filename'] or (options['model'] + '.csv'))
            )
            # записать данные в модель из файла
            objs = create_objects(model_class, file_path)
            if objs:
                self.stdout.write('Запись в модель данных успешно выполнена')
