from django.shortcuts import render


def resource_not_found(request):
    context = {'path': request.path}
    response = render(request, 'resourceNotFound.html', context)
    response.status_code = 404
    return response


def server_error(request):
    response = render(request, 'serverError.html')
    response.status_code = 500
    return response
