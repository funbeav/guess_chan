from dataclasses import dataclass
from typing import Optional


@dataclass
class CorrectAnswer:
    text: str = ''
    image_url: str = ''


@dataclass
class AnswerResult:
    is_correct: bool
    given_answer: str
    correct_answer: Optional[CorrectAnswer]
