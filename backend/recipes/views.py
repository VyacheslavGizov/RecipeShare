from django.shortcuts import redirect


def redirect_to_recipe(request, pk):
    return redirect(request.build_absolute_uri(f'/recipes/{pk}'))
