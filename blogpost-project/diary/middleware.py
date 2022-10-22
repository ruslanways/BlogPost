import logging

from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse

class UserLastRequestMiddleware:
    """
    Saves the datetime of last user request.
    Doesn't for AnonymousUser. 
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print()
        if request.user.is_authenticated:
            request.user.last_request = timezone.now()
            request.user.save()
        response = self.get_response(request)
        return response


logger = logging.getLogger(__name__)

class UncaughtExceptionMiddleware:
    """
    Handles uncaught exceptions: loges it.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        logger.error(f'Exception {type(exception)}, User: {request.user}, Page requested: {request.get_full_path()}')
        if request.path.startswith('/api/'):
            return JsonResponse({'Uncaught Exception': str(exception)}, status=500)
        return render(request, '500.html', status=500)