import os

SERVICE_TITLE='AwesomeNet'
APPLICATION_PORT=os.environ.get('APPLICATION_PORT', '8000')
APPLICATION_SERVICES_ANNONCE=os.environ.get('APPLICATION_SERVICES_ANNONCE', '').split(',')
