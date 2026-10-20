"""
EduMentor Application Domain Services.
"""

from edumentor.services.avatar_expression_manager import (
    AvatarExpressionManager,
    avatar_expression_manager,
)
from edumentor.services.teacher_message_engine import (
    TeacherMessageEngine,
    teacher_message_engine,
)

__all__ = [
    "AvatarExpressionManager",
    "avatar_expression_manager",
    "TeacherMessageEngine",
    "teacher_message_engine",
]

