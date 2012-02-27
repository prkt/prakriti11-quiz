from django.forms import ModelForm, ChoiceField, Select, widgets, Form
from quiz.models import Question, AttemptedQuestion

class QuestionFormAdmin(ModelForm):
    OPTIONS = (
        (1, 'Option 1'),
        (2, 'Option 2'),
        (3, 'Option 3'),
        (4, 'Option 4'),
    )
    correct_option = ChoiceField(widget = widgets.RadioSelect, choices = OPTIONS, help_text = "Please Choose Correct Answer")
    class Meta:
        model = Question

class QuestionForm(Form):
    OPTIONS = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
    )
    correct_option = ChoiceField(widget = widgets.RadioSelect, choices = OPTIONS,)
