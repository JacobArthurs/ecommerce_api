import graphene
from django.db.models import Count, Sum, F, DecimalField
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from datetime import datetime, time
from .types import OrderType, OrdersPerMonthType
from .models import Order, OrderItem

class OrderQuery(graphene.ObjectType):
    all_orders = graphene.List(
        OrderType, 
        description="Retrieve all orders."
    )
    order_by_id = graphene.Field(
        OrderType, 
        id=graphene.Int(required=True, description="The ID of the order to retrieve."), 
        description="Retrieve a single order by its ID."
    )
    search_orders = graphene.List(
        OrderType,
        min_cost=graphene.Float(default_value=None, description="The minimum cost of orders to retrieve."),
        max_cost=graphene.Float(default_value=None, description="The maximum cost of orders to retrieve."),
        start_date=graphene.Date(default_value=None, description="The start date of orders to retrieve."),
        end_date=graphene.Date(default_value=None, description="The end date of orders to retrieve."),
        description="Search for orders based on various criteria such as name, description, cost range, and supply range."
    )
    orders_per_month = graphene.List(
        OrdersPerMonthType, 
        last_n_months=graphene.Int(required=True, description="The number of months to include in the count, counting backwards from the current month."),
    )

    def resolve_all_orders(self, info):
        """
        Fetches all order instances from the database.
        
        Returns:
            List of all Order instances.
        """
        return Order.objects.all()
    
    def resolve_order_by_id(self, info, id):
        """
        Retrieves a single Order by its ID.

        Returns:
            A Order if found, None otherwise.
        """
        return Order.objects.filter(pk=id).first()

    def resolve_search_orders(self, info, **kwargs):
        """
        Searches for orders matching the given criteria.
        
        Returns:
            List of Order instances matching the search criteria.
        """
        queryset = Order.objects.all()

        if kwargs.get('min_cost') is not None:
            queryset = queryset.filter(total_cost__gte=kwargs['min_cost'])
        if kwargs.get('max_cost') is not None:
            queryset = queryset.filter(total_cost__lte=kwargs['max_cost'])
        if kwargs.get('start_date') is not None:
            start_datetime = datetime.combine(kwargs['start_date'], time.min)
            queryset = queryset.filter(created_at__gte=start_datetime)
        if kwargs.get('end_date') is not None:
            end_datetime = datetime.combine(kwargs['end_date'], time.max)
            queryset = queryset.filter(created_at__lte=end_datetime)

        return queryset
    
    def resolve_orders_per_month(self, info, last_n_months):
        """
        Calculates the number of orders created and the cost of orders created each month for the last N months.
        
        Returns:
            A list of OrdersPerMonthType instances, each representing the order count for a month.
        """
        end_date = now().date().replace(day=1) + relativedelta(months=1) - relativedelta(days=1)
        start_date = end_date.replace(day=1) - relativedelta(months=last_n_months-1)

        queryset = Order.objects \
            .filter(created_at__date__gte=start_date, created_at__date__lte=end_date) \
            .annotate(month=TruncMonth('created_at')) \
            .values('month') \
            .annotate(order_count=Count('id'), order_cost=Sum('total_cost')) \
            .order_by('month')
        
        order_count_dict = {item['month'].strftime("%B %Y"): (item['order_count'], item['order_cost']) for item in queryset}
        months_in_range = [(start_date + relativedelta(months=i)).strftime("%B %Y") for i in range(last_n_months)]

        return [
            OrdersPerMonthType(
                month=month,
                order_count=order_count_dict.get(month, (0, 0))[0],
                order_cost=order_count_dict.get(month, (0, 0))[1]
            ) for month in months_in_range
        ]
