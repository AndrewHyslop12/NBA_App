from django import forms

class SearchByNameForm(forms.Form):
    
    player_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        "class": "form-control",
        "type": "text",
        "id": "player_name",
        "placeholder": "Enter an active players name to get started",
        "aria-describedby": "basic-addon2"
    }), label = "Player Name");
    