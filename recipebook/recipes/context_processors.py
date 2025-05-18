# recipes/context_processors.py
def user_data(request):
    return {
        'current_user': request.user,
    }