from django.contrib import admin
import quiz.models as quiz

from django.forms import TextInput, Textarea
from django.db import models


# Register your models here.

class AnswersInline(admin.TabularInline):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    model = quiz.Answer
    extra = 1


class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})},
    }
    fieldsets = [
        (None, {'fields': ['to', 'value', 'points', 'image']}),
    ]
    inlines = [AnswersInline]


class QuizAdmin(admin.ModelAdmin):
    model = quiz.Quiz

# TODO Place here QuestionAdmin ;)

admin.site.register(quiz.Question, QuestionAdmin)
admin.site.register(quiz.Quiz, QuizAdmin)
admin.site.register(quiz.Record)
