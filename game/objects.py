from dataclasses import dataclass
from typing import Optional


@dataclass
class AnswerResult:
    chan_image_id: int = None
    is_correct: bool = False
    given_answer: str = ''
    correct_answer: Optional[str] = None
    character_image_url: Optional[str] = None


@dataclass
class ChanImageResult:
    chan_image_id: Optional[int] = None
    chan_image_url: Optional[str] = None
    letters: Optional[list] = None
    words_lengths: Optional[list] = None
    message: str = ''


@dataclass
class WordsLettersResult:
    words_lengths: Optional[list] = None
    letters: Optional[list] = None


@dataclass
class UserAttemptLog:
    id: int = None
    image_url: str = None
    status: str = None
    answer: str = None
    date: str = None
