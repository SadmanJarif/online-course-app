# Course 9 Final Project — Django Online Course App — SUMMARY

**Status: built and verified locally only. NOT submitted to Coursera/Mark.
NOT published to GitHub. No Coursera score exists or is claimed.**

Project: IBM Full Stack Software Developer, Course 9 final project
("Online Course App"). Mark reference from the task: learner/2582,
15 points, pass 70% (10.5/15). That pass mark is from the task brief —
it has not been verified against Mark, because nothing was submitted.

Built: 2026-11-06 (local time +06). Python 3.12.3, Django 4.2.30,
Pillow 10.2.0 (both in `requirements.txt`).

## File list

```
course9-online-course/
├── manage.py
├── requirements.txt              # Django==4.2.30, Pillow==10.2.0
├── .gitignore                    # .venv/, db.sqlite3, __pycache__
├── db.sqlite3                    # local dev DB with seeded demo data
│                                 # (gitignored; recreate with migrate+seed)
├── mysite/
│   ├── settings.py               # onlinecourse app installed; DEBUG=True (local only)
│   ├── urls.py                   # admin/ + onlinecourse.urls at root
│   ├── wsgi.py / asgi.py
├── onlinecourse/
│   ├── models.py                 # 8 models: Instructor, Learner, Course,
│   │                             # Lesson, Enrollment, Question, Choice,
│   │                             # Submission
│   ├── admin.py                  # imports & registers 7 classes:
│   │                             # Course, Lesson, Instructor, Learner,
│   │                             # Question, Choice, Submission
│   ├── views.py                  # CourseListView, CourseDetailView, enroll,
│   │                             # submit, extract_answers, show_exam_result,
│   │                             # registration_request
│   ├── urls.py                   # course list/detail, enroll,
│   │                             # <course_id>/submit/ -> submit,
│   │                             # course/<course_id>/submission/<submission_id>/result/
│   │                             #   -> show_exam_result, registration/
│   ├── tests.py                  # 5 tests (see "Tests" below)
│   ├── migrations/0001_initial.py
│   ├── templates/onlinecourse/
│   │   ├── base.html
│   │   ├── course_list_bootstrap.html
│   │   ├── course_details_bootstrap.html   # exam form: checkboxes
│   │   │                             # named choice_<choice_id>, POSTs to submit
│   │   ├── exam_result_bootstrap.html
│   │   └── user_registration_bootstrap.html
│   └── static/onlinecourse/      # Bootstrap 4.3.1 vendored locally
│       ├── css/bootstrap.min.css # (no CDN dependency, renders offline)
│       └── js/{bootstrap.min.js, jquery-3.3.1.slim.min.js, popper.min.js}
├── scripts/
│   ├── seed_demo.py              # idempotent demo data (see "Demo data")
│   └── screenshots.py            # Playwright capture of the 2 screenshots
└── screenshots/
    ├── 03-admin-site.png         # REAL headless-Chromium screenshot,
    │                             # Django admin home, logged in as admin
    └── 07-final.png              # REAL headless-Chromium screenshot of the
                                  # live local exam-result page (submission 1,
                                  # 2.0/2.0). NOT a mockup, NOT a Coursera
                                  # result — it is the local demo exam only.
```

## How to run (local)

```bash
cd ~/workspace/course9-online-course
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python scripts/seed_demo.py
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Then: course list http://127.0.0.1:8000/ · demo course
http://127.0.0.1:8000/1/ · admin http://127.0.0.1:8000/admin/

Demo data (`scripts/seed_demo.py`, idempotent): superuser
`admin` / `admin123` (LOCAL DEV ONLY — change before any real use);
learner `learner1` / `learner123`; course "Python for Data Science"
(id 1) with 1 lesson and 2 questions (grades 1.0 each, total 2.0).
The live exam flow was run as `admin` (enrolled via `/1/enroll/`,
submitted the two correct choices, result at
`/course/1/submission/1/result/`).

To re-capture screenshots (needs the server running + seeded data):

```bash
.venv/bin/pip install playwright
.venv/bin/playwright install chromium
.venv/bin/python scripts/screenshots.py
```

## Tests — command and result

```bash
.venv/bin/python manage.py check
# System check identified no issues (0 silenced).

.venv/bin/python manage.py test onlinecourse -v 2
# Ran 5 tests in ~15–44s — OK
#   test_course_list_renders ... ok
#   test_course_details_renders_exam_form ... ok
#   test_submit_all_correct_scores_full_marks ... ok  (asserts 2.0/2.0)
#   test_submit_one_wrong_scores_zero_for_that_question ... ok (1.0/2.0)
#   test_admin_registers_seven_models ... ok
```

Two bugs found and fixed during testing (both verified by the tests
above): (1) `CourseDetailView` needed `pk_url_kwarg = 'course_id'`
(the URL passes `course_id`, not `pk`); (2) `Question.is_get_score`
now intersects the submission's selected ids with *this question's*
own choices before comparing with its correct choices — without this,
a multi-question exam always scored 0.

## Live smoke test (runserver, curl) — verified 2026-11-06

| Check | Result |
|---|---|
| `GET /` | 200, contains "Python for Data Science" |
| `GET /1/` (anonymous) | 200 (exam form hidden until login, by design) |
| `GET /admin/login/` | 200, "Django administration" |
| Admin login `admin`/`admin123` | 302 → `/admin/`, then 200 "Site administration" |
| `GET /1/enroll/` (as admin) | 302 → `/1/` |
| `GET /1/` (authenticated) | 200, contains "Start Exam" and `choice_<id>` inputs |
| `POST /1/submit/` (choice_2 + choice_3, the correct answers) | 302 → `/course/1/submission/1/result/` |
| `GET /course/1/submission/1/result/` | 200, "score of 2.0/2.0", "Congratulations, Admin!" |

The 2.0/2.0 is the **local demo exam** (2 seeded questions, both
answered correctly). It is not a Coursera/Mark grade.

## What Mark needs next (not done — needs Jarif / a browser agent)

1. **Publish the code to GitHub.** Nothing has been pushed anywhere.
   Suggested: new repo (e.g. `online-course-app`), push everything in
   this folder *except* `.venv/` and `db.sqlite3` (see `.gitignore`).
   Do not push the local `admin`/`admin123` credentials anywhere public
   beyond this local folder — they are dev-only; change or remove the
   seeded superuser before publishing if the DB is ever included.
2. **Submit to Coursera/Mark** (learner/2582, 15 pts, pass 70%) from the
   browser, following the course's own submission instructions — this
   subagent cannot use a live browser and did not attempt it. Mark
   will need the GitHub repo URL and the two screenshots
   (`screenshots/03-admin-site.png`, `screenshots/07-final.png`).
3. **Verify the actual Mark rubric** at submission time. This build
   covers the items named in the task (models with Question/Choice/
   Submission, admin importing 7 classes, `course_details_bootstrap.html`,
   `submit` + `show_exam_result` in views and urls, the two screenshots)
   plus a working course list/enroll/registration flow, but the exact
   Mark checks (file paths, naming, screenshot numbering) were not
   available locally and have not been confirmed.
4. **Known limitation:** the app has no app-level login view — login
   currently goes through `/admin/login/`. Registration exists
   (`/registration/`), but a learner created there is not staff, so
   they cannot use the admin login page. If Mark expects a learner
   login page, add `django.contrib.auth.views.LoginView` + a
   `user_login_bootstrap.html` template before submitting.
