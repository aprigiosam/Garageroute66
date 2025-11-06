from django.conf import settings

def garage_info(request):
    name = getattr(settings, "GARAGE_NAME", "Garage Route 66")
    return {
        "GARAGE_NAME": name,
    }
