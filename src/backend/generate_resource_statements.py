import random

def generate_insert_statements(num_entries):
    lat_min, lat_max = 12.8805, 13.0352
    long_min, long_max = 77.5805, 77.6890
    types = ['Ambulance', 'Fire Truck', 'Police Car']
    statuses = ['available']

    insert_statements = []

    for _ in range(num_entries):
        resource_type = random.choice(types)
        current_latitude = round(random.uniform(lat_min, lat_max), 4)
        current_longitude = round(random.uniform(long_min, long_max), 4)
        status = random.choice(statuses)

        statement = f"('{resource_type}', {current_latitude}, {current_longitude}, '{status}')"
        insert_statements.append(statement)

    return insert_statements

def main():
    num_entries = 100  # Adjust the number of entries as needed
    statements = generate_insert_statements(num_entries)
    print("INSERT INTO resources (type, current_latitude, current_longitude, status) VALUES")
    print(",\n".join(statements) + ";")

if __name__ == "__main__":
    main()