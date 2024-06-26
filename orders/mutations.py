import graphene
from gql.types import OperationResult
from .models import Order, OrderItem
from .types import CreateOrderInput
from products.models import Product
from graphql_jwt.decorators import login_required

class CreateOrder(graphene.Mutation):
    """
    Creates a order based on the provided inputs. Validates input to ensure any provided cost or
    supply values are positive if provided.
    """
    class Arguments:
        order_items = graphene.List(CreateOrderInput, required=True, description="The items in the order with quantities, required.")

    operation_result = graphene.Field(OperationResult)

    @login_required
    @staticmethod
    def mutate(root, info, order_items):
        product_ids = [int(item.product_id) for item in order_items]
        products = Product.objects.in_bulk(product_ids)

        if len(products) != len(set(product_ids)):
            return CreateOrder(operation_result=OperationResult(success=False, message="One or more products not found."))
        
        if any(item.quantity < 1 for item in order_items):
            return CreateOrder(operation_result=OperationResult(success=False, message="One or more quantities are less than 1."))

        order = Order(total_cost=sum(products[int(item.product_id)].cost * item.quantity for item in order_items), user=info.context.user)
        order.save()

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=products[int(item.product_id)],
                quantity=item.quantity,
                cost=products[int(item.product_id)].cost
            ) for item in order_items
        ])

        return CreateOrder(operation_result=OperationResult(success=True, message="Order created successfully."))

class UpdateOrderItem(graphene.Mutation):
    """
    Updates an existing order item's details based on the provided inputs.
    The price will be set to the product's current price.
    """
    class Arguments:
        id = graphene.ID(required=True, description="The ID of the order item to update, required.")
        quantity = graphene.Int(required=True, description="The quantity of the order item, required.")

    operation_result = graphene.Field(OperationResult)

    @login_required
    @staticmethod
    def mutate(root, info, id, quantity):
        if quantity < 1:
            return UpdateOrderItem(operation_result=OperationResult(success=False, message="One or more quantities are less than 1."))

        try:
            order_item = OrderItem.objects.get(pk=id)
        except OrderItem.DoesNotExist:
            return UpdateOrderItem(operation_result=OperationResult(success=False, message="Order item not found."))
        
        if order_item.order.user != info.context.user and not info.context.user.groups.filter(name='admin').exists():
            return UpdateOrderItem(operation_result=OperationResult(success=False, message="You can only edit your own orders."))

        order_item.quantity = quantity
        order_item.cost = order_item.product.cost
        order_item.save()

        order = order_item.order
        order.total_cost = sum(order_item.cost * order_item.quantity for order_item in order.items.all())
        order.save()
        
        return UpdateOrderItem(operation_result=OperationResult(success=True, message="Order item updated successfully."))

class DeleteOrder(graphene.Mutation):
    """
    Deletes a order by its ID.
    """
    class Arguments:
        id = graphene.ID(required=True, description="The ID of the order to be deleted.")

    operation_result = graphene.Field(OperationResult)

    @login_required
    @staticmethod
    def mutate(root, info, id):
        try:
            order = Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return DeleteOrder(operation_result=OperationResult(success=False, message="Order not found."))
        
        if order.user != info.context.user  and not info.context.user.groups.filter(name='admin').exists():
            return DeleteOrder(operation_result=OperationResult(success=False, message="You can only delete your own orders."))

        order.delete()

        return DeleteOrder(operation_result=OperationResult(success=True, message="Order deleted successfully."))
    
class DeleteOrderItem(graphene.Mutation):
    """
    Deletes a order item by its ID.
    """
    class Arguments:
        id = graphene.ID(required=True, description="The ID of the order item to be deleted.")

    operation_result = graphene.Field(OperationResult)

    @login_required
    @staticmethod
    def mutate(root, info, id):
        try:
            order_item = OrderItem.objects.get(pk=id)
        except OrderItem.DoesNotExist:
            return DeleteOrderItem(operation_result=OperationResult(success=False, message="Order item not found."))
        
        if order_item.order.user != info.context.user and not info.context.user.groups.filter(name='admin').exists():
            return DeleteOrderItem(operation_result=OperationResult(success=False, message="You can only delete your own orders."))

        order_item.delete()

        order = order_item.order
        order.total_cost = sum(order_item.cost * order_item.quantity for order_item in order.items.all())
        order.save()

        return DeleteOrderItem(operation_result=OperationResult(success=True, message="Order item deleted successfully."))

class OrderMutations(graphene.ObjectType):
    create_order = CreateOrder.Field(description="Creates a new order with the specified details.")
    update_order_item = UpdateOrderItem.Field(description="Updates an existing order with new values.")
    delete_order = DeleteOrder.Field(description="Deletes the order identified by the given ID.")
    delete_order_item = DeleteOrderItem.Field(description="Deletes the order item identified by the given ID.")