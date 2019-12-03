import os


class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = ",\x85\x1f\t\r\xd7'\xda\xd2\xa23\x10\xddW\xe4\x141\xb78Mu\x16\rP%\xe6m\xf4xoi\x93"
    ALLOWED_IMG_EXT = {'png', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG'}
    FCM_API_KEY = 'AAAADW0VoeA:APA91bFli2ybkzpMDc0WnbyCpfMyppWdXznkTRpTGkDAKaZ8W3Oj6Znv6BIwtmuDmYXkU9gGYlQ' \
                  '0mwEBOuxpzeX24nABHA6PkFODW3d2NiuQZIUndqBEC2xRr1b4lMTAInUSCFotdyCC'


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ['OTE_DATABASE_URL']


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:pwd12345@localhost/do_it_online_test_db'
    DEBUG = True


class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ['OTE_DATABASE_URL']


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}
