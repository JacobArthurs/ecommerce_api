from graphql_jwt.utils import jwt_payload

def jwt_payload_handler(user, request):
    """
    Sets the payload for the JWT token.
    """
    payload = jwt_payload(user, request)

    groups = user.groups.all().values_list('name', flat=True)
    payload['groups'] = list(groups)
    return payload