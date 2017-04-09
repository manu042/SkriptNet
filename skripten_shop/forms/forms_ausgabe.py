from django import forms


class ScanLegicForm(forms.Form):
    """
    Form zum Scannen der Legic ID bei der Ausgabe
    """
    legic_id = forms.CharField(label="Legic-ID", widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))


class ActivateStudentForm(forms.Form):
    """
    Form zum verknüpfen einer Legic ID mit dem Account eines Studenten
    """
    legic_id = forms.CharField(label="Legic-ID")
    birth_date = forms.DateField(label="Geburtsdatum (TT.MM.JJJJ)",
                                 widget=forms.DateInput(attrs={'autofocus': 'autofocus'}))


class NewLegicCardForm(forms.Form):
    """
    Form zur Eingabe einer neuen Legic-ID
    """
    email = forms.EmailField(max_length=100, label='E-Mail Adresse',
                             widget=forms.EmailInput(attrs={'autofocus': 'autofocus'}))
    new_legic_id = forms.CharField(label="Neue Legic-ID")
