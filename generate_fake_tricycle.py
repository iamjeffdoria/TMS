import csv
import random
from faker import Faker
from datetime import timedelta, date

fake = Faker()

REMARKS_CHOICES = ['with_mayors_permit', 'without_mayors_permit', None]

TOTAL_ROWS = 20
output_file = "tricycle_fake.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    writer.writerow([
        "body_number", "name", "address", "make_kind",
        "engine_motor_no", "chassis_no", "plate_no",
        "date_registered", "date_expired", "status", "remarks"
    ])

    for i in range(TOTAL_ROWS):
        date_registered = fake.date_between(start_date="-3y", end_date="today")
        date_expired = date_registered + timedelta(days=365)

        if date_expired < date.today():
            status = "Expired"
        elif date_registered > date.today() - timedelta(days=30):
            status = "New"
        else:
            status = random.choice(["Renewed", "Inactive", "New"])

        remark = random.choice(REMARKS_CHOICES)

        writer.writerow([
            f"BN-{10000 + i}",
            fake.name(),
            fake.address().replace("\n", ", "),
            random.choice(["Honda TMX", "Yamaha Mio", "Suzuki Raider", "Kawasaki XRM", "Rusi"]),
            f"ENG-{fake.random_number(digits=8)}",
            f"CHS-{fake.random_number(digits=8)}",
            f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{fake.random_number(digits=4)}",
            date_registered,
            date_expired,
            status,
            remark
        ])

print(f"✅ CSV file generated successfully: {output_file}")
print(f"📊 Total records: {TOTAL_ROWS}")