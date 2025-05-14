from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import memory_game, CustomLoginView, user_scores, save_score,signup_view,save_after_login

urlpatterns = [
    path('', memory_game, name='memory_game'),
    path('signup/', signup_view, name='signup'),
    path('save-after-login/', save_after_login, name='save_after_login'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('save-score/', save_score, name='save_score'),
    path('scores/', user_scores, name='user_scores'),
]
