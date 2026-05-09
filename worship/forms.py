from django import forms
from .models import ProductReview, ProductQA

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class ProductQAForm(forms.ModelForm):
    class Meta:
        model = ProductQA
        fields = ['question']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 2}),
        }
