from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Ingredient, UserWeight, CustomUser
import logging
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)
from django.views.decorators.csrf import csrf_exempt

# Utility Functions
def get_bmi_category(bmi):
    """Helper function to categorize BMI values"""
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal"
    elif 25 <= bmi < 30:
        return "Overweight"
    return "Obese"

# Authentication Views
def user_register(request):
    """Handles user registration with validation"""
    if request.method == "POST":
        try:
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip().lower()
            password = request.POST.get("password", "")
            profile_picture = request.FILES.get("profile_picture")

            # Validation
            if not all([username, email, password]):
                raise ValidationError("All fields are required")
            
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("Email is already in use")

            if profile_picture:
                if profile_picture.size > 2 * 1024 * 1024:  # 2MB limit
                    raise ValidationError("Profile picture too large (max 2MB)")
                if not profile_picture.content_type in ['image/jpeg', 'image/png']:
                    raise ValidationError("Only JPEG or PNG images allowed")

            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            if profile_picture:
                user.profile_picture = profile_picture
                user.save()

            return redirect("login")
        
        except ValidationError as e:
            return render(request, "recipes/register.html", {"error": str(e)})
        except IntegrityError:
            return render(request, "recipes/register.html", {"error": "Username already exists"})
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return render(request, "recipes/register.html", {"error": "An error occurred during registration"})

    return render(request, "recipes/register.html")


def user_login(request):
    """Handles user authentication"""

    if request.method == "POST":
        email = request.POST.get("email", "").lower()
        password = request.POST.get("password", "")
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
        
        return render(request, "recipes/login.html", {
            "error": "Invalid email or password",
            "email": email
        })

    return render(request, "recipes/login.html")


@login_required
def user_logout(request):
    """Handles user logout"""
    logout(request)
    return redirect("login")


# Profile Views
@login_required
def user_profile(request):
    """Displays user profile"""
    return render(request, "recipes/profile.html", {"user": request.user})


@login_required
def edit_profile(request):
    """Handles profile updates"""
    if request.method == "POST":
        try:
            user = request.user
            new_username = request.POST.get("username", "").strip()
            new_email = request.POST.get("email", "").strip().lower()
            new_picture = request.FILES.get("profile_picture")

            # Validate username
            if new_username and new_username != user.username:
                if CustomUser.objects.filter(username=new_username).exists():
                    raise ValidationError("Username already taken")
                user.username = new_username

            # Validate email
            if new_email and new_email != user.email:
                if CustomUser.objects.filter(email=new_email).exists():
                    raise ValidationError("Email already in use")
                user.email = new_email

            # Validate profile picture
            if new_picture:
                if new_picture.size > 2 * 1024 * 1024:
                    raise ValidationError("Profile picture too large (max 2MB)")
                if not new_picture.content_type in ['image/jpeg', 'image/png']:
                    raise ValidationError("Only JPEG or PNG images allowed")
                
                # Delete old picture if exists
                if user.profile_picture:
                    default_storage.delete(user.profile_picture.path)
                user.profile_picture = new_picture

            user.save()
            return redirect("profile")

        except ValidationError as e:
            return render(request, "recipes/edit_profile.html", {
                "user": request.user,
                "error": str(e)
            })
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return render(request, "recipes/edit_profile.html", {
                "user": request.user,
                "error": "An error occurred while updating your profile"
            })

    return render(request, "recipes/edit_profile.html", {"user": request.user})


# BMI Calculator Views
@login_required
def bmi_calculator(request):
    """Displays BMI calculator page"""
    return render(request, "recipes/bmi.html")

@csrf_exempt
@login_required
def submit_bmi(request):
    """Handles BMI calculation and storage"""
    if request.method == "POST":
        try:
            height = float(request.POST.get("height", 0))
            weight = float(request.POST.get("weight", 0))
            
            if height <= 0 or weight <= 0:
                raise ValidationError("Height and weight must be positive values")
            
            height_in_m = height / 100  # Convert cm to m
            bmi = round(weight / (height_in_m ** 2), 2)
            category = get_bmi_category(bmi)
            
            UserWeight.objects.create(
                user= request.user,
                weight=weight,
                bmi=bmi
            )
            
            return JsonResponse({
                "message": "BMI recorded successfully",
                "bmi": bmi,
                "category": category
            })
            
        except (ValueError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"BMI submission error: {str(e)}")
            return JsonResponse({"error": "An error occurred"}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)


@login_required
def get_weight_data(request):
    """Provides weight data for charts"""
    try:
        weight_entries = UserWeight.objects.filter(user=request.user).order_by("-date")[:10]  # Last 10 entries

        if not weight_entries.exists():
            return JsonResponse({"labels": [], "weights": [], "bmis": [], "message": "No recent data found"}, status=200)

        data = {
            "labels": [entry.date.strftime("%Y-%m-%d") for entry in weight_entries],
            "weights": [float(entry.weight) for entry in weight_entries],
            "bmis": [float(entry.bmi) for entry in weight_entries]
        }
        
        return JsonResponse(data, status=200)
    
    except Exception as e:
        logger.error(f"❌ Weight data fetch error: {str(e)}")
        return JsonResponse({"error": "Failed to fetch weight data", "details": str(e)}, status=500)



# Ingredient Views
@login_required
def ingredient_book(request):
    """Displays ingredient management interface"""
    return render(request, "recipes/ingredients.html")


@csrf_exempt
@login_required
def add_ingredient(request):
    print("✅ Request received to add ingredient")
    print("User:", request.user)

    if not request.user.is_authenticated:
        print("❌ User is not authenticated!")
        return JsonResponse({"error": "User is not logged in"}, status=401)

    if request.method == "POST":
        try:
            import json
            data = json.loads(request.body.decode("utf-8"))
            ingredient_name = data.get("name", "").strip()

            print("✅ Ingredient received:", ingredient_name)

            if not ingredient_name:
                return JsonResponse({"error": "Ingredient name cannot be empty"}, status=400)

            Ingredient.objects.create(user=request.user, name=ingredient_name)
            print("✅ Ingredient added successfully!")
            return JsonResponse({"message": "Ingredient added successfully"}, status=201)

        except Exception as e:
            print("❌ Error adding ingredient:", str(e))
            return JsonResponse({"error": "Failed to add ingredient", "details": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)




@login_required
def get_ingredients(request):
    """Returns user's ingredients list"""
    try:
        ingredients = list(Ingredient.objects.filter(
            user=request.user
        ).order_by("name").values_list("name", flat=True))
        
        return JsonResponse({"ingredients": ingredients})
    
    except Exception as e:
        logger.error(f"Ingredients fetch error: {str(e)}")
        return JsonResponse({"error": "Failed to fetch ingredients"}, status=500)


@login_required
def delete_ingredient(request):
    """Deletes a user's ingredient"""
    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            
            if not name:
                raise ValidationError("Ingredient name required")
            
            deleted, _ = Ingredient.objects.filter(
                user=request.user,
                name__iexact=name
            ).delete()
            
            if not deleted:
                raise ValidationError("Ingredient not found")
            
            return JsonResponse({"message": "Ingredient deleted successfully"})
            
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            logger.error(f"Ingredient delete error: {str(e)}")
            return JsonResponse({"error": "Failed to delete ingredient"}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)


# Leaderboard View
@login_required
def leaderboard(request):
    """Displays weight progress leaderboard"""
    return render(request, "recipes/leaderboard.html")


# Home Page
def home(request):
    """Displays the home page"""
    return render(request, "recipes/index.html")