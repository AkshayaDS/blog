import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blogapp', '0001_initial'),
    ]

    operations = [
        # Replacing AlterUniqueTogether with constraints
        migrations.AlterModelOptions(
            name='favorite',
            options={},
        ),
        migrations.AlterField(
            model_name='blog',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='blog',
            name='category',
            field=models.CharField(
                choices=[
                    ('food', 'Food'),
                    ('travel', 'Travel'),
                    ('tech', 'Technology'),
                    ('lifestyle', 'Lifestyle'),
                    ('education', 'Education'),
                ],
                default='lifestyle',
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='blog',
            name='image',
            field=models.ImageField(
                upload_to='blog_images/',
                blank=True,
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='blog',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='favorites',
                to='blogapp.blog',
            ),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(
                fields=['user', 'blog'],
                name='unique_user_blog_favorite'
            ),
        ),
    ]
