from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Feedback, Eleve, Cours

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['type_feedback', 'eleve', 'cours', 'sujet', 'message', 'priorite']
        widgets = {
            'type_feedback': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'eleve': forms.Select(attrs={
                'class': 'form-select',
                'required': False
            }),
            'cours': forms.Select(attrs={
                'class': 'form-select',
                'required': False
            }),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the subject of your feedback',
                'required': True,
                'maxlength': 200
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your question or concern in detail...',
                'rows': 5,
                'required': True
            }),
            'priorite': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            })
        }
    
    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        super().__init__(*args, **kwargs)
        
        if parent:
            # Filtrer les enfants du parent
            self.fields['eleve'].queryset = Eleve.objects.filter(parent=parent)
            self.fields['eleve'].empty_label = "Select a child (optional)"
            
            # Filtrer les cours des enfants du parent
            enfants = Eleve.objects.filter(parent=parent)
            self.fields['cours'].queryset = Cours.objects.filter(
                classe__in=[enfant.classe for enfant in enfants]
            ).order_by('-date', 'heure_debut')
            self.fields['cours'].empty_label = "Select a course (optional)"
        
        # Personnaliser les labels
        self.fields['type_feedback'].label = "Type of feedback"
        self.fields['eleve'].label = "Child (optional)"
        self.fields['cours'].label = "Course (optional)"
        self.fields['sujet'].label = "Subject"
        self.fields['message'].label = "Message"
        self.fields['priorite'].label = "Priority"