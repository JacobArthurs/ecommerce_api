from django.db import migrations

def create_user_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    admin_group = Group.objects.create(name='admin')
    user_group = Group.objects.create(name='user')

def remove_user_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    admin_group = Group.objects.filter(name='admin').delete()
    user_group = Group.objects.filter(name='user').delete()

class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunPython(create_user_groups, remove_user_groups),
    ]