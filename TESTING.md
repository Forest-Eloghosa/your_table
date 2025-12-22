# Bug Fixes & Improvements

This document summarizes the recent bugs found during development, the root cause for each, the fix applied, and verification steps ran locally. Use this as a quick checklist when testing the project.

## 1) Navbar overlap & toggler not working
- Symptom: Navbar overlapped page content and the mobile toggler didn't expand/close reliably.
- Cause: Inconsistent Bootstrap markup and missing JS bundle for the navbar toggler.
- Fix: Standardized the navbar markup in `templates/navbar.html`, included Bootstrap JS bundle via CDN in `templates/base.html` and ensured the navbar is fixed-top while adding top padding to the hero section.
- Files changed: `templates/base.html`, `templates/navbar.html`, `static/css/base.css` (small spacing utility).
- How to verify:
  - Start the server and view the site on desktop and mobile widths.
  - Confirm the navbar does not overlap content and the toggler expands/collapses.

## 2) Hero / text misalignment on small screens
- Symptom: Hero text was hidden under the fixed navbar on small screens.
- Cause: Fixed navbar height was not accounted for in the hero section top spacing.
- Fix: Added a `.section-padding-top` class and applied appropriate top padding where needed.
- Files changed: `static/css/base.css`, templates using hero sections.
- How to verify: Resize browser to mobile width and ensure hero text is visible and not overlapped.

## 3) Mood buttons stacking incorrectly
- Symptom: Buttons stacked or wrapped oddly at smaller widths.
- Cause: Mixed custom CSS and Bootstrap grid usage caused inconsistent layout rules.
- Fix: Standardized the button layout using a simple responsive CSS grid and adjusted media queries.
- Files changed: `static/css/base.css`, components/templates containing the buttons.

## 4) Quotes repeating / not updating (front-end JS)
- Symptom: Quote widget reused the same index and didn't cycle through quotes as expected.
- Cause: `Math.random()` produced repeated values and DOM state wasn't resetting between cycles.
- Fix: Implemented a Fisher–Yates shuffle on load and cycled through shuffled quotes so each quote appears once per cycle.
- Files changed: `static/js/main.js` (or relevant JS file).

## 5) Secret key & environment handling
- Symptom: SECRET_KEY was hard-coded in `yourtable/settings.py` and committed in repo.
- Cause: Default startproject behavior; sensitive value committed.
- Fix: Settings now load `DJANGO_SECRET_KEY` (or `SECRET_KEY`) from environment and optionally load `.env` when `python-dotenv` is available. Added `.env` to `.gitignore` and removed secrets from the index.
- Files changed: `yourtable/settings.py`, `.gitignore`.
- Commands to create local `.env` (do not commit):
  ```powershell
  echo DJANGO_SECRET_KEY=replace-with-a-secure-random-string > .env
  ```

## 6) `db.sqlite3` tracked in git
- Symptom: Local SQLite DB (`db.sqlite3`) was tracked in repo history.
- Fix: Added `db.sqlite3` to `.gitignore` and removed it from the index:
  ```powershell
  git rm --cached db.sqlite3
  git commit -m "Ignore db.sqlite3 and remove from index"
  ```

## Database configuration rationale

Simple explanation for assessors (why the code checks `DATABASE_URL` first):

- The settings check `os.environ.get('DATABASE_URL')` and, if present, use
  `dj_database_url` to parse that value into Django's `DATABASES` config. This
  is the standard pattern used on Heroku and many cloud providers where a full
  database connection string is provided through the `DATABASE_URL` env var.
- If `DATABASE_URL` isn't present (common during local development) or if the
  parsing package isn't available, the code falls back to a local SQLite
  database (`db.sqlite3`). This fallback ensures `manage.py` commands and
  tests work locally without extra setup.
- Order matters: checking `DATABASE_URL` first lets production use the
  recommended (managed) database automatically while still keeping the project
  simple to run locally.

For clarity, here is the exact code snippet used in `yourtable/settings.py`:

```python
if os.environ.get('DATABASE_URL'):
    try:
        import dj_database_url

        DATABASES = {
            'default': dj_database_url.parse(os.environ.get('DATABASE_URL'), conn_max_age=600)
        }
    except Exception:
        # dj_database_url not installed or parse failed — fallback to local SQLite.
        # Print a simple warning to stdout so devs see why the fallback happened.
        print('WARNING: dj_database_url not available or DATABASE_URL parse failed; falling back to SQLite')
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

This demonstrates the intended behavior:

1. If `DATABASE_URL` is set → parse and use it (Postgres in production).
2. Otherwise → use the local SQLite file for development and testing.

This approach is intentional and reviewer-friendly: a single configuration
works in typical development and deployment workflows without extra changes.


## 7) TemplateDoesNotExist: home.html
- Symptom: TemplateView couldn't find `home.html` (TemplateDoesNotExist).
- Cause: Project-level `templates/` directory wasn't configured in `TEMPLATES['DIRS']`.
- Fix: Added `BASE_DIR / 'templates'` to `TEMPLATES['DIRS']` in `yourtable/settings.py`.
- Files changed: `yourtable/settings.py`.

## 8) NoReverseMatch errors (login/logout/signup/booking_list)
- Symptom: Template reversing failed for names like `login`, `logout`, `signup`, `booking_list`.
- Cause: URL names were namespaced (e.g., `app_name = 'bookings'`) or using django-allauth names (`account_login`) and the templates used the wrong name.
- Fixes applied:
  - Updated navbar and templates to use the correct names:
    - `users:signup` for the signup view
    - `account_login` and `account_logout` for allauth auth views
    - `bookings:booking_list` for the bookings list link
  - Added django-allauth URLs (`path('accounts/', include('allauth.urls'))`) to `yourtable/urls.py`.
- Files changed: `templates/navbar.html`, `templates/reviews/review_list.html`, `templates/home.html`, `yourtable/urls.py`.

## 9) Allauth import error when running manage.py
- Symptom: `ModuleNotFoundError: No module named 'allauth'` during `manage.py` commands.
- Cause: `django-allauth` was referenced in `INSTALLED_APPS` but not installed in the virtualenv.
- Fix: Installed `django-allauth` into the venv and then re-ran migrations. Add to `requirements.txt` if needed.
- Commands to install:
  ```powershell
  pip install django-allauth
  pip freeze > requirements.txt
  ```

## 10) PowerShell copy command errors when copying templates
- Symptom: `Copy-Item` / `cp` command failed with `PositionalParameter` errors.
- Cause: PowerShell uses named parameters (e.g., `-Recurse`) and different quoting rules than Unix shells.
- Fix / best practice: Use PowerShell-safe commands. Example to copy only the allauth templates into project templates (adjust venv path as needed):
  ```powershell
  New-Item -ItemType Directory -Path .\templates -Force
  Copy-Item -Path ".\.venv\Lib\site-packages\allauth\templates\*" -Destination ".\templates" -Recurse -Force
  ```
- Safer alternative: create only the minimal templates you need (e.g., `templates/account/login.html`) rather than copying the entire package.

## 11) Reviews page OperationalError (no such table)
- Symptom: `OperationalError: no such table: reviews_review` when loading `/reviews/`.
- Cause: Migrations for the `reviews` app had not been created/applied.
- Fix: Created migrations and applied them; the `reviews_review` table was created.
- Commands run:
  ```powershell
  python manage.py makemigrations reviews
  python manage.py migrate
  python manage.py showmigrations reviews
  ```

## 12) Added signup and review features
- Summary: Added a simple `signup` view (using `UserCreationForm`), templates for signup/login/logout, and a `Review` model with `ListView` and `CreateView`.
- Files added/changed (high-level):
  - `users/views.py`, `users/urls.py`, `templates/registration/signup.html`
  - `templates/account/login.html`, `templates/registration/logged_out.html`
  - `reviews/models.py`, `reviews/views.py`, `reviews/urls.py`, `reviews/admin.py`
  - `templates/reviews/review_list.html`, `templates/reviews/review_form.html`

## Verification checklist (quick)
1. Ensure virtualenv is activated.
2. Install dependencies (if not already):
   ```powershell
   pip install -r requirements.txt
   # or at least: pip install django django-allauth python-dotenv
   ```
3. Ensure `.env` contains `DJANGO_SECRET_KEY` or set it in the environment.
4. Run migrations:
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Create a superuser if you need admin access:
   ```powershell
   python manage.py createsuperuser
   ```
6. Run the server and test critical flows:
   ```powershell
   python manage.py runserver
   # Visit: /, /accounts/login/, /users/signup/, /reviews/, /bookings/
   ```

## Notes and next improvements
- Add message display block to `templates/base.html` so `messages.success` and other feedback is visible immediately after signup/login.
- Consider auto-logging-in users after signup for better UX.
- Add unit tests (Django `TestCase`) for authentication and reviews create/list flows.
- If any sensitive values were pushed to a remote repo, rotate them and consider using BFG or `git filter-repo` to remove them from history.

---


## 12) Static files 404 & footer not showing
- Symptom: Browser DevTools shows 404 Not Found for `/static/css/base.css` and `/static/js/main.js`. The footer appears unstyled or seems missing because styles are not loaded.
- Cause: During development Django wasn't including the project-level `static/` directory in the staticfiles search paths (no `STATICFILES_DIRS` configured) and `STATIC_URL` may have been configured without a leading slash, causing the dev server to not resolve assets at the expected paths.
- Fix: Updated `yourtable/settings.py`:
  - Set `STATIC_URL = '/static/'` (leading slash)
  - Added `STATICFILES_DIRS = [ BASE_DIR / 'static' ]` so Django's staticfiles app will find files in the project-level `static/` folder when `DEBUG = True`.
- Files changed: `yourtable/settings.py`.
- How to verify:
  1. Confirm files exist in the repo:
     - `static/css/base.css`
     - `static/js/main.js`
  2. Restart the dev server and visit the site:
     ```powershell
     python manage.py runserver
     ```
  3. Open browser DevTools → Network and reload the page. Confirm `/static/css/base.css` and `/static/js/main.js` return HTTP 200.
  4. Confirm the footer now displays with styling from `base.css`.
  5. If assets still 404:
     - Ensure `DEBUG = True` in `settings.py` while testing locally.
     - Check template references use `{% load static %}` and `{% static 'css/base.css' %}` (currently correct in `templates/base.html`).
     - Confirm there are no typos in file paths or filenames.

- Notes for production:
  - In production you should run `python manage.py collectstatic` and serve the resulting files from your web server (e.g., via Nginx). Do not rely on `STATICFILES_DIRS`/Django static serving in production.

## 13) Footer layout, favicon detection, and social icons alignment
- Symptom: The footer text and social icons were invisible or stacked vertically. The browser showed a globe icon instead of your app favicon in some cases.
- Cause(s):
  - Invalid HTML: `<li>` elements were placed directly inside a `<p>` tag which is invalid. Browsers treated list items as block elements and stacked them vertically.
  - Missing CSS utility: the template used a `dark-bg` class but no corresponding CSS existed, causing white text on a white background so the footer appeared invisible.
  - Favicon detection: while PNG favicons existed, some browsers prefer or fallback to `favicon.ico` or a `shortcut icon` link. Without a proper fallback some browsers show a globe or default icon (and they also aggressively cache favicons).
  - Minor icon mismatch: Twitter icon used an uncommon class (`fa-x-twitter-square`) that some Font Awesome versions don't recognize; `fa-twitter-square` is more broadly supported.
- Fixes applied:
  - HTML: Replaced invalid inline `<li>` usage with a proper `<ul class="social-list">` placed in a centered container and using Bootstrap utility classes (`d-inline-flex`, `list-unstyled`) so items render inline.
  - CSS: Added `.dark-bg` to `static/css/base.css` (dark background + white text) and added `.social-list` / `.social-link` styles to align icons horizontally, add spacing, hover states, and sensible colors.
  - Favicon: Added a shortcut favicon fallback link in `templates/base.html`:
    ```html
    <link rel="shortcut icon" href="{% static 'favicon/favicon.ico' %}">
    ```
    This helps browsers that expect an `.ico` or a `shortcut icon` entry to detect your favicon.
  - Icons: Replaced the Twitter icon class with a supported Font Awesome class (`fa-twitter-square`) and ensured icon elements include `aria-hidden="true"`.
- Files changed: `templates/footer.html`, `templates/base.html`, `static/css/base.css`.
- How to verify:
  1. Confirm static assets load (see section 12). In particular check:
     - `/static/css/base.css` (should return 200)
     - `/static/favicon/favicon.ico` or the PNG variations (should return 200)
  2. Hard-refresh the page (Ctrl+F5) or open an Incognito window — favicons are heavily cached by browsers.
  3. Check the footer visually: copyright text centered, "Follow us:" line, and social icons in a single horizontal row.
  4. Inspect the UL in DevTools — it should have `display: inline-flex` (via Bootstrap class) and the `.social-link` rules applied.
  5. Hover an icon to confirm hover/focus styles (icon color changes and a small lift).

- Accessibility notes and small extras applied:
  - Icon `<i>` elements have `aria-hidden="true"` and links include `aria-label` so screen readers announce the social link names instead of icon glyphs.
  - The list is `list-unstyled` and uses semantic `<ul>` / `<li>` markup (better for screen readers than stray `<li>`s in paragraphs).



---

## Recent fixes (2025-11-07)

This section documents a short series of template and form errors discovered during development on Nov 7, 2025 and the quick fixes that were applied.

### A) TemplateSyntaxError: "Invalid block tag on line X: 'static', expected 'endif'"
- Symptom: Several pages (menu item detail, reviews list, user profile) raised a TemplateSyntaxError complaining that `{% static %}` was an invalid block tag and the parser expected `endif`.
- Cause: Templates were using the `{% static %}` tag without first loading the `static` template library in that template (missing `{% load static %}` at the top). If Django encounters an unknown tag inside a block it may report an unexpected tag like `static` and show `expected 'endif'` depending on surrounding tags.
- Fix applied:
  - Added `{% load static %}` to the top of the affected templates:
    - `menu/templates/menu/menu_item_detail.html`
    - `templates/reviews/review_list.html`
    - `templates/registration/profile.html`
- Verification steps:
  1. Restart the development server (if needed):
     ```powershell
     & ".\.venv\Scripts\python.exe" manage.py runserver
     ```
  2. Visit the pages that previously errored (e.g., `/menu/grilled-salmon/`, `/reviews/`, `/users/profile/`) and confirm the pages render without TemplateSyntaxError.
  3. Run `python manage.py check` to confirm no template syntax issues are reported.

### B) Booking creation POST error: AttributeError "'list' object has no attribute 'strip'"
- Symptom: Submitting the create booking form resulted in an AttributeError with traceback pointing to Django form field coercion (`to_python`/`strip`) because the view received a list where a string was expected.
- Cause: The booking model uses a single DateTimeField but the form/widget provided two inputs (date + time). If the form definition used only the model field with a SplitDateTimeWidget via `Meta.widgets`, Django can still coerce incorrectly depending on how the form fields are defined, leading the value to be a `list` (two-element list from POST) when the field expects a single string.
- Fix applied:
  - Replaced the `Meta.widgets` approach with an explicit `SplitDateTimeField` on the form so the form expects a two-input field correctly and parses them into a single datetime value.
  - File changed: `bookings/forms.py`
    - Added:
      ```python
      from django.forms.widgets import SplitDateTimeWidget

      class BookingForm(forms.ModelForm):
          date = forms.SplitDateTimeField(
              widget=SplitDateTimeWidget(
                  date_attrs={'type': 'date'}, time_attrs={'type': 'time'}
              )
          )

          class Meta:
              model = Booking
              fields = ['restaurant', 'date', 'guests', 'special_requests']
      ```
- Verification steps:
  1. Open the booking creation page (`/bookings/new/`) and confirm the form shows separate date and time inputs.
  2. Submit a booking; confirm the POST succeeds and no AttributeError appears.
  3. Confirm the booking record appears in `/bookings/` and in the admin if needed.

### C) Duplicate loop in `menu_list.html` producing logic errors / redundant processing
- Symptom: `menu/templates/menu/menu_list.html` included duplicated `{% for category in categories %}` loops (one nested inside another) which produced incorrect rendering and increased template complexity.
- Cause: Template duplication likely introduced during previous edits.
- Fix applied:
  - Simplified the template so there is a single `if categories` guard and a single `for category in categories` loop. Kept the `else` branch to show "No menu categories available." when empty.
  - File changed: `menu/templates/menu/menu_list.html`
- Verification steps:
  1. Visit `/menu/` to ensure categories and menu items display once and layout is correct.
  2. Confirm there are no template syntax errors and that images fall back to the placeholder when `item.image` is missing.

---






