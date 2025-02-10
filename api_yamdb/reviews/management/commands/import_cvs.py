import csv
from collections import namedtuple
from django.conf import settings
from django.core.management import BaseCommand
from django.db.utils import IntegrityError
from reviews.models import (
    Category, Comment, Genre, GenreTitle, Review, Title, User
)

model_tuple = namedtuple('Model', ['base', 'model', 'fields'])

user = model_tuple('users.csv', User, [
    'id', 'username', 'email', 'role', 'bio', 'first_name', 'last_name'])
category = model_tuple('category.csv', Category, [
    'id', 'name', 'slug'])
genre = model_tuple('genre.csv', Genre, [
    'id', 'name', 'slug'])
title = model_tuple('titles.csv', Title, [
    'id', 'name', 'year', 'category'])
review = model_tuple('review.csv', Review, [
    'id', 'title_id', 'text', 'author', 'score', 'pub_date'])
comment = model_tuple('comments.csv', Comment, [
    'id', 'review_id', 'text', 'author', 'pub_date'])
genre_title = model_tuple('genre_title.csv', GenreTitle, [
    'id', 'title_id', 'genre_id'])

models = (user, category, genre, title, genre_title, review, comment, )


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for model in models:
            try:
                self.process_model(model)
            except IntegrityError:
                pass
            except FileNotFoundError:
                raise BaseException(f'Проверьте наличие файла {model.base}')
        self.stdout.write(self.style.SUCCESS('Данные успешно загружены.'))

    def process_model(self, model):
        with open(
            f'{settings.BASE_DIR}/static/data/{model.base}',
            'r', encoding='utf-8'
        ) as csv_file:
            reader = csv.DictReader(csv_file)
            self.validate_fields(reader, model)
            if model.model == Title:
                self.process_title(reader)
            elif model.model == Review:
                self.process_review(reader)
            elif model.model == Comment:
                self.process_comment(reader)
            else:
                self.process_generic_model(reader, model)

    def validate_fields(self, reader, model):
        if reader.fieldnames != model.fields:
            raise BaseException(f'Проверьте поля в {model.base}')

    def process_title(self, reader):
        for data in reader:
            category_id = data.pop('category')
            category_instance = Category.objects.get(id=category_id)
            Title.objects.create(category=category_instance, **data)

    def process_review(self, reader):
        reviews_to_create = []
        for data in reader:
            author_instance = self.get_author_instance(data)
            if not author_instance:
                continue
            review_data = {**data, 'author': author_instance}
            reviews_to_create.append(Review(**review_data))
        Review.objects.bulk_create(reviews_to_create)

    def process_comment(self, reader):
        comments_to_create = []
        for data in reader:
            author_instance = self.get_author_instance(data)
            if not author_instance:
                continue
            comment_data = {**data, 'author': author_instance}
            comments_to_create.append(Comment(**comment_data))
        Comment.objects.bulk_create(comments_to_create)

    def process_generic_model(self, reader, model):
        model.model.objects.bulk_create(
            model.model(**data) for data in reader
        )

    def get_author_instance(self, data):
        author_id = data.pop('author')
        try:
            return User.objects.get(id=author_id)
        except User.DoesNotExist:
            print(f"Пользователь с идентификатором {author_id} не существует.")
            return None
