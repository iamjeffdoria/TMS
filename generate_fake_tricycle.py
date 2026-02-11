import csv 
import random 
from faker import Faker 
from datetime import timedelta, date 
 
fake = Faker() 
 
# Status choices (matching your updated model) 
status_choices = ["New", "Renewed", "Expired", "Inactive"] 
 
# Remarks options 
remarks_choices = [ 
    "New Registration", 
    "Renewed Permit", 
    "Mayor's Permit Issued", 
    "Expired Permit", 
    "For Renewal", 
    "Pending Documentation",
    "Complete Documents",
    None 
] 
 
# Total rows to generate 
TOTAL_ROWS = 50 
 
# Output file 
output_file = "tricycle_fake.csv" 
 
with open(output_file, mode="w", newline="", encoding="utf-8") as file: 
    writer = csv.writer(file) 
 
    # CSV Header (matching Tricycle model fields) 
    writer.writerow([ 
        "body_number", 
        "name", 
        "address", 
        "make_kind", 
        "engine_motor_no", 
        "chassis_no", 
        "plate_no", 
        "date_registered", 
        "date_expired", 
        "status", 
        "remarks" 
    ]) 
 
    for i in range(TOTAL_ROWS): 
        # Dates 
        date_registered = fake.date_between(start_date="-3y", end_date="today") 
        date_expired = date_registered + timedelta(days=365) 
 
        # Determine status based on dates and randomization
        if date_expired < date.today(): 
            status = "Expired"
        elif date_registered > date.today() - timedelta(days=30):
            # Recently registered (within last 30 days)
            status = "New"
        else:
            # For older registrations, randomly assign Renewed or Inactive
            status = random.choice(["Renewed", "Inactive", "New"])
 
        # Match remarks to status
        if status == "Expired":
            remark = random.choice(["Expired Permit", "For Renewal", None])
        elif status == "New":
            remark = random.choice(["New Registration", "Complete Documents", None])
        elif status == "Renewed":
            remark = random.choice(["Renewed Permit", "Mayor's Permit Issued", None])
        else:  # Inactive
            remark = random.choice(["Pending Documentation", "For Renewal", None])

        writer.writerow([ 
            f"BN-{10000 + i}",                               # body_number 
            fake.name(),                                     # name 
            fake.address().replace("\n", ", "),              # address 
            random.choice(["Honda TMX", "Yamaha Mio", "Suzuki Raider", "Kawasaki XRM", "Rusi"]),    # make_kind 
            f"ENG-{fake.random_number(digits=8)}",           # engine_motor_no 
            f"CHS-{fake.random_number(digits=8)}",           # chassis_no 
            f"{fake.random_uppercase_letter()}{fake.random_uppercase_letter()}{fake.random_number(digits=4)}",  # plate_no 
            date_registered,                                 # date_registered 
            date_expired,                                    # date_expired 
            status,                                          # status 
            remark                                           # remarks 
        ]) 
 
print(f"✅ CSV file generated successfully: {output_file}") 
print(f"📊 Total records: {TOTAL_ROWS}")