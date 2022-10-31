import os
from celery import Celery
from celery import app


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogpost.settings")
app = Celery("django_celery")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# @app.on_after_finalize.connect
# def setup_periodic_tasks(sender, **kwargs):
#     #Executes every Saturday morning at 10:00 a.m.
#     sender.add_periodic_task(
#         crontab(hour=23, minute=50, day_of_week=7),
#         send_week_report.s(),
#     )


# @app.task
# def send_week_report():

#     now = datetime.now()
#     week_ago = datetime.now()-timedelta(days=7)
#     users = CustomUser.objects.filter(date_joined__range=(week_ago, now)).count()
#     posts = Post.objects.filter(created__range=(week_ago, now)).coun()
#     likes = Like.objects.filter(created__range=(week_ago, now)).count()

#     send_mail(
#         "Postways week report",
#         "Hi admin😉"
#         "\n\nFor the last week 'Postways' got\n"
#         f"new users: {users}\n"
#         f"new posts: {posts}\n"
#         f"new likes: {likes}\n"
#         "\nHave a nice weekend😉",
#         None,
#         ["ruslanways@gmail.com"]
#     )

