def is_admin (request):
    return {'is_admin': request.user.groups.filter(name='admin').exists()}

def is_customer (request):
    return {'is_customer': request.user.groups.filter(name='customer').exists()}
