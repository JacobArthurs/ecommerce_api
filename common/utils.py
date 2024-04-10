from graphql_jwt.utils import jwt_payload

def jwt_payload_handler(user, request):
    """
    Sets the payload for the JWT token.
    """
    payload = jwt_payload(user, request)

    groups = user.groups.all().values_list('name', flat=True)
    payload['groups'] = list(groups)
    return payload

def execute_mutation(self, mutation_name, variables):
    """
    Execute a GraphQL mutation based on provided variable values and their types.
    :param mutation_name: String name of the mutation.
    :param variables: Dictionary with keys as variable names and values as dicts including 'type' and 'value'.
    """
    variable_definitions = ", ".join(
        f"${name}: {details['type']}" for name, details in variables.items()
    )
    variable_arguments = ", ".join(
        f"{name}: ${name}" for name in variables.keys()
    )

    mutation = f'''
    mutation {mutation_name}({variable_definitions}) {{
        {mutation_name}({variable_arguments}) {{
            operationResult {{
                success
                message
            }}
        }}
    }}
    '''

    variable_values = {name: details['value'] for name, details in variables.items()}

    return self.query(
        mutation,
        operation_name=mutation_name,
        variables=variable_values
    )