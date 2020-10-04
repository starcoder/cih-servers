from django.urls import path

from . import views

app_name = "interact"
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:project_id>/', views.project, name="detail"),
    path('<int:project_id>/<int:entity_type_id>', views.entity_type, name="detail"),
    path('<int:project_id>/<int:entity_type_id>/<int:entity_id>', views.entity, name="detail"),
    path('<int:project_id>/visualization/<int:visualization_id>', views.visualization, name="visualization"),
    path('bottlenecks/<int:project_id>', views.bottlenecks, name="bottlenecks"),
    path('topics/<int:project_id>', views.topics, name="topics"),
    path('liwc/<int:project_id>', views.liwc, name="liwc"),
    path('vega/<int:project_id>/<int:visualization_id>', views.vega, name="vega"),
    path('vega/<int:project_id>', views.vega_grid, name="vega_grid"),
    path('vega/<int:project_id>/topics', views.vega_topics, name="vega_topics"),
    path('vega/<int:project_id>/bottlenecks', views.vega_bottlenecks, name="vega_bottlenecks"),
    path('vega/<int:project_id>/liwc', views.vega_liwc, name="vega_liwc"),
]
