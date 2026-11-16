# CI/CD Pipeline

فایل کانفیگ CI در این مسیر قرار دارد زیرا توکن شخصی (PAT) استفاده‌شده برای push، `workflow` scope نداشت و GitHub از ثبت مستقیم `.github/workflows/ci.yml` جلوگیری می‌کند.

The CI config lives here as `ci.yml` instead of under `.github/workflows/` because the Personal Access Token used to push does **not** have the `workflow` scope, so GitHub refuses commits that touch `.github/workflows/`.

## نحوه فعال‌سازی CI / Enabling CI

### گزینه ۱ — نصب دستی فایل (سریع‌ترین) / Option 1 — Manual install (fastest)

1. در ریپو GitHub به مسیر `.github/workflows/` بروید (اگر نیست، بسازید).
2. فایل `docs/ci.yml` را با همان محتوا در آن مسیر با نام `ci.yml` ثبت کنید (می‌توانید از رابط وب GitHub این کار را بکنید).
3. push بعدی، workflow به‌صورت خودکار روی push/PR به `main` اجرا می‌شود.

### گزینه ۲ — صدور PAT با `workflow` scope / Option 2 — Issue a PAT with `workflow` scope

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic).
2. توکنی با حداقل scope‌های `repo` و `workflow` بسازید.
3. با آن push کنید:

   ```bash
   git remote set-url origin https://x-access-token:<NEW_PAT>@github.com/parsasohrab1/inno-kartoniran-shasta.git
   mkdir -p .github/workflows && cp docs/ci.yml .github/workflows/ci.yml
   git add .github/workflows/ci.yml
   git commit -m "ci: enable GitHub Actions workflow"
   git push origin main
   ```

## آنچه CI انجام می‌دهد / What the CI does

- نصب وابستگی‌ها از `requirements.txt`
- بررسی نحوی (py_compile) همه ماژول‌های `src/`
- اجرای 24 تست pytest در `tests/`
- بررسی وجود فایل‌های داده (`data/real`, `data/synthetic`)
- اجرای pipeline کامل: آموزش مدل‌ها + بهینه‌ساز دیگ‌بخار + برنامه‌ریز تولید
- بررسی وجود خروجی‌ها (مدل‌ها، گزارش‌ها، داشبورد)
- آپلود artifact شامل `models/`, `data/outputs/`, `ai_dashboard.html`
- چاپ خلاصه شاخص‌ها (R²، صرفه‌جویی گاز، کاهش CO₂، راه‌اندازی سرد)

این pipeline دقیقاً همان مراحلی است که برای رسیدن به **TRL 5** اجرا شده است.
