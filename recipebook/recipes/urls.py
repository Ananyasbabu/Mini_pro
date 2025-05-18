from django.urls import path, reverse
from django.contrib.auth import views as auth_views
from .views import (
    home,
    user_register, user_login, user_logout,
    user_profile, edit_profile,
    bmi_calculator, submit_bmi, get_weight_data,
    ingredient_book, add_ingredient, get_ingredients, delete_ingredient,
    leaderboard
)

urlpatterns = [
    # Home Page
    path("", home, name="home"),
    
    # Authentication
    path("register/", user_register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),

    # Password Reset (built-in Django views)
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="recipes/password_reset.html"
    ), name="password_reset"),
    
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="recipes/password_reset_done.html"
    ), name="password_reset_done"),
    
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="recipes/password_reset_confirm.html"
    ), name="password_reset_confirm"),
    
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name="recipes/password_reset_complete.html"
    ), name="password_reset_complete"),

    # User Profile
    path("profile/", user_profile, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    
    # BMI Calculator
    path("bmi/", bmi_calculator, name="bmi"),
    path("api/v1/bmi/", submit_bmi, name="submit_bmi"),
    path("api/v1/weight-data/", get_weight_data, name="get_weight_data"),
    
    # Ingredient Management
    path("ingredients/", ingredient_book, name="ingredients"),
  
    path("api/v1/ingredients/", get_ingredients, name="get_ingredients"),
    path("api/v1/ingredients/add/", add_ingredient, name="add_ingredient"),
    path("api/v1/ingredients/delete/", delete_ingredient, name="delete_ingredient"),


    
    # Leaderboard
    path("progress/", leaderboard, name="leaderboard"),
]
