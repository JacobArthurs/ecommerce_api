import graphene
import graphql_jwt

class AuthenticationMutations(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field(description="Authenticates a user with the specified username and password.")
    verify_token = graphql_jwt.Verify.Field(description="Verifies a JWT token.")
    refresh_token = graphql_jwt.Refresh.Field(description="Refreshes a JWT token.")