from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Jméno a příjmení",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 rounded bg-green-100 text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-green-600",
                "placeholder": "Jméno a příjmení",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 rounded bg-green-100 text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-green-600",
                "placeholder": "Email",
            }
        ),
    )
    subject = forms.CharField(
        label="Předmět",
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 rounded bg-green-100 text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-green-600",
                "placeholder": "Předmět",
            }
        ),
    )
    message = forms.CharField(
        label="Zpráva",
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-4 py-2 rounded bg-green-100 text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-green-600",
                "placeholder": "Zpráva",
                "rows": 5,
            }
        ),
    )
