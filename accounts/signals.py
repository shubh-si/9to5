from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User, SeekerProfile, EmployerProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        seeker_group, _ = Group.objects.get_or_create(name="Job Seekers")
        employer_group, _ = Group.objects.get_or_create(name="Employers")

        if instance.role == User.Role.JOB_SEEKER:
            SeekerProfile.objects.get_or_create(user=instance)
            instance.groups.add(seeker_group)
        elif instance.role == User.Role.EMPLOYER:
            EmployerProfile.objects.get_or_create(
                user=instance,
                defaults={"company_name": f"{instance.username}'s Company"},
            )
            instance.groups.add(employer_group)
