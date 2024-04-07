from graphql_jwt.utils import jwt_payload
from django.contrib.auth.models import User

def jwt_payload_handler(user, request):
    payload = jwt_payload(user, request)

    groups = user.groups.all().values_list('name', flat=True)
    payload['groups'] = list(groups)
    return payload
