from django.contrib import admin
from reviews.models import Category, Genre, Title, Review, User, Comment


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category')
    search_fields = ('name',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date')
    search_fields = ('title', 'author')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'pub_date')
    search_fields = ('text', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
