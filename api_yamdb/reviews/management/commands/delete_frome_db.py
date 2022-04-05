from django.core.management.base import BaseCommand

from reviews.models import Titles, Categories, Genres, Review, Comment

model = {'titles': Titles, 'categories': Categories,
         'genres': Genres, 'review': Review, 'comment': Comment}


class Command(BaseCommand):
    help = 'Delete object from model '

    def add_arguments(self, parser):
        parser.add_argument('model', nargs='+', type=str, help='Model')
        parser.add_argument('obj_id', nargs='+', type=int, help='Object ID')

    def handle(self, *args, **options):
        model_key = options['model']
        for m in model_key:
            Model = model[m]
        obj_ids = options['obj_id']
        for obj_id in obj_ids:
            print(f'1: {obj_id}')
            try:
                obj = Model.objects.get(pk=obj_id)
                print(f'2: {obj}')
                obj.delete()
                self.stdout.write(f'объект {obj} из модели {Model} удалён'
                                  ' успешно')
            except Titles.DoesNotExist:
                self.stdout.write(f'объект из модели {Model} не'
                                  ' сущестует')
