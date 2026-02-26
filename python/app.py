from flask import Flask, jsonify, render_template
import json
import os
from functools import reduce
from datetime import datetime

app = Flask(__name__)

# ──────────────────────────────────────────────
# OOP: Student Class
# ──────────────────────────────────────────────
class Student:
    def __init__(self, name, student_id, courses, grades,
                 eligible_courses="-", graduate="No"):
        self.name              = name
        self.student_id        = student_id
        self.courses           = courses          # list of course codes
        self.grades            = grades           # list of floats
        # EligibleCourses is sourced from Prolog (bridge output),
        # stored as a raw string e.g. "SWC3524" or "-"
        self._eligible_courses = eligible_courses
        self.graduate          = graduate

    # ── Computed properties ──────────────────

    @property
    def avg_grade(self):
        """Average grade using reduce (functional style)."""
        if not self.grades:
            return 0.0
        total = reduce(lambda acc, g: acc + g, self.grades)
        return round(total / len(self.grades), 2)

    def predict_performance(self):
        """
        Predict performance tier based on average grade.
        Aligns with Haskell output thresholds.
        """
        avg = self.avg_grade
        if avg >= 80:
            return "Excellent"
        elif avg >= 70:
            return "Good"
        elif avg >= 55:
            return "Average"
        else:
            return "Poor"

    def has_distinction(self):
        """
        Distinction if average grade > 80.
        Matches Haskell: Distinction Students (> 80) -> Aisyah (89.5), Anis (83.25).
        Balqis (79.0) does NOT qualify.
        """
        return self.avg_grade > 80

    def is_top_student(self):
        """
        Top student if average grade >= 89.
        Matches Haskell: only Aisyah (89.5) qualifies.
        """
        return self.avg_grade >= 89

    def get_eligible_courses(self):
        """
        Returns eligible course string as determined by Prolog bridge.
        Prolog facts: eligible(am123, swc3524) and recommend(am789, swc3524).
        Functional: uses filter to remove any blank entries.
        """
        parts = list(filter(
            lambda c: c.strip() not in ("", "-"),
            self._eligible_courses.split(";")
        ))
        return ";".join(parts) if parts else "-"

    def to_dict(self):
        """
        Serialize student to a flat dict the frontend can consume.
        Arrays -> semicolon-separated strings for the HTML table renderer.
        """
        return {
            "Name":            self.name,
            "ID":              self.student_id,
            "Code":            ";".join(self.courses),
            "Grades":          ";".join(str(g) for g in self.grades),
            "AvgGrade":        self.avg_grade,
            "Prediction":      self.predict_performance(),
            "Distinction":     "Yes" if self.has_distinction() else "No",
            "TopStudent":      "Yes" if self.is_top_student() else "No",
            "EligibleCourses": self.get_eligible_courses(),
            "Graduate":        self.graduate,
        }


# ──────────────────────────────────────────────
# Helper: load raw JSON -> list[Student]
# ──────────────────────────────────────────────
def load_students():
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '..', 'data', 'students.json')

    with open(file_path, 'r') as f:
        raw = json.load(f)

    # Functional: map each raw dict -> Student object
    return list(map(
        lambda d: Student(
            name             = d["Name"],
            student_id       = d["ID"],
            courses          = d["Code"],                       # list in JSON
            grades           = d["Grades"],                    # list in JSON
            eligible_courses = d.get("EligibleCourses", "-"),  # from Prolog bridge
            graduate         = d.get("Graduate", "No"),
        ),
        raw
    ))


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html', year=datetime.now().year)


@app.route('/api/students')
def get_students():
    students = load_students()

    # Functional: map each Student -> serialisable dict
    result = list(map(lambda s: s.to_dict(), students))
    return jsonify(result)


# Optional summary endpoint (bonus)
@app.route('/api/summary')
def get_summary():
    students = load_students()

    avgs        = list(map(lambda s: s.avg_grade, students))
    class_avg   = round(reduce(lambda a, b: a + b, avgs) / len(avgs), 2) if avgs else 0
    excellent   = list(filter(lambda s: s.predict_performance() == "Excellent", students))
    top         = list(filter(lambda s: s.is_top_student(), students))
    distinction = list(filter(lambda s: s.has_distinction(), students))

    return jsonify({
        "totalStudents":    len(students),
        "classAvgGrade":    class_avg,
        "excellentCount":   len(excellent),
        "topStudentCount":  len(top),
        "distinctionCount": len(distinction),
    })


if __name__ == '__main__':
    app.run(debug=True)