import csv
import random
from faker import Faker
from datetime import timedelta, date

fake = Faker()

# Status choices matching Franchise model
status_choices = ["New", "Renewal", "Renewed", "Expired", "Inactive"]

# Sample routes
routes = [
    "Poblacion - Market - Hospital",
    "Barangay 1 - Barangay 5 - Town Hall",
    "Terminal - School - Church",
    "Market - Cemetery - Park",
    "North District - South District",
]

# Sample treasurers
treasurers = [
    "Juan dela Cruz",
    "Maria Santos",
    "Pedro Reyes",
    "Ana Garcia",
    "Jose Mendoza",
]

# Total rows to generate
TOTAL_ROWS = 500

# Output file
output_file = "franchise_fake.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    # CSV Header (matching Franchise model fields, excluding tricycle FK)
    writer.writerow([
        'name',
        'denomination',
        'plate_no',
        'valid_until',
        'motor_no',
        'authorized_no',
        'chassis_no',
        'authorized_route',
        'purpose',
        'official_receipt_no',
        'date',
        'amount_paid',
        'municipal_treasurer',
        'status',
    ])

    for i in range(TOTAL_ROWS):
        date_issued = fake.date_between(start_date='-2y', end_date='today')
        valid_until = date_issued + timedelta(days=365)

        writer.writerow([
            fake.name(),                                        # name
            random.choice(["Single", "Double", "Sidecar"]),    # denomination
            f"TRI-{fake.random_number(digits=4, fix_len=True)}",  # plate_no
            valid_until,                                        # valid_until
            f"MN-{fake.random_number(digits=7, fix_len=True)}", # motor_no
            f"AUTH-{1000 + i}",                                 # authorized_no
            f"CHS-{fake.random_number(digits=7, fix_len=True)}",# chassis_no
            random.choice(routes),                              # authorized_route
            random.choice([
                "Public Transport",
                "School Service",
                "Market Delivery",
                None,
            ]),                                                 # purpose
            f"OR-{fake.random_number(digits=6, fix_len=True)}", # official_receipt_no
            date_issued,                                        # date
            round(random.uniform(500, 5000), 2),               # amount_paid
            random.choice(treasurers),                          # municipal_treasurer
            random.choice(status_choices),                      # status
        ])

print(f"✅ CSV file generated: {output_file} ({TOTAL_ROWS} rows)")