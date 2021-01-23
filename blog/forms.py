from django import forms
from .models import Blog, Yorum
from ckeditor.widgets import CKEditorWidget

banned_email_list = ['onur@gmail.com','test@test.com','a@a.com']

class iletisimForm(forms.Form):
    isim = forms.CharField(max_length=50,label="İsim", required=False)
    soyisim = forms.CharField(max_length=50, label="Soyisim", required=False)
    email = forms.EmailField(max_length=100, label="Email", required=True)
    email2= forms.EmailField(max_length=100, label="Email2", required=True)
    icerik = forms.CharField(max_length=1000, label="İçerik", required=True)

    def __init__(self,*args, **kwargs):
        super(iletisimForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class':'form-control'}
        self.fields['icerik'].widget = forms.Textarea(attrs={'class': 'form-control'})
        #self.fields['icerik'] = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

    def clean_isim(self):
        isim = self.cleaned_data.get("isim")
        if isim == 'ahmet':
            raise forms.ValidationError("Kral sen giremen!")
        return isim

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email in banned_email_list:
            raise forms.ValidationError('Lütfen banlı email girmeyin.')
        return email
    
    def clean(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")

        if email != email2:
            self.add_error('email',"Email eşleşmedi")
            self.add_error('email2',"Email eşleşmedi")
    

class blogForm(forms.ModelForm):
    icerik = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Blog
        fields = ['title','image','icerik','yayin_taslak','kategoriler']

    def __init__(self,*args, **kwargs):
        super(blogForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class':'form-control'}
        self.fields['icerik'].widget.attrs['rows'] = 10

    def clean_icerik(self):
        icerik = self.cleaned_data.get('icerik')
        if len(icerik) < 250:
            uzunluk = len(icerik)
            msg = "Lütfen en az 250 karakter giriniz. Şuan girilen karakter: (%s)"%(uzunluk)
            raise forms.ValidationError(msg)
        return icerik

class PostSorguForm(forms.Form):

    search = forms.CharField(max_length=500, widget= forms.TextInput(attrs={'placeholder':'Arama..','class':'form-control'}), 
    required=False)

    taslak_yayin = forms.ChoiceField(widget= forms.Select(attrs={'class':'form-control'}), 
                                        choices= (('yayin','YAYIN'),('taslak', 'TASLAK'),('hepsi', 'HEPSI')),
                                        required=False)

class YorumForm(forms.ModelForm):

    class Meta:
        model = Yorum
        fields = ['icerik']

    def __init__(self,*args, **kwargs):
        super(YorumForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs = {'class':'form-control'}
