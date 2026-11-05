"""Views for the Online Course App.

Includes the two exam views required by the Course 9 final project:
  - submit(request, course_id)
  - show_exam_result(request, course_id, submission_id)
"""
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Course, Enrollment, Lesson, Question, Submission


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-pub_date')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = Enrollment.objects.filter(
                    user=user, course=course).exists()
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    pk_url_kwarg = 'course_id'
    template_name = 'onlinecourse/course_details_bootstrap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson_list'] = Lesson.objects.filter(
            course=self.object).order_by('order')
        context['question_list'] = Question.objects.filter(
            course=self.object)
        return context


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    is_enrolled = Enrollment.objects.filter(user=user, course=course).exists()
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details',
                                        args=(course.id,)))


def submit(request, course_id):
    """Create a Submission from the exam form and redirect to the result."""
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    choices = extract_answers(request)
    submission.choices.set(choices)
    submission.save()
    return HttpResponseRedirect(reverse(
        viewname='onlinecourse:show_exam_result',
        args=(course.id, submission.id)))


def extract_answers(request):
    """Collect the Choice objects the learner ticked.

    The exam form in course_details_bootstrap.html names each checkbox
    ``choice_<choice_id>``, so a ticked box appears in request.POST.
    """
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice_'):
            choice_id = int(key.split('_')[1])
            submitted_answers.append(get_object_or_404(Choice, pk=choice_id))
    return submitted_answers


def show_exam_result(request, course_id, submission_id):
    """Grade a submission and render the exam result page."""
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    questions = Question.objects.filter(course=course)
    total_grade = sum(q.grade for q in questions)
    selected_ids = [c.id for c in submission.choices.all()]
    grade = sum(q.is_get_score(selected_ids) for q in questions)
    context = {
        'course': course,
        'grade': grade,
        'total_grade': total_grade,
        'passed': total_grade > 0 and grade >= 0.7 * total_grade,
        'submission': submission,
        'questions': questions,
        'selected_ids': selected_ids,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user = User.objects.create_user(username=username, first_name=first_name,
                                        last_name=last_name, password=password)
        login(request, user)
        return redirect("onlinecourse:course_list")
