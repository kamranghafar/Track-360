from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import Resource
from django.db.models import Q


class Command(BaseCommand):
    help = 'Links Resource records to User accounts based on matching names or usernames'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Automatically link resources to users based on name matching',
        )
        parser.add_argument(
            '--resource',
            type=str,
            help='Resource name to link',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username to link to the resource',
        )

    def handle(self, *args, **options):
        if options['auto']:
            self.auto_link_resources()
        elif options['resource'] and options['user']:
            self.link_specific_resource(options['resource'], options['user'])
        else:
            self.stdout.write(self.style.WARNING('Please specify either --auto or both --resource and --user'))

    def auto_link_resources(self):
        """
        Automatically link resources to users based on name matching.
        Tries to match resource names with usernames or first/last names.
        """
        linked_count = 0
        resources = Resource.objects.filter(user__isnull=True)
        
        for resource in resources:
            # Try to find a matching user
            # First, try exact match on username
            user = User.objects.filter(username__iexact=resource.name.replace(' ', '.')).first()
            
            if not user:
                # Try to match on first name + last name
                name_parts = resource.name.split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                    user = User.objects.filter(
                        Q(first_name__iexact=first_name) & Q(last_name__iexact=last_name)
                    ).first()
            
            if not user:
                # Try to match on email if resource has email
                if resource.email:
                    user = User.objects.filter(email__iexact=resource.email).first()
            
            if user:
                resource.user = user
                resource.save()
                linked_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'Linked resource "{resource.name}" to user "{user.username}"'
                ))
        
        if linked_count == 0:
            self.stdout.write(self.style.WARNING('No resources were automatically linked to users'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully linked {linked_count} resources to users'))

    def link_specific_resource(self, resource_name, username):
        """
        Link a specific resource to a specific user.
        """
        try:
            resource = Resource.objects.get(name=resource_name)
        except Resource.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Resource "{resource_name}" not found'))
            return
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return
        
        resource.user = user
        resource.save()
        self.stdout.write(self.style.SUCCESS(
            f'Successfully linked resource "{resource.name}" to user "{user.username}"'
        ))