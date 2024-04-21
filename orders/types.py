import graphene
from graphene_django import DjangoObjectType
from .models import Order, OrderItem

class OrderItemType(DjangoObjectType):
    """
    Represents the Order item model in GraphQL. This type exposes all fields of the Order item 
    model, facilitating queries on products in the database.
    """
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderType(DjangoObjectType):
    """
    Represents the Order model in GraphQL. This type exposes all fields of the Order model,
    facilitating queries on products in the database.
    """
    items = graphene.List(OrderItemType)

    class Meta:
        model = Order
        fields = '__all__'

    def resolve_items(self, info):
        return self.items.all()

class OrdersPerMonthType(graphene.ObjectType):
    """
    Represents the count of orders created each month. It encapsulates
    the month and the count of orders for easier aggregation and presentation.
    """
    month = graphene.String(description="The name of the month in 'Month YYYY' format.")
    order_count = graphene.Int(description="The count of orders created in that month.")
    order_cost = graphene.Float(description="The total cost of orders in that month.")

class CreateOrderInput(graphene.InputObjectType):
    """
    Represents the input needed to create an order.
    """
    product_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True)