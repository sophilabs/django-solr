
#http://passingcuriosity.com/2010/default-settings-for-django-applications/

def inject_defaults():
    import default_settings
    import sys
    
    _app_settings = sys.modules['djangosolr.conf.default_settings']
    _def_settings = sys.modules['django.conf.global_settings']
    _settings = sys.modules['django.conf'].settings
    for _k in dir(_app_settings):
        if _k.isupper():
            # Add the value to the default settings module
            setattr(_def_settings, _k, getattr(_app_settings, _k))
    
            # Add the value to the settings, if not already present
            if not hasattr(_settings, _k):
                setattr(_settings, _k, getattr(_app_settings, _k))