# gms/hosts.py
from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'fitness', 'gms.urls', name='fitness'),
    host(r'pathan', 'gms.urls', name='pathan'),
)
