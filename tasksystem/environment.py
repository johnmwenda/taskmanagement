# ENVIRONMENT = 'local'
ENVIRONMENT = 'development'
# ENVIRONMENT = 'production'

SETTINGS_MODULE = 'tasksystem.settings.local'

if ENVIRONMENT == 'local':
    SETTINGS_MODULE = 'tasksystem.settings.local'
if ENVIRONMENT == 'development':
    SETTINGS_MODULE = 'tasksystem.settings.development'
if ENVIRONMENT == 'production':
    SETTINGS_MODULE = 'tasksystem.settings.production'
