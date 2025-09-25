from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'completed']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zadajte názov úlohy...',
                'maxlength': 200,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Podrobný popis úlohy (voliteľné)...',
                'rows': 4,
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat(),
            }),
            'completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'title': '📌 Názov úlohy',
            'description': '📝 Popis',
            'due_date': '📅 Termín splnenia',
            'completed': '✅ Dokončené',
        }
        help_texts = {
            'title': 'Krátky a výstižný názov úlohy (povinné)',
            'description': 'Podrobnejší popis úlohy, poznámky (voliteľné)',
            'due_date': 'Dátum, kedy má byť úloha dokončená',
            'completed': 'Označte, ak je úloha už dokončená',
        }

    def clean_title(self):
        """Validácia názvu úlohy"""
        title = self.cleaned_data.get('title')

        if not title:
            raise ValidationError('Názov úlohy je povinný!')

        title = title.strip()

        if len(title) < 3:
            raise ValidationError('Názov úlohy musí mať aspoň 3 znaky!')

        if len(title) > 200:
            raise ValidationError('Názov úlohy je príliš dlhý (max. 200 znakov)!')

        # Kontrola duplicitných úloh (len pre nové úlohy)
        if not self.instance.pk:
            if Task.objects.filter(title__iexact=title).exists():
                raise ValidationError('Úloha s týmto názvom už existuje!')

        return title

    def clean_description(self):
        """Validácia popisu úlohy"""
        description = self.cleaned_data.get('description')

        if description:
            description = description.strip()

            if len(description) > 1000:
                raise ValidationError('Popis je príliš dlhý (max. 1000 znakov)!')

        return description

    def clean_due_date(self):
        """Validácia termínu splnenia"""
        due_date = self.cleaned_data.get('due_date')

        if due_date:
            today = timezone.now().date()

            # Varovanie pre minulé dátumy (ale neblokujeme ich)
            if due_date < today:
                # Pre aktualizáciu existujúcej úlohy povolíme minulé dátumy
                if self.instance.pk:
                    return due_date
                else:
                    raise ValidationError('Termín splnenia nemôže byť v minulosti!')

            # Varovanie pre príliš vzdialené dátumy
            max_date = today.replace(year=today.year + 2)
            if due_date > max_date:
                raise ValidationError('Termín splnenia je príliš vzdialený (max. 2 roky)!')

        return due_date

    def clean(self):
        """Celková validácia formulára"""
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        due_date = cleaned_data.get('due_date')
        completed = cleaned_data.get('completed')

        # Ak je úloha označená ako dokončená, ale nemá termín, nastaví sa na dnes
        if completed and not due_date:
            cleaned_data['due_date'] = timezone.now().date()

        # Kontrola logiky - dokončená úloha s budúcim termínom
        if completed and due_date and due_date > timezone.now().date():
            # Len upozornenie, nie chyba
            self.add_error(None, 'Pozor: Označujete úlohu ako dokončenú, ale termín je v budúcnosti.')

        return cleaned_data


class TaskSearchForm(forms.Form):
    """Formulár pre vyhľadávanie a filtrovanie úloh"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '🔍 Hľadať úlohy...',
        }),
        label='Vyhľadávanie'
    )

    STATUS_CHOICES = [
        ('', 'Všetky úlohy'),
        ('completed', 'Dokončené'),
        ('pending', 'Čakajúce'),
        ('overdue', 'Po termíne'),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Stav'
    )

    DUE_CHOICES = [
        ('', 'Všetky termíny'),
        ('today', 'Dnes'),
        ('week', 'Tento týždeň'),
        ('month', 'Tento mesiac'),
    ]

    due_filter = forms.ChoiceField(
        choices=DUE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Termín'
    )

    SORT_CHOICES = [
        ('created_at', 'Dátum vytvorenia'),
        ('title', 'Názov'),
        ('due_date', 'Termín splnenia'),
        ('completed', 'Stav'),
    ]

    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='created_at',
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Zoradiť podľa'
    )

    ORDER_CHOICES = [
        ('desc', 'Zostupne'),
        ('asc', 'Vzostupne'),
    ]

    order = forms.ChoiceField(
        choices=ORDER_CHOICES,
        required=False,
        initial='desc',
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Poradie'
    )