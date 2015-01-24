import datetime
from django.test import TestCase
import audit_trail
from audit_trail.models import AuditTrail
from .models import TestModelTrackAllFields, TestModelTrackOneField, TestModelWithFieldLabels, \
    Post, Comment, User, AA, AB, BB, ShortcutTestModel, Post1, Comment1


class TestAuditTrail(TestCase):
    def test_create_audit_trail_on_creation(self):
        model = TestModelTrackAllFields.objects.create(char='a')
        self.assertEqual(AuditTrail.objects.all().count(), 1)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.CREATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': '',
                'new_value': 'a',
                'field_label': 'char'
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
                'new_value': '',
                'field_label': 'char'
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
                'field_label': 'char'
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
                'field_label': 'char'
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
                'field_label': 'char2'
            }
        })

        trail = AuditTrail.objects.all()[1]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char': {
                'old_value': 'a',
                'new_value': 'b',
                'field_label': 'char'
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
                'field_label': 'char'
            },
            'char2': {
                'old_value': 'y',
                'new_value': 'z',
                'field_label': 'char2'
            }
        })

    def test_field_labels(self):
        TestModelWithFieldLabels.objects.create(char='a', char2='x')

        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.get_changes()['char']['field_label'], TestModelWithFieldLabels.FIELD_LABELS['char'])
        self.assertEqual(trail.get_changes()['char2']['field_label'], TestModelWithFieldLabels.FIELD_LABELS['char2'])

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
                'old_value': '',
                'new_value': 'a',
                'field_label': 'name'
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
                'old_value': '',
                'new_value': 'a',
                'field_label': 'char'
            }
        })

        model.char2 = 'b'
        model.save()
        self.assertEqual(AuditTrail.objects.all().count(), 2)
        trail = AuditTrail.objects.all()[0]
        self.assertEqual(trail.action, AuditTrail.ACTIONS.UPDATED)
        self.assertEqual(trail.get_changes(), {
            'char2': {
                'old_value': '',
                'new_value': 'b',
                'field_label': 'char2'
            }
        })

        trails = audit_trail.get_for_object(model)
        self.assertEqual(trails.get_changes(), {
            'char2': {
                'old_value': '',
                'new_value': 'b',
                'field_label': 'char2'
            },
            'char': {
                'old_value': '',
                'new_value': 'a',
                'field_label': 'char'
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
                'field_label': 'char'
            }
        })

        trails = audit_trail.get_for_object(model)
        self.assertEqual(trails.get_changes(), {
            'char2': {
                'old_value': '',
                'new_value': 'b',
                'field_label': 'char2'
            },
            'char': {
                'old_value': '',
                'new_value': 'AAA',
                'field_label': 'char'
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
        self.assertEqual(comment1_changes['changes']['text'], {
            'field_label': u'text',
            'new_value': u'',
            'old_value': u'comment 1 text'
        })

        comment2_changes = related_objects_changes[1]
        self.assertEqual(comment2_changes['representation'], 'Comment 2')
        self.assertEqual(comment2_changes['action'], 'Updated')
        self.assertEqual(comment2_changes['changes']['text'], {
            'field_label': u'text',
            'new_value': u'comment 2 text change',
            'old_value': u'comment 2 text'
        })

        comment3_changes = related_objects_changes[2]
        self.assertEqual(comment3_changes['representation'], 'Comment 3')
        self.assertEqual(comment3_changes['action'], 'Created')
        self.assertEqual(comment3_changes['changes']['text'], {
            'field_label': u'text',
            'new_value': u'comment 3 text',
            'old_value': u''
        })