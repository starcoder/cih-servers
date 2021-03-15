from django.conf.urls import include, url
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .models import starcoder_models, starcoder_reconstruction_models
from .views import starcoder_list_views, starcoder_detail_views, ProjectListView, ProjectDetailView, EntityListView, EntityDetailView, about_view, editor_view
from turkle import views as turkle_views

app_name = "interact"
urlpatterns = [
    path('', ProjectListView.as_view(), name='project_list'),
    url(r'turkle', include('turkle.urls')),
    path('about', about_view, name="about"),
    path('editor', editor_view, name="editor"),
    path('project/<int:pk>/', ProjectDetailView.as_view(), name="project_detail"),
    path('schema/<int:project_id>/', views.schema, name="schema"),
    path('entities/<int:entity_type_id>', EntityListView.as_view(), name="entity_list"),    
    path('entity/<int:entity_type_id>/<int:pk>/', EntityDetailView.as_view(), name="entity_detail"),
    
    path('bottlenecks/<int:project_id>', views.bottlenecks, name="bottlenecks"),
    path('topics/<int:project_id>', views.topics, name="topics"),
    path('liwc/<int:project_id>', views.liwc, name="liwc"),
    path('figure/<int:project_id>/<str:entity>/<str:field>', views.figure, name="figure"),

    path('vega/<int:project_id>/<str:entity>/<str:independent_field>', views.vega, name="vega"),
    path('vega/<int:project_id>/topics', views.vega_topics, name="vega_topics"),
    path('vega/<int:project_id>/bottlenecks', views.vega_bottlenecks, name="vega_bottlenecks"),
    path('vega/<int:project_id>/liwc', views.vega_liwc, name="vega_liwc"),
    path('vega/<int:project_id>/schema', views.vega_schema, name="vega_schema"),
    path('vega/<int:project_id>/model', views.vega_model, name="vega_model"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

