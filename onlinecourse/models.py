"""Models for the IBM Course 9 final project: Online Course App.

Models (8): Instructor, Learner, Course, Lesson, Enrollment,
Question, Choice, Submission.
Admin registers 7 of these (see admin.py); Enrollment is the
through-model for Course.users and is managed via the app, not admin.
"""
from django.conf import settings
from django.db import models
from django.utils.timezone import now


class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    occupation = models.CharField(
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT,
    )
    social_link = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return self.user.username + "," + self.occupation


class Course(models.Model):
    name = models.CharField(max_length=100, default='online course')
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    description = models.CharField(max_length=1000, null=True)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + "Description: " + str(self.description)


class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    MODE_CHOICES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=MODE_CHOICES, default=AUDIT)
    rating = models.FloatField(default=5.0)

    def __str__(self):
        return self.user.username + " enrolled in " + self.course.name


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question_text = models.TextField()
    grade = models.FloatField(default=1.0)

    def is_get_score(self, selected_ids):
        """Return the grade for this question, or 0 if any wrong choice
        was selected or a correct choice was missed.

        Only this question's own choices are considered: selected_ids
        holds the whole submission's choices, so intersect first.
        """
        all_answers = self.choice_set.all()
        question_choice_ids = {c.id for c in all_answers}
        selected_for_this = set(selected_ids) & question_choice_ids
        correct_ids = {c.id for c in all_answers if c.is_correct}
        if selected_for_this == correct_ids:
            return self.grade
        return 0

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return f"Submission {self.id} by {self.enrollment.user.username}"
