"""Admin for the Online Course App.

Registers 7 model classes: Course, Lesson, Instructor, Learner,
Question, Choice, Submission. (Enrollment is the through-model for
Course.users and is not registered here.)
"""
from django.contrib import admin

from .models import Choice, Course, Instructor, Learner, Lesson, Question, Submission


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 3


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 3


class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date', 'total_enrollment')
    search_fields = ('name',)
    list_filter = ('pub_date',)


class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ('question_text', 'course', 'grade')
    list_filter = ('course',)
    search_fields = ('question_text',)


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission)
