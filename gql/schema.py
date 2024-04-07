import graphene
from products.queries import ProductQuery
from products.mutations import ProductMutations
from reviews.queries import ReviewQuery
from reviews.mutations import ReviewMutations
from tags.queries import TagQuery
from tags.mutations import TagMutations
from orders.queries import OrderQuery
from orders.mutations import OrderMutations
from users.queries import UserQuery
from users.mutations import UserMutations
from authentication.mutations import AuthenticationMutations

class Query(ProductQuery, ReviewQuery, TagQuery, OrderQuery, UserQuery, graphene.ObjectType):
    pass

class Mutation(ProductMutations, ReviewMutations, TagMutations, OrderMutations, UserMutations, AuthenticationMutations, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)