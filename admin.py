from django.contrib import admin
from quiz.models import Question, AttemptedQuestion
from quiz.forms import QuestionFormAdmin

class QuestionAdmin(admin.ModelAdmin):
    form = QuestionFormAdmin
    exclude = ('author', )
    list_display = ('title','author', 'option1', 'option2', 'option3', 'option4', 'correct_option', 'max_marks','min_time', 'max_time')
    list_filter = ['author']
    
    def save_form(self, request, form, change):
        obj = super(QuestionAdmin, self).save_form(request, form, change)
        obj.author = request.user
        return obj
        
        
class AttemptedQuestionAdmin(admin.ModelAdmin):
    field_sets = None
    readonly_fields = ('question', 'player', 'time', 'marks_obtained', 'time_taken', 'server_time_taken', 'answered',)
    list_display = ('time',  'question', 'player', 'marks_obtained', 'time_taken', 'server_time_taken', 'answered',)
    list_filter = ['time', 'player']
    search_fields = ['player', 'question_title']
    date_hierarchy = 'time'
 
admin.site.register(Question, QuestionAdmin)
admin.site.register(AttemptedQuestion, AttemptedQuestionAdmin)
