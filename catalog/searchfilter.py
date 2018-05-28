# path/to/your/module.py
from django_python3_ldap.utils import format_search_filters

def custom_format_search_filters(ldap_fields):
    # Add in simple filters.
    ldap_fields["memberOf"] = "1.2.840.113556.1.4.1941:=CN=SpNotify,CN=Users,DC=twfp,DC=com"
    # Call the base format callable.
    search_filters = format_search_filters(ldap_fields)
    return search_filters