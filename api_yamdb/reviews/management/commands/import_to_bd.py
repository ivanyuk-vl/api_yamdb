from django.core.management.base import BaseCommand
import csv

from reviews.models import Titles, Categories, Genres, Review, Comment
from users.models import CustomUser

model = {'titles': Titles, 'categories': Categories,
         'genres': Genres, 'review': Review, 'comment': Comment,
         'customuser': CustomUser}


def list_obj(dr, obj, options):
    i = 0
    if obj == 'titles':
        categories = Categories.objects.create(pk=i['category'])
        options[obj] = (Titles(categories_id=categories.pk,
                               name=i['name'],
                               year=i['year'], ) for i in dr)
    elif obj == 'categories':
        options[obj] = (Categories(name=i['name'],
                                   slug=i['slug'], ) for i in dr)
    elif obj == 'genres':
        options[obj] = (Genres(name=i['name'],
                               slug=i['slug'], ) for i in dr)
    elif obj == 'review':
        options[obj] = (Review(text=i['text'],
                               score=i['score'],
                               pub_date=i['pub_date'],
                               author_id=i['author'],
                               title_id=i['title_id'], ) for i in dr)
    elif obj == 'customuser':
        options[obj] = (CustomUser(username=i['username'],
                                   first_name=i['first_name'],
                                   last_name=i['last_name'],
                                   email=i['email'],
                                   role=i['role'],
                                   bio=i['bio'], ) for i in dr)
    return options[obj]


class Command(BaseCommand):
    help = 'Creating model objects according the file path specified'

    def add_arguments(self, parser):
        parser.add_argument('model', nargs='+', type=str, help='Model')
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        model_key = options['model']
        for m in model_key:
            Model = model[m]
        for csv_file in options['csv_file']:
            with open(f'static/data/{csv_file}', 'r', encoding='utf8') as fil:
                dr = csv.DictReader(fil)
                for m in model_key:
                    objs = list_obj(dr, m, model)
                Model.objects.bulk_create(objs)
