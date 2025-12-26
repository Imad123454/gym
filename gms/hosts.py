from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(r"", "gms.urls", name="fitness"),  # 👈 MUST match DEFAULT_HOST
)
