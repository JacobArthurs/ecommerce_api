import graphene
from products.queries import ProductQuery
from products.mutations import ProductMutations

class Query(ProductQuery, graphene.ObjectType):
    pass

class Mutation(ProductMutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)