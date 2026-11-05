"""Tests for the Online Course App (local smoke tests, not Mark).

Covers: course list page, course details + exam form, submit flow,
show_exam_result grading (all-correct = full marks, one wrong = 0
for that question), and admin registration of the 7 model classes.
"""
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Choice, Course, Enrollment, Instructor, Lesson, Question, Submission


def make_course():
    instructor_user = User.objects.create_user('instructor1', password='x')
    instructor = Instructor.objects.create(user=instructor_user)
    course = Course.objects.create(
        name='Python for Data Science',
        description='Learn Python basics for data science.',
        pub_date='2026-01-01',
    )
    course.instructors.add(instructor)
    Lesson.objects.create(course=course, title='Introduction',
                          content='Welcome to the course.', order=0)
    q1 = Question.objects.create(
        course=course, question_text='What is 2 + 2?', grade=1.0)
    Choice.objects.create(question=q1, choice_text='3', is_correct=False)
    Choice.objects.create(question=q1, choice_text='4', is_correct=True)
    q2 = Question.objects.create(
        course=course, question_text='Which is a Python list?', grade=1.0)
    Choice.objects.create(question=q2, choice_text='[1, 2, 3]', is_correct=True)
    Choice.objects.create(question=q2, choice_text='{1: 2}', is_correct=False)
    return course


class CourseFlowTests(TestCase):
    def setUp(self):
        self.course = make_course()
        self.user = User.objects.create_user('learner1', password='learner123')
        Enrollment.objects.create(user=self.user, course=self.course, mode='honor')
        self.client = Client()
        self.client.login(username='learner1', password='learner123')

    def test_course_list_renders(self):
        resp = self.client.get(reverse('onlinecourse:course_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Python for Data Science')

    def test_course_details_renders_exam_form(self):
        resp = self.client.get(reverse(
            'onlinecourse:course_details', args=(self.course.id,)))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Start Exam')
        self.assertContains(resp, 'What is 2 + 2?')
        self.assertContains(resp, 'choice_')

    def test_submit_all_correct_scores_full_marks(self):
        correct = Choice.objects.filter(is_correct=True)
        data = {f'choice_{c.id}': str(c.id) for c in correct}
        resp = self.client.post(
            reverse('onlinecourse:submit', args=(self.course.id,)), data)
        self.assertEqual(resp.status_code, 302)
        submission = Submission.objects.get(enrollment__user=self.user)
        resp = self.client.get(reverse(
            'onlinecourse:show_exam_result',
            args=(self.course.id, submission.id)))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '2.0/2.0')
        self.assertContains(resp, 'Congratulations')

    def test_submit_one_wrong_scores_zero_for_that_question(self):
        q1_correct = Choice.objects.get(question__question_text='What is 2 + 2?',
                                        is_correct=True)
        q2_wrong = Choice.objects.get(question__question_text='Which is a Python list?',
                                      is_correct=False)
        data = {f'choice_{q1_correct.id}': str(q1_correct.id),
                f'choice_{q2_wrong.id}': str(q2_wrong.id)}
        self.client.post(reverse('onlinecourse:submit', args=(self.course.id,)), data)
        submission = Submission.objects.get(enrollment__user=self.user)
        resp = self.client.get(reverse(
            'onlinecourse:show_exam_result',
            args=(self.course.id, submission.id)))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '1.0/2.0')

    def test_admin_registers_seven_models(self):
        from django.contrib import admin
        registered = {m.__name__ for m in admin.site._registry}
        for name in ('Course', 'Lesson', 'Instructor', 'Learner',
                     'Question', 'Choice', 'Submission'):
            self.assertIn(name, registered)
