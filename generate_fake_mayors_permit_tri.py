import csv
import random
from faker import Faker
from datetime import timedelta, date

fake = Faker()

# Quarter choices
quarter_choices = [
    "First Quarter",
    "Second Quarter",
    "Third Quarter",
    "Fourth Quarter"
]

# Status choices
status_choices = ["active", "inactive", "expired"]

# Total rows to generate
TOTAL_ROWS = 500

# Output file
output_file = "mayors_permit_tricycle_fake.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # CSV Header (matching your model fields)
    writer.writerow([
        'control_no',
        'name',
        'address',
        'motorized_operation',
        'business_name',
        'expiry_date',
        'amount_paid',
        'or_no',
        'issue_date',
        'issued_at',
        'mayor',
        'quarter',
        'status'
    ])

    for i in range(TOTAL_ROWS):
        issue_date = fake.date_between(start_date='-2y', end_date='today')
        expiry_date = issue_date + timedelta(days=365)

        writer.writerow([
            f"TRI-{1000+i}",                       # control_no
            fake.name(),                            # name
            fake.address().replace("\n", ", "),     # address
            "Tricycle",                             # motorized_operation (fixed)
            fake.company() + " Tricycle Service",   # business_name
            expiry_date,                             # expiry_date
            random.randint(500, 3000),              # amount_paid
            f"OR-{fake.random_number(digits=6)}",   # or_no
            issue_date,                              # issue_date
            fake.city(),                             # issued_at
            random.choice(["Mayor Juan", "Mayor Ana", "Mayor Cruz"]),  # mayor
            random.choice(quarter_choices),         # quarter
            random.choice(status_choices)           # status
        ])

print(f"CSV file generated: {output_file}")
