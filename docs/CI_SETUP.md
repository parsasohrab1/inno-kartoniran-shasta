# CI/CD Pipeline

فایل کانفیگ CI در این مسیر (`docs/ci.yml`) قرار دارد زیرا توکن فعلی یک **Fine-grained PAT** است که مجوز **"Workflows"** repository permission را ندارد. GitHub هر تغییری در مسیر `.github/workflows/` را با HTTP **403** رد می‌کند — این محدودیت در سطح سرور اعمال می‌شود و نه‌تنها روی push معمولی، بلکه روی Contents API و حتی Git Database API (blobs/trees/commits) نیز تأیید شده است.

The CI config lives here as `docs/ci.yml` because the current deploy token is a **fine-grained PAT** without the **"Workflows"** repository permission. GitHub rejects any change under `.github/workflows/` with HTTP **403** — verified server-side across `git push`, the Contents API, and the low-level Git Database API (blobs/trees/commits).

## نحوه فعال‌سازی CI / Enabling CI

### گزینه ۱ (توصیه‌شده) — اجرای اسکریپت با PAT جدید / Option 1 (recommended) — run the helper script

1. یک **fine-grained PAT** جدید با این مجوزها بسازید:
   - Repository access → `Only select repositories` → `inno-kartoniran-shasta`
   - Repository permissions → `Workflows: Read and write` (و `Contents: Read and write` که به‌صورت پیش‌فرض با Workflows می‌آید).
   - یا یک **classic PAT** با scope‌های `repo` + `workflow`.
2. اسکریپت را اجرا کنید (فایل `docs/ci.yml` را می‌خواند، یک کامیت با مسیر `.github/workflows/ci.yml` می‌سازد و refs/heads/main را به‌روز می‌کند):

   ```bash
   PAT_WITH_WORKFLOW=<your_new_token> bash scripts/enable_ci.sh
   ```

   خروجی موفق: پیام `SUCCESS: .github/workflows/ci.yml added` و لینک کامیت.
   سپس workflow در https://github.com/parsasohrab1/inno-kartoniran-shasta/actions فعال می‌شود.

### گزینه ۲ — نصب دستی از وب GitHub / Option 2 — manual install via GitHub web

1. در ریپو GitHub دکمه **Add file → Create new file** را بزنید.
2. نام فایل را `.github/workflows/ci.yml` وارد کنید.
3. محتوای `docs/ci.yml` را کپی-پیست کنید و **Commit changes**.
4. این روش نیازی به PAT ندارد (احراز هویت وب کافی است).

### گزینه ۳ — push معمولی با PAT دارای مجوز / Option 3 — normal push with a permissioned PAT

```bash
git remote set-url origin https://x-access-token:<NEW_PAT>@github.com/parsasohrab1/inno-kartoniran-shasta.git
mkdir -p .github/workflows && cp docs/ci.yml .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "ci: enable GitHub Actions workflow"
git push origin main
```

> توجه: `.github/workflows/ci.yml` در `.gitignore` قرار دارد تا push با توکن فعلی رد نشود. اگر از گزینه ۳ استفاده می‌کنید، ابتدا آن خط را از `.gitignore` حذف کنید یا با `git add -f` آن را اضافه کنید.

## آنچه CI انجام می‌دهد / What the CI does

- نصب وابستگی‌ها از `requirements.txt` (Python 3.12).
- بررسی نحوی (`py_compile`) همه ماژول‌های `src/`.
- اجرای 24 تست `pytest` در `tests/`.
- بررسی وجود فایل‌های داده (`data/real`, `data/synthetic`).
- اجرای pipeline کامل: آموزش مدل‌ها + بهینه‌ساز دیگ‌بخار + برنامه‌ریز تولید.
- بررسی وجود خروجی‌ها (`models/`, `data/outputs/`, `ai_dashboard.html`).
- آپلود artifact شامل `models/`, `data/outputs/`, `ai_dashboard.html` (14 روز نگه‌داری).
- چاپ خلاصه شاخص‌ها (R²، صرفه‌جویی گاز، کاهش CO₂، راه‌اندازی سرد).

این pipeline دقیقاً همان مراحلی است که برای رسیدن به **TRL 5** اجرا شده است.
