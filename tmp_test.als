open util/ordering[Grade] sig Person { teaches : set Course, enrolled : set Course, projects : set Project } sig Professor,Student in Person {} sig Course { projects : set Project, grades : Person -> Grade } sig Project {} sig Grade {}
}

// -----------------------------------------------------------------------------
// Positive Instances (expect 1): Scenarios that satisfy the requirement
// -----------------------------------------------------------------------------

// Positive Instance 1: No two students work on the same project in any course.
// The premise of the implication (that s1 and s2 are on the same project in a course)
// is false, thus the constraint is vacuously satisfied.
run {
  some disj s1, s2: Student {
    some c: Course {
      some p: Project {
        p in c.projects
        s1 in c.enrolled and s2 in c.enrolled
        p in s1.projects
        not (p in s2.projects) // s2 does not work on 'p'
        // Grades can differ by more than one unit, as the constraint doesn't apply
        c.grades[s1] = Grade.first
        c.grades[s2] = Grade.first.next.next
      }
    }
  }
  SameProjectGradeConstraint
  some Grade.first.next.next // Ensure at least 3 grades exist for this setup
} for 4 expect 1

// Positive Instance 2: Students work on the same project and have identical grades (0 unit difference).
run {
  some disj s1, s2: Student {
    some c: Course {
      some p: Project {
        p in c.projects
        s1 in c.enrolled and s2 in c.enrolled
        p in s1.projects
        p in s2.projects
        c.grades[s1] = Grade.first
        c.grades[s2] = Grade.first // Grades are the same
      }
    }
  }
  SameProjectGradeConstraint
  some Grade // Ensure at least 1 grade exists
} for 4 expect 1

// Positive Instance 3: Students work on the same project and their grades differ by exactly one unit.
run {
  some disj s1, s2: Student {
    some c: Course {
      some p: Project {
        p in c.projects
        s1 in c.enrolled and s2 in c.enrolled
        p in s1.projects
        p in s2.projects
        c.grades[s1] = Grade.first
        c.grades[s2] = Grade.first.next // Grades differ by one unit
      }
    }
  }
  SameProjectGradeConstraint
  some Grade.first.next // Ensure at least two grades exist for Grade.first.next
} for 4 expect 1

// Positive Instance 4: Students work on the same project, but are enrolled in different courses.
// The premise of the implication (that s1 and s2 are in the *same* course 'c') is false for any single 'c'.
run {
  some disj s1, s2: Student {
    some disj c1, c2: Course { // Two distinct courses
      some p: Project {
        p in c1.projects and p in c2.projects
        s1 in c1.enrolled // s1 in c1
        s2 in c2.enrolled // s2 in c2, thus not s2 in c1 for the premise to hold
        p in s1.projects and p in s2.projects // Both work on 'p'
        // Grades can differ by more than one unit, as the constraint doesn't apply
        c1.grades[s1] = Grade.first
        c2.grades[s2] = Grade.first.next.next
      }
    }
  }
  SameProjectGradeConstraint
  some Grade.first.next.next // Ensure at least three grades for this setup
} for 4 expect 1

// Positive Instance 5: Students are in the same course, but work on different projects.
// The premise of the implication (that s1 and s2 are on the *same* project 'p') is false for any single 'p'.
run {
  some disj s1, s2: Student {
    some c: Course {
      some disj p1, p2: Project { // Two distinct projects
        p1 in c.projects and p2 in c.projects
        s1 in c.enrolled and s2 in c.enrolled
        p1 in s1.projects
        p2 in s2.projects // Students work on different projects
        // Grades can differ by more than one unit, as the constraint doesn't apply
        c.grades[s1] = Grade.first
        c.grades[s2] = Grade.first.next.next
      }
    }
  }
  SameProjectGradeConstraint
  some Grade.first.next.next // Ensure at least three grades for this setup
} for 4 expect 1

// -----------------------------------------------------------------------------
// Negative Instances (expect 0): Scenarios that violate the requirement
// -----------------------------------------------------------------------------

// Negative Instance 1: Two students work on the same project, and their grades differ by more than one unit.
// This is a direct violation of the constraint.
run {
  some disj s1, s2: Student {
    some c: Course {
      some p: Project {
        p in c.projects
        s1 in c.enrolled and s2 in c.enrolled
        p in s1.projects
        p in s2.projects
        c.grades[s1] = Grade.first
        c.grades[s2] = Grade.first.next.next // Grades differ by two units
      }
    }
  }
  SameProjectGradeConstraint
  some Grade.first.next.next // Ensure at least three grades exist for this violation
} for 4 expect 0

// Negative Instance 2: Three students work on the same project; two of them violate the grade difference rule.
// The 'all' quantifier in the predicate means if any pair violates it, the predicate is false.
run {
  some disj s1, s2, s3: Student {
    some c: Course {
      some p: Project {
        p in c.projects
        s1 in c.enrolled and s2 in c.enrolled and s3 in c.enrolled
        p in s1.projects and p in s2.projects and p in s3.projects
        c.grades[s1] = Grade.first
        c.grades[s2] = Grade.first.next
        c.grades[s3] = Grade.first.next.next // S1 and S3 grades differ by more than one unit
      }
    }
  }
  SameProjectGradeConstraint
  some Grade.first.next.next // Ensure at least three grades
} for 4 expect 0

// Negative Instance 3: Multiple projects and courses, but still one specific violation exists.
// Even with other valid conditions, one violation makes the overall constraint false.
run {
  some disj s1, s2: Student {
    some disj c1, c2: Course { // Two distinct courses
      some disj p1, p2: Project { // Two distinct projects
        p1 in c1.projects // p1 exists in c1
        p2 in c2.projects // p2 exists in c2
        s1 in c1.enrolled and s2 in c1.enrolled // Both students in c1
        p1 in s1.projects and p1 in s2.projects // Both students work on p1 in c1
        c1.grades[s1] = Grade.first
        c1.grades[s2] = Grade.first.next.next // Grades differ by more than one unit in C1 for P1
      }
    }
  }
  SameProjectGradeConstraint
  some Grade.first.next.next // Ensure at least three grades for violation
} for 4 expect 0

// Negative Instance 4: Clear violation with grades being `first` and `last` where `last` is sufficiently far from `first`.
// This emphasizes a large difference in grades.
run {
  some disj s1, s2: Student {
    some c: Course {
      some p: Project {
        p in c.projects
        s1 in c.enrolled and s2 in c.enrolled
        p in s1.projects
        p in s2.projects
        c.grades[s1] = Grade.first
        c.grades[s2] = Grade.last // Grades are first and last
      }
    }
  }
  SameProjectGradeConstraint
  // Ensure that Grade.first and Grade.last differ by more than one unit.
  Grade.last != Grade.first and Grade.last != Grade.first.next and Grade.first != Grade.last.next
} for 4 expect 0

// Negative Instance 5: A minimal setup with exactly one course, one project, two students, leading to a violation.
// Ensures that extraneous elements do not mask the core violation.
run {
  one c: Course {
    one p: Project {
      p in c.projects
      some disj s1, s2: Student {
        s1 in c.enrolled and s2 in c.enrolled
        p in s1.projects and p in s2.projects
        c.grades[s1] = Grade.first
        c.grades[s2] = Grade.first.next.next // Grades differ by more than one unit
      }
    }
  }
  SameProjectGradeConstraint
  some Grade.first.next.next // Ensure at least three grades
} for 4 expect 0