class MailerFactory:
    def __init__(self, config):
        self.config = config

    def create(self):
        return SmtpMailer(self.config)
