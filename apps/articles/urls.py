from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.AccueilView.as_view(), name='accueil'),
    path('articles/', views.ArticleListView.as_view(), name='liste'),
    path('articles/<slug:slug>/', views.ArticleDetailView.as_view(), name='detail'),
    path('categorie/<slug:slug>/', views.ArticleParCategorieView.as_view(), name='par_categorie'),
    path('tag/<slug:slug>/', views.ArticleParTagView.as_view(), name='par_tag'),
    path('recherche/', views.RechercheView.as_view(), name='recherche'),
]



# Routes journaliste
from . import views as v
urlpatterns += [
    path('redaction/', v.MesArticlesView.as_view(), name='mes_articles'),
    path('redaction/nouveau/', v.CreerArticleView.as_view(), name='creer_article'),
    path('redaction/<slug:slug>/modifier/', v.ModifierArticleView.as_view(), name='modifier_article'),
    path('redaction/<slug:slug>/supprimer/', v.SupprimerArticleView.as_view(), name='supprimer_article'),
]

