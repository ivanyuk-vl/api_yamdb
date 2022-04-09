from django.apps import apps
from django.core.management.base import BaseCommand


def get_apps():
    applications_list = {}
    for app_class in apps.get_app_configs():
        application = {'app': app_class,
                       'name': app_class.name,
                       'verbose_name': app_class.verbose_name,
                       'models': []}

        for model_class in app_class.get_models():
            application['models'].append(model_class.__name__)

        applications_list[app_class.name] = application

    return applications_list


def get_stdout_str(app, show_model):
    message = f"""
Application {str(app['app'])}:
    name: {str(app['name'])}
    verbose name: {str(app['verbose_name'])}"""

    if show_model:
        message += f"\r\n    models: {str(app['models'])}"
    return message


class Command(BaseCommand):
    help = 'Получить информацию о приложениях'

    def add_arguments(self, parser):
        parser.add_argument('--app_name', type=str, help='Список')
        parser.add_argument('--show_models', help='Список',
                            action='store_const', const=True)

    def handle(self, *args, **options):
        applications = get_apps()
        if options['app_name'] is None:
            for app in applications.values():
                message = get_stdout_str(app, options['show_models'])
                self.stdout.write(message)
        else:
            message = get_stdout_str(applications[options['app_name']],
                                     options['show_models'])
            self.stdout.write(message)
