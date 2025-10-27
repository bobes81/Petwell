from django.http import HttpResponse

def robots_txt(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /admin/\nAllow: /\n\nSitemap: https://petwell-app-ivo-59ea39e413cf.herokuapp.com/sitemap.xml",
        content_type="text/plain"
    )

def sitemap_xml(request):
    return HttpResponse(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url>\n'
        '    <loc>https://petwell-app-ivo-59ea39e413cf.herokuapp.com/</loc>\n'
        '    <changefreq>daily</changefreq>\n'
        '    <priority>1.0</priority>\n'
        '  </url>\n'
        '  <url>\n'
        '    <loc>https://petwell-app-ivo-59ea39e413cf.herokuapp.com/products/</loc>\n'
        '    <changefreq>weekly</changefreq>\n'
        '    <priority>0.8</priority>\n'
        '  </url>\n'
        '</urlset>',
        content_type="application/xml"
    )
