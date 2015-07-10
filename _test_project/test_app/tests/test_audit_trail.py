import datetime
from django.test import TestCase
import audit_trail
from audit_trail.models import AuditTrail
from ..models import TestModelTrackAllFields, TestModelTrackOneField, TestModelWithFieldLabels, \
    Post, Comment, User, AA, AB, BB, ShortcutTestModel, Post1, Comment1, Person, Animal, SomePerson


class TestAuditTrail(TestCase):
    def test_create_audit_trail_on_creation(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.CREATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': None,
                'new_value': 'a',
                'field_label': 'Char'
            }
        })

    def test_create_audit_trail_on_deletion(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        model.delete()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.DELETED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': 'a',
                'new_value': None,
                'field_label': 'Char'
            }
        })

    def test_audit_for_selected_field(self):
        self.assertEqual(AuditTrail.objects.all().count(), 0)
        model = TestModelTrackOneField.objects.create(char='a')

        model.text = 'sometext'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        model.char = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': 'a',
                'new_value': 'b',
                'field_label': 'Char'
            }
        })

    def test_audit_trail_history_for_all_fields(self):
        model = TestModelTrackAllFields.objects.create(char='a', char2='x')
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        model.char = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': 'a',
                'new_value': 'b',
                'field_label': 'Char'
            }
        })

        model.char2 = 'y'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 3)

        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char2': {
                'old_value': 'x',
                'new_value': 'y',
                'field_label': 'Char2'
            }
        })

        trail = AuditTrail.objects.all()[1]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': 'a',
                'new_value': 'b',
                'field_label': 'Char'
            }
        })

        model.char = 'c'
        model.char2 = 'z'
        model.save()

        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': 'b',
                'new_value': 'c',
                'field_label': 'Char'
            },
            'char2': {
                'old_value': 'y',
                'new_value': 'z',
                'field_label': 'Char2'
            }
        })

    def test_field_labels(self):
        TestModelWithFieldLabels.objects.create(char='a', char2='x', char_3='1')
        trail = AuditTrail.objects.all()[0]

        self.assertEqual(trail.get_changes()['char']['field_label'], 'Char 1')
        self.assertEqual(trail.get_changes()['char2']['field_label'], 'Char 2')
        self.assertEqual(trail.get_changes()['char_3']['field_label'], 'Char 3')

    def test_related_tracking_init_watcher_for_subclass(self):
        # We only initialized audit on Post but Comment.should be created automatically
        self.assertIsNotNone(getattr(Comment, 'audit', None))

    def test_related_tracking(self):
        author = User.objects.create()
        post = Post.objects.create(author=author)
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        comment = Comment.objects.create()
        self.assertEqual(AuditTrail.objects.all().count(), 1)

        comment = Comment.objects.create(post=post)
        self.assertEqual(AuditTrail.objects.all().count(), 3)

        post_trail = AuditTrail.objects.all()[0]
        comment_trail = AuditTrail.objects.all()[1]
        self.assertEqual(post_trail.action, AuditTrail.ACTIONS.RELATED_CHANGED)
        self.assertEqual(post_trail.related_trail, comment_trail)

    def test_fk_tracking(self):
        author = User.objects.create()
        self.assertEqual(AuditTrail.objects.all().count(), 0)
        post = Post.objects.create(author=author)
        self.assertEqual(AuditTrail.objects.all().count(), 1)
        author.name = 'new name'
        author.save()
        self.assertEqual(AuditTrail.objects.all().count(), 3)

        post_trail = AuditTrail.objects.all()[0]
        user_trail = AuditTrail.objects.all()[1]
        self.assertEqual(post_trail.action, AuditTrail.ACTIONS.RELATED_CHANGED)
        self.assertEqual(post_trail.related_trail, user_trail)

        author.delete()
        self.assertEqual(AuditTrail.objects.all().count(), 5)

    def test_related_tracking_ordering(self):
        self.assertEqual(AA.audit.track_related, ['ab_set'])
        self.assertEqual(BB.audit.track_related, ['ab_set'])
        self.assertEqual(AB.audit.track_only_with_related, False)
        self.assertEqual(sorted(AB.audit.notify_related), ['aa', 'bb'])

    def test_shortcut(self):
        model = ShortcutTestModel.objects.create(name='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.CREATED)
        self.assertEqual(trail.get_changes(), {
            'name': {
                'old_value': None,
                'new_value': 'a',
                'field_label': 'Name'
            }
        })

    def test_shortcut_override_class_attribute(self):
        self.assertEqual(Post1.audit.track_related, ['comment1_set'])
        self.assertEqual(Comment1.audit.track_only_with_related, False)
        self.assertEqual(Comment1.audit.fields, ['text'])

    def test_queryset_changes(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.CREATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': None,
                'new_value': 'a',
                'field_label': 'Char'
            }
        })

        model.char2 = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char2': {
                'old_value': None,
                'new_value': 'b',
                'field_label': 'Char2'
            }
        })

        trails = audit_trail.get_for_object(model)
        self.assertEqual(trails.get_changes(), {
            'char2': {
                'old_value': None,
                'new_value': 'b',
                'field_label': 'Char2',
                'field_name': 'char2'
            },
            'char': {
                'old_value': None,
                'new_value': 'a',
                'field_label': 'Char',
                'field_name': 'char'
            }
        })

        model.char = 'AAA'
        model.save()

        self.assertEqual(AuditTrail.objects.all().count(), 3)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': 'a',
                'new_value': 'AAA',
                'field_label': 'Char'
            }
        })

        trails = audit_trail.get_for_object(model)
        self.assertEqual(trails.get_changes(), {
            'char2': {
                'old_value': None,
                'new_value': 'b',
                'field_label': 'Char2',
                'field_name': 'char2'
            },
            'char': {
                'old_value': None,
                'new_value': 'AAA',
                'field_label': 'Char',
                'field_name': 'char'
            }
        })

    def test_queryset_changes_reset_if_same_value(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.CREATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': None,
                'new_value': 'a',
                'field_label': 'Char'
            }
        })

        model.char2 = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char2': {
                'old_value': None,
                'new_value': 'b',
                'field_label': 'Char2'
            }
        })

        model.char2 = None
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 3)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char2': {
                'old_value': 'b',
                'new_value': None,
                'field_label': 'Char2'
            }
        })

        trails = audit_trail.get_for_object(model)

        self.assertEqual(len(trails.get_changes().keys()), 1)
        self.assertEqual(trails.get_changes(), {
            'char': {
                'old_value': None,
                'new_value': 'a',
                'field_label': 'Char',
                'field_name': 'char',
            }
        })

    def test_queryset_get_related_changes(self):
        """
        1. Create post
        2. Create comment 1
        3. Create comment 2

        --- Testing changes
        4. Delete comment 1
        5. Change comment 3
        6. Create comment 3
        """
        author = User.objects.create()
        post = Post.objects.create(author=author)
        comment1 = Comment.objects.create(post=post, text='comment 1 text')
        comment2 = Comment.objects.create(post=post, text='comment 2 text')

        time_from = datetime.datetime.now()

        comment1.delete()
        comment2.text = 'comment 2 text change'
        comment2.save()
        comment3 = Comment.objects.create(post=post, text='comment 3 text')

        # Do not display created and deleted object during period
        comment4 = Comment.objects.create(post=post, text='comment 3 text')
        comment4.delete()

        trails = audit_trail.get_for_object(post).filter(action_time__gt=time_from).order_by()
        related_objects_changes = trails.get_related_changes()
        self.assertEqual(len(related_objects_changes), 3)

        comment1_changes = related_objects_changes[0]
        self.assertEqual(comment1_changes['representation'], 'Comment 1')
        self.assertEqual(comment1_changes['action'], 'Deleted')
        self.assertEqual(comment1_changes['model'], 'test_app.comment')
        self.assertEqual(comment1_changes['changes']['text'], {
            'field_label': u'Text',
            'new_value': None,
            'old_value': u'comment 1 text',
            'field_name': 'text'
        })

        comment2_changes = related_objects_changes[1]
        self.assertEqual(comment2_changes['representation'], 'Comment 2')
        self.assertEqual(comment2_changes['action'], 'Updated')
        self.assertEqual(comment1_changes['model'], 'test_app.comment')
        self.assertEqual(comment2_changes['changes']['text'], {
            'field_label': u'Text',
            'new_value': u'comment 2 text change',
            'old_value': u'comment 2 text',
            'field_name': 'text',
        })

        comment3_changes = related_objects_changes[2]
        self.assertEqual(comment3_changes['representation'], 'Comment 3')
        self.assertEqual(comment3_changes['action'], 'Created')
        self.assertEqual(comment1_changes['model'], 'test_app.comment')
        self.assertEqual(comment3_changes['changes']['text'], {
            'field_label': u'Text',
            'new_value': u'comment 3 text',
            'old_value': None,
            'field_name': 'text'
        })

    def test_related_object_change(self):
        dog = Animal.objects.create(name='Dog')
        snake = Animal.objects.create(name='Snake')

        man = Person.objects.create()
        man.pet = dog
        man.save()

        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'pet': {
                'old_value': None,
                'new_value': unicode(dog.id),
                # 'new_value_string': u'[#%d] Dog' % dog.id,
                'field_label': u'Pet'
            }
        })

        man.pet = snake
        man.save()

        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'pet': {
                'old_value': unicode(dog.id),
                # 'old_value_string': u'[#%d] Dog' % dog.id,
                'new_value': unicode(snake.id),
                # 'new_value': u'[#%d] Snake' % snake.id,
                'field_label': u'Pet'
            }
        })

        man.pet = None
        man.save()

        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'pet': {
                'old_value': unicode(snake.id),
                # 'old_value': u'[#%d] Snake' % snake.id,
                'new_value': None,
                'field_label': u'Pet'
            }
        })

    def test_values_with_choices(self):
        person = SomePerson.objects.create()
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.CREATED)
        self.assertEqual(trail.get_changes(), {
            'season': {
                'old_value': None,
                'new_value': '0',
                # 'new_value': u'[#0] ' + person.get_season_display(),
                'field_label': u'Season'
            }
        })