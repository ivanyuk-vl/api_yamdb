# api_yamdb
api_yamdb

## Как развернуть

Перейти в каталог, где будет размещен проект
```shell
cd <путь_к_каталогу>
```
Клонировать проект из репозитария
```shell
git clone git@github.com:RazuvaevSD/api_yamdb.git
```
Перейти в каталог с проектом
```shell
cd api_yamdb
```
Установить виртуальное окружение
```shell
python3 -m venv venv
```
Активировать виртуальное окружение
```shell
source venv/bin/activate
```
Установить зависимости
```shell
pip3 install -r requirements.txt
```
Перейти в корневой каталог проекта
```shell
cd yatube_api
```
Запустить проект
```shell
python manage.py runserver
```
***
## Загрузка данных из csv-файлов
**Для импорта данных в базу необходимо**
- разместить файл (с расширением _csv_) c данными в каталоге `static/data/`
- выполнить команду `import_to_db <application> <model>`


**Обязательные параметры:**
- `aplication` - принимает имя приложения зарегистрированного в проекте, 
модель которого должна принять данные
- `model` - принимает имя модели которая должна принять данные

**Необязательные параметры:**
- `--filename` - имя загружаемого файла. Задается в том случае если имя файла 
не соответствует имени модели. Если не указан, для поиска файла используется 
имя `<model>+'.csv'`.
- `--clear` - параметр для очистки указанной модели от данных

**Требования к файлу:**
- должен иметь расширение csv
- должен содержать все обязательные поля модели (не содержать поля 
отсутствующие в модели)
в качестве разделителя использовать `,`

**Пример 1**  
Записать данные из файла `static/data/Category.csv` в модель `Category` 
приложения `reviews`
``` shell
import_to_db reviews Category
```
**Пример 2**  
Записать данные из файла `static/data/MySuperFile.csv` в модель `Category` 
приложения `reviews`
``` shell
import_to_db reviews Category MySuperFile.csv
```
**Пример 3**  
Удалить все записи из модели `Category` приложения `reviews`
``` shell
import_to_db reviews Category --clear
```

**Внимание!**
Во избежание ошибки `FOREIGN KEY constraint failed` при загрузке данных с 
реляционными связями необходимо соблюдать последовательность

## Получить информацию о приложениях или моделях проекта
### get_apps 
Без параметров возвращает список зарегистрированных приложений

Необязательные параметры:
- `--app_name` - принимает имя приложения. Позволяет вывести информацию по 
конкретному приложению
- `--show_models` - позволяет добавить к выводу список моделей приложения


**Пример 1**
Отобразить информацию о всех приложениях, с отображением списка моделей
```shell
get_apps --show_models
```

**Пример 2**  
Отобразить информацию о приложении `Users`, с отображением списка моделей
```shell
get_apps --app_name users --show_models
```


**Пример 1**
Отобразить информацию о всех моделях приложения `reviews`, с отображением 
списка полей
```shell
get_models reviews --show_fields
```


### get_models
Возвращает список моделей зарегистрированных приложении

**Обязательные параметры:**
- `app_name` - принимает имя приложения

**Необязательные параметры:**
- --model_name - принимает имя модели. Позволяет вывести информацию по 
конкретной модели
- --show_fields - позволяет добавить к выводу список полей модели

**Пример 1**
Отобразить информацию о всех моделях приложения `reviews`, с отображением 
списка полей
```shell
get_models reviews --model_name Comment --show_fields
```

**Пример 2**  
Отобразить информацию о модели `Comment` приложения `reviews`, с отображением 
списка полей
```shell
get_models reviews --model_name Comment --show_fields
```

***
## API v1
С возможностями API можно ознакомиться, перейдя по ссылке 
[http://127.0.0.1/redoc/](http://127.0.0.1/redoc/)
