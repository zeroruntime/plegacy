CORE_SUBJECTS = {
    'ENGLISH LANGUAGE',
    'MATHEMATICS',
    'SCIENCE',
    'SOCIAL STUDIES',
}


class AggregateScoreError(ValueError):
    pass


def calculate_aggregate_score(subject_grades):
    valid_grades = {}

    for subject, grade in subject_grades.items():
        normalized_subject = subject.strip().upper()
        try:
            numeric_grade = int(str(grade).strip())
        except (TypeError, ValueError) as exc:
            raise AggregateScoreError(f'{subject} grade must be a number from 0 to 9.') from exc

        if numeric_grade < 0 or numeric_grade > 9:
            raise AggregateScoreError(f'{subject} grade must be between 0 and 9.')

        if numeric_grade == 0:
            continue

        valid_grades[normalized_subject] = numeric_grade

    core_results = [
        (subject, grade)
        for subject, grade in valid_grades.items()
        if subject in CORE_SUBJECTS
    ]
    elective_results = [
        (subject, grade)
        for subject, grade in valid_grades.items()
        if subject not in CORE_SUBJECTS
    ]

    if len(core_results) < 4:
        raise AggregateScoreError(
            'Enter valid grades for all 4 core subjects: English Language, Mathematics, Science, and Social Studies.'
        )

    if len(elective_results) < 2:
        raise AggregateScoreError('Enter valid grades for at least 2 elective subjects.')

    selected_core = sorted(core_results, key=lambda result: result[1])[:4]
    selected_electives = sorted(elective_results, key=lambda result: result[1])[:2]
    selected_subjects = selected_core + selected_electives

    return {
        'score': sum(grade for _, grade in selected_subjects),
        'subjects': selected_subjects,
    }
