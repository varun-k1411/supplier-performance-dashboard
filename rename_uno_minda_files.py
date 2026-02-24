import os
import re

# EXACT folder path where your Excel files are located
folder_path = r"C:\Users\Lenovo\PycharmProjects\Supplier Performance Trends\data"

print("\nScanning folder:")
print(folder_path)
print("\nFiles found:\n")


def get_clean_plant_name(text):

    text = text.upper()

    if "SENSOR" in text and "PUNE" in text:
        return "Sensor_Pune"

    elif "SWITCH" in text and "PUNE" in text:
        return "Switch_Pune"

    elif "SWITCH" in text and "HOSUR" in text:
        return "Switch_Hosur"

    elif "SWITCH" in text and "PANTNAGAR" in text:
        return "Switch_Pantnagar"

    else:
        return "Unknown"


rename_count = 0

for filename in os.listdir(folder_path):

    print("Found:", filename)

    if filename.endswith(".xlsx"):

        # Extract date pattern like 03.2025
        date_match = re.search(r'(\d{2})\.(\d{4})', filename)

        # Extract plant name
        plant_match = re.search(r'UNO MINDA-(.*?) -', filename)

        if date_match and plant_match:

            month = date_match.group(1)
            year = date_match.group(2)

            plant_raw = plant_match.group(1)
            plant = get_clean_plant_name(plant_raw)

            new_filename = f"{year}_{month}_{plant}.xlsx"

            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)

            # Skip if already renamed
            if old_path != new_path:

                print("\nRenaming:")
                print("OLD:", filename)
                print("NEW:", new_filename)

                os.rename(old_path, new_path)

                rename_count += 1

print(f"\nDone. Total files renamed: {rename_count}")