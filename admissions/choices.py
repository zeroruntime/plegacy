ALUMNI_SPECIAL_YEAR_GROUPS = [
    '1993_shs',
    '1993_olevel',
    '1994_shs',
    '1994_olevel',
]

ALUMNI_YEAR_GROUPS = [
    str(year)
    for year in range(1971, 2016)
    if year not in (1993, 1994)
] + ALUMNI_SPECIAL_YEAR_GROUPS

ALUMNI_YEAR_GROUP_CHOICES = [(year_group, year_group) for year_group in ALUMNI_YEAR_GROUPS]

ALUMNI_HOUSE_CHOICES = [(f'House {number}', f'House {number}') for number in range(1, 14)]

ALUMNI_RELATIONSHIP_CHOICES = [
    ('Son', 'Son'),
    ('Nephew', 'Nephew'),
    ('Grandson', 'Grandson'),
    ('Other', 'Other'),
]

PARENT_RELATIONSHIP_CHOICES = [
    ('Parent', 'Parent'),
    ('Guardian', 'Guardian'),
]

PROGRAM_CHOICES = [
    ('General Arts', 'General Arts'),
    ('Visual Arts', 'Visual Arts'),
    ('Business', 'Business'),
    ('General Science', 'General Science'),
]

BECE_SUBJECTS = [
    'ARABIC',
    'CAREER TECHNOLOGY',
    'COMPUTING',
    'CREATIVE ART AND DESIGN',
    'ENGLISH LANGUAGE',
    'FRENCH',
    'GHANAIAN LANGUAGE',
    'MATHEMATICS',
    'RELIGIOUS AND MORAL EDUCATION',
    'SCIENCE',
    'SOCIAL STUDIES',
]


def choice_list_with_blank(choices, label='Select an option'):
    return [('', label), *choices]
