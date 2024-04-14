import graphene
from datetime import datetime, time
from .types import TagType
from .models import Tag
from graphql_jwt.decorators import user_passes_test

class TagQuery(graphene.ObjectType):
    all_tags = graphene.List(
        TagType, 
        description="Retrieve all tags."
    )
    tag_by_id = graphene.Field(
        TagType, 
        id=graphene.Int(required=True, description="The ID of the tag to retrieve."), 
        description="Retrieve a single tag by its ID."
    )
    search_tags = graphene.List(
        TagType,
        name=graphene.String(default_value=None, description="A substring of the tag name to filter by. Case-insensitive."),
        tag_description=graphene.String(default_value=None, description="A substring of the tag description to filter by. Case-insensitive."),
        start_date=graphene.Date(default_value=None, description="The start date of tags to retrieve."),
        end_date=graphene.Date(default_value=None, description="The end date of tags to retrieve."),
        description="Search for tags based on various criteria such as title, and description."
    )

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    def resolve_all_tags(self, info):
        """
        Fetches all tags from the database.
        
        Returns:
            List of all tags.
        """
        return Tag.objects.all()
    
    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    def resolve_tag_by_id(self, info, id):
        """
        Retrieves a single tag by its ID.

        Returns:
            A tag if found, None otherwise.
        """
        return Tag.objects.filter(pk=id).first()

    @user_passes_test(lambda user: user.groups.filter(name='admin').exists())
    def resolve_search_tags(self, info, **kwargs):
        """
        Searches for tags matching the given criteria.
        
        Returns:
            List of tag instances matching the search criteria.
        """
        queryset = Tag.objects.all()

        if kwargs.get('name'):
            queryset = queryset.filter(name__icontains=kwargs['name'])
        if kwargs.get('tag_description'):
            queryset = queryset.filter(description__icontains=kwargs['tag_description'])
        if kwargs.get('start_date') is not None:
            start_datetime = datetime.combine(kwargs['start_date'], time.min)
            queryset = queryset.filter(created_at__gte=start_datetime)
        if kwargs.get('end_date') is not None:
            end_datetime = datetime.combine(kwargs['end_date'], time.max)
            queryset = queryset.filter(created_at__lte=end_datetime)
        
        return queryset