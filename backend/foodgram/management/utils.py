import json


NOT_FOUND_MESSAGE = 'Ошибка! Файл {path} не найден.'
SOME_ERROR = 'Ошибка! {error}'


def load_from_json(model, path):
    try:
        with open(path, 'r', encoding='utf-8') as json_file:
            model.objects.bulk_create(
                (
                    model(**line)
                    for line in json.load(json_file)
                ),
                ignore_conflicts=True
            )
    except FileNotFoundError:
        print(NOT_FOUND_MESSAGE.format(path=path))
    except Exception as error:
        print(SOME_ERROR.format(error))
