import csv
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Quarter choices
quarters = [
    "First Quarter",
    "Second Quarter",
    "Third Quarter",
    "Fourth Quarter"
]

def random_date(start, end):
    """Generate a random date between two dates."""
    return start + timedelta(
        days=random.randint(0, (end - start).days)
    )

# Generate 50 fake rows (you can change this)
TOTAL_ROWS = 10000

# File name
output_file = "mayors_permit_fake.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # CSV Header
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

    # Generate fake rows
    for i in range(TOTAL_ROWS):
        issue_date = fake.date_between(start_date='-2y', end_date='today')
        expiry_date = issue_date + timedelta(days=365)

        status = random.choice(["active", "inactive", "expired"])

        writer.writerow([
            f"CTRL-{1000+i}",                        # control_no
            fake.name(),                             # name
            fake.address().replace("\n", ", "),      # address
            random.choice(["Tricycle", "Van", "Taxi", "Motorcycle"]),  # motorized_operation
            fake.company(),                          # business_name
            expiry_date,                              # expiry_date
            random.randint(100, 5000),               # amount_paid
            f"OR-{fake.random_number(digits=6)}",    # or_no
            issue_date,                               # issue_date
            fake.city(),                              # issued_at
            random.choice(["Mayor Juan", "Mayor Ana", "Mayor Cruz"]),  # mayor
            random.choice(quarters),                 # quarter
            status                                    # status
        ])

print(f"CSV file generated: {output_file}")
