import graphene

class OperationResult(graphene.ObjectType):
    success = graphene.Boolean(required=True, description="Indicates if the operation was successful.")
    message = graphene.String(description="A message related to the operation's outcome, which could be an error message or a success confirmation.")