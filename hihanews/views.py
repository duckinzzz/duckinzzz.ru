from pathlib import Path

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.http import FileResponse, Http404
from django.shortcuts import render


NEWS_TEMPLATE_ROOT = Path(settings.BASE_DIR) / 'hihanews' / 'templates' / 'hihanews' / 'news'
ALLOWED_ASSET_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg', '.avif'}


def news_index(request):
    news_items = sorted(
        [
            news_dir.name
            for news_dir in NEWS_TEMPLATE_ROOT.iterdir()
            if news_dir.is_dir() and (news_dir / 'index.html').is_file()
        ],
        reverse=True,
    )
    return render(request, 'hihanews/news/index.html', {'news_items': news_items})


def news_detail(request, news_slug):
    template_name = f'hihanews/news/{news_slug}/index.html'
    try:
        return render(request, template_name, {'news_slug': news_slug})
    except TemplateDoesNotExist as exc:
        raise Http404('News not found') from exc


def news_asset(request, news_slug, asset_path):
    news_dir = NEWS_TEMPLATE_ROOT / news_slug
    asset_file = (news_dir / asset_path).resolve()

    if not asset_file.is_file():
        raise Http404('Asset not found')

    if asset_file.suffix.lower() not in ALLOWED_ASSET_EXTENSIONS:
        raise Http404('Unsupported asset type')

    try:
        asset_file.relative_to(news_dir.resolve())
    except ValueError as exc:
        raise Http404('Invalid asset path') from exc

    return FileResponse(asset_file.open('rb'))
