

class UserLastRequestMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f'SAVE datetime of user {request.user} request')
        response = self.get_response(request)
        return response

