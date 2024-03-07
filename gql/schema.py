import graphene
from products.queries import ProductQuery
from products.mutations import ProductMutations
from reviews.queries import ReviewQuery
from reviews.mutations import ReviewMutations

class Query(ProductQuery, ReviewQuery, graphene.ObjectType):
    pass

class Mutation(ProductMutations, ReviewMutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)