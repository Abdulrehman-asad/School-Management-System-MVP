"""
Importing every model here ensures SQLAlchemy's mapper registry has all
classes available when relationships are resolved by string name
(e.g. relationship("Teacher")), regardless of which module is imported first.
"""

from app.models.user import Role, User          # noqa: F401
from app.models.academic import SchoolClass, Section, Subject   # noqa: F401
from app.models.teacher import Teacher, TeacherSubjectAssignment, TeacherStatus  # noqa: F401
from app.models.student import ParentGuardian, Student, GenderEnum, StudentStatus  # noqa: F401
from app.models.attendance import Attendance, AttendanceStatus  # noqa: F401
from app.models.homework import Homework, HomeworkSubmission, SubmissionStatus  # noqa: F401
from app.models.timetable import TimetableEntry, DayOfWeek  # noqa: F401
from app.models.exam import Exam, ExamSubjectSchedule, Result  # noqa: F401
from app.models.fee import FeeStructure, FeeChallan, FeeFrequency, ChallanStatus  # noqa: F401
from app.models.notice import Notice, NoticeAudience  # noqa: F401
from app.models.notification import Notification, NotificationType  # noqa: F401
