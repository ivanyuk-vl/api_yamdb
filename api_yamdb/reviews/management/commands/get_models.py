from pprint import pprint

from django.apps import apps
from django.core.management.base import BaseCommand


def get_app(app_name):
    for app_class in apps.get_app_configs():
        if app_name == app_class.name:
            return app_class
    return False


def get_models(app_class):
    models_list = {}
    for model_class in app_class.get_models():
        model = {'model': model_class,
                 'name': model_class.__name__,
                 'fields': []}

        for field in model_class._meta.fields:
            model['fields'].append(field.name)

        models_list[model_class.__name__] = model
    # pprint(models_list)
    return models_list


def get_stdout_str(model, show_fields):
    message = f"""
Model {str(model['model'])}:
    name: {str(model['name'])}"""

    if show_fields:
        message += f"\r\n    models: {str(model['fields'])}"
    return message


class Command(BaseCommand):
    help = 'Получить информацию о модулях приложения'

    def add_arguments(self, parser):
        parser.add_argument('app_name', type=str, help='Имя приложения')
        parser.add_argument('--model_name', type=str, help='Список')
        parser.add_argument('--show_fields', help='Список',
                            action='store_const', const=True)

    def handle(self, *args, **options):
        app = get_app(options['app_name'])
        if not app:
            self.stdout.write('Приложение не найдено')

        models = get_models(app)
        if options['model_name'] is None:
            for model in models.values():
                message = get_stdout_str(model, options['show_fields'])
                self.stdout.write(message)
        else:
            message = get_stdout_str(models[options['model_name']],
                                     options['show_fields'])
            self.stdout.write(message)
