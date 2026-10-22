from vercel.proxy import ContinueResponse, Proxy, Request, Response


SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; base-uri 'self'; object-src 'none'; "
        "frame-ancestors 'none'; form-action 'self'; script-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com; style-src-attr 'none'; "
        "style-src-elem 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: blob: https://*.supabase.co; connect-src 'self'"
    ),
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


def add_security_headers(request: Request) -> Response:
    return ContinueResponse(headers=SECURITY_HEADERS)


proxy = Proxy(fallback=add_security_headers)
