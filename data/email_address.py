from abc import ABC, abstractmethod
import re


EMAIL_PATTERN = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
EDU_TLD = '.edu'


class EmailAddress(ABC):
    @abstractmethod
    def __init__(self, email: str):
        # Subclasses provide concrete validation rules.
        print("Can't init this class!")

    def __str__(self):
        return self.email


class StandardEmailAddress(EmailAddress):
    def __init__(self, email: str):
        if not isinstance(email, str):
            raise TypeError(f'Bad type for email: {type(email)}')

        normalized = email.strip().lower()
        if not normalized:
            raise ValueError('Email cannot be empty')
        if not EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError(f'Invalid email format for {email=}')

        self.email = normalized


class EduEmailAddress(StandardEmailAddress):
    def __init__(self, email: str):
        super().__init__(email)
        if not self.email.endswith(EDU_TLD):
            raise ValueError(f'Email must end with {EDU_TLD}')
