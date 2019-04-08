__all__ = [
    "StudentResource",
    "AdvisorResource",
    "CollegeResource",
    "MajorResource",
    "QueueResource",
    "QueuerResource",
    "FaqResource",
]

from distutils.util import strtobool

import falcon

from sa.models import Student, Advisor, College, Major, Faq, Queuer
from sa.utils import required_arguments


class StudentResource:
    def on_get(self, req, resp, student_id: int = None):
        students = []
        query = self.db.query(Student)

        if student_id:
            students.append(query.filter(Student.id == student_id).one())
        else:
            if "email" in req.data:
                query = query.filter(Student.email == req.data["email"])

            students.extend(query.all())

        resp.body = {"students": [student.as_dict() for student in students]}

    @falcon.before(
        required_arguments,
        ("email", "student_identifier", "is_undergraduate", "major_id"),
    )
    def on_post(self, req, resp):
        student = Student()

        student.email = req.data["email"]
        student.student_identifier = req.data["student_identifier"]
        student.is_undergraduate = req.data["is_undergraduate"]
        student.major_id = req.data["major_id"]

        self.db.Student.save(student)
        self.db.commit()

        resp.status = falcon.HTTP_201
        resp.body = {"student_id": student.id}


class AdvisorResource:
    def on_get(self, req, resp, advisor_id: int = None):
        advisors = []
        query = self.db.query(Advisor)

        if advisor_id:
            advisors.append(query.filter(Advisor.id == advisor_id).one())
        else:
            advisors.extend(query.all())

        resp.body = {"advisors": [advisor.as_dict() for advisor in advisors]}


class CollegeResource:
    def on_get(self, req, resp, college_id: int = None):
        colleges = []
        query = self.db.query(College)

        if college_id:
            colleges.append(query.filter(College.id == college_id).one())
        else:
            colleges.extend(query.all())

        resp.body = {"colleges": [college.as_dict() for college in colleges]}


class MajorResource:
    def on_get(self, req, resp, college_id: int, major_id: int = None):
        majors = []
        query = self.db.query(Major).filter(Major.college_id == college_id)

        if major_id:
            majors.append(query.filter(Major.id == major_id).one())
        else:
            majors.extend(query.all())

        resp.body = {"majors": [major.as_dict() for major in majors]}


class FaqResource:
    def on_get(self, req, resp, faq_id: int = None):
        faqs = []
        query = self.db.query(Faq)

        if faq_id:
            faqs.append(query.filter(Faq.id == faq_id).one())
        else:
            faqs.extend(query.all())

        resp.body = {"faqs": [faq.as_dict() for faq in faqs]}


class QueueResource:
    def on_get(self, req, resp):
        query = self.db.query(Queuer)

        if "major_id" in req.data:
            query = query.filter(Queuer.major_id == int(req.data["major_id"]))

        if "is_undergraduate" in req.data:
            query = query.filter(
                Queuer.is_undergraduate == strtobool(req.data["is_undergraduate"])
            )

        resp.body = {
            "queue": [
                l.as_dict()
                for l in sorted(query.all(), key=lambda lg: int(lg.position))
            ]
        }


class QueuerResource:
    @falcon.before(required_arguments, ("student_id"))
    def on_post(self, req, resp):
        """ Enqueue a Student for a specific major/undergrad queue. """
        student = (
            self.db.query(Student).filter(Student.id == req.data["student_id"]).one()
        )

        if "name" in req.data:
            student.name = req.data["name"]
            self.db.Student.save(student)

        tail_queuer = (
            self.db.query(Queuer)
            .filter(Queuer.major_id == student.major_id)
            .filter(Queuer.is_undergraduate == student.is_undergraduate)
            .order_by(Queuer.position.desc())
            .first()
        )

        queuer = Queuer(
            student_id=student.id,
            major_id=student.major_id,
            is_undergraduate=student.is_undergraduate,
            position=1 if not tail_queuer else tail_queuer.position + 1,
        )

        self.db.Queuer.save(queuer)
        self.db.commit()

        resp.body = {"queuer": queuer.as_dict()}
        resp.status = falcon.HTTP_201

    @falcon.before(required_arguments, ("student_id"))
    def on_delete(self, req, resp, queuer_id: int = None):
        """ Dequeue a Student for a specific major/undergrad queue. """
        queuer = (
            self.db.query(Queuer)
            .filter(Queuer.student_id == req.data["student_id"])
            .one()
        )

        remaining_queuers = (
            self.db.query(Queuer)
            .filter(Queuer.major_id == queuer.major_id)
            .filter(Queuer.is_undergraduate == queuer.is_undergraduate)
            .filter(Queuer.position > queuer.position)
            .all()
        )

        for lg in remaining_queuers:
            lg.position -= 1
            self.db.Queuer.save(lg)

        self.db.commit()

        resp.status = falcon.HTTP_202
