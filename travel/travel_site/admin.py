from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


class TagsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ('name',)
    autocomplete_fields = ['location', ]


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_tag')
    list_display_links = ('name', 'image_tag')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


class DayInline(admin.TabularInline):
    model = Day
    readonly_fields = ('id',)
    extra = 1


class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'quantity', 'price', 'slug')
    list_display_links = ('name',)
    search_fields = ('name', )
    prepopulated_fields = {"slug": ("name",)}
    inlines = [DayInline]


class BlogAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'created_at', 'slug')
    list_display_links = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


class ProductRentAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'light')
    list_display_links = ('name',)
    search_fields = ('name',)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_displayed')
    list_display_links = ('name',)
    search_fields = ('name',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_displayed')
    list_display_links = ('name',)
    search_fields = ('name',)


class SlideAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_displayed')
    list_display_links = ('name',)
    search_fields = ('name',)


class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname')
    list_display_links = ('name', 'surname')
    search_fields = ('name',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'price', 'status', 'products')
    list_display_links = ('name', 'phone', 'price', 'products')
    search_fields = ('phone',)


admin.site.register(Tags, TagsAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Tour, TourAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(ProductRent, ProductRentAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Slide, SlideAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Order, OrderAdmin)
