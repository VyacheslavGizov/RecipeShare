import json


SOME_ERROR = ('При загрузке данных в модель {model} из {path} '
              'возникла ошибка: {error}')


def load_from_json(model, path):
    try:
        with open(path, 'r', encoding='utf-8') as json_file:
            model.objects.bulk_create(
                (model(**line) for line in json.load(json_file)),
                ignore_conflicts=True
            )
    except Exception as error:
        print(SOME_ERROR.format(model=model, path=path, error=error))
