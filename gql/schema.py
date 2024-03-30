import graphene
from products.queries import ProductQuery
from products.mutations import ProductMutations
from reviews.queries import ReviewQuery
from reviews.mutations import ReviewMutations
from tags.queries import TagQuery
from tags.mutations import TagMutations
from orders.queries import OrderQuery
from orders.mutations import OrderMutations


class Query(ProductQuery, ReviewQuery, TagQuery, OrderQuery, graphene.ObjectType):
    pass

class Mutation(ProductMutations, ReviewMutations, TagMutations, OrderMutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)