from django.urls import path, re_path
from .views import kullanici_takip_et_cikar, takipci_takip_edilen_listesi, kullanici_modal_takip_et_cikar, kullanici_takip_et_cikar_for_post

urlpatterns = [
    path("takiplesme/", kullanici_takip_et_cikar, name="takiplesme"),
    path("modal-takiplesme/", kullanici_modal_takip_et_cikar,
         name="modal-takiplesme"),
    path("takipci_takip_edilen_liste/<str:follow_type>/",
         takipci_takip_edilen_listesi, name="takipci_takip_edilen_listesi"),
    path("kullanici_takip_et_cikar_for_post/", kullanici_takip_et_cikar_for_post,
         name="kullanici_takip_et_cikar_for_post")

]
