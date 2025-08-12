import requests
from bs4 import BeautifulSoup
import json

url = "https://www.csc.jfn.ac.lk/courses-direct-intake/"

response = requests.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.text, 'html.parser')

course_titles = soup.find_all("div", class_="su-spoiler-title")
course_contents = soup.find_all("div", class_="su-spoiler-content")

# Provided course lists per level:
level_1_courses = {
    "CSC101S3", "CSC102S3", "CSC103S3", "CSC104S2", "CSC105S3", "CSC106S3",
    "CSC107S2", "CSC108S2", "CSC109S2", "CSC110S2", "CSC111S2", "CSC112S3"
}
level_2_courses = {
    "CSC201S2", "CSC202S2", "CSC203S2", "CSC204S2", "CSC205S2", "CSC206S4",
    "CSC207S3", "CSC208S3", "CSC209S3", "CSC210S3", "CSC211S2", "CSC212S2"
}
level_3_courses = {
    "CSC301S3", "CSC302S2", "CSC303S2", "CSC304S3", "CSC305S2", "CSC306S3",
    "CSC307S3", "CSC308S3", "CSC309S3", "CSC310S3", "CSC311S3", "CSC312S3"
}
level_4_courses = {
    "CSC401S3", "CSC402S3", "CSC403S3", "CSC404S3", "CSC405S3", "CSC406S6",
    "CSC407S6"
}

all_courses = []

def extract_course_code(course_name):
    # Extract code from course title line, e.g. "CSC101S3: Foundations..."
    if ":" in course_name:
        return course_name.split(":")[0].strip()
    else:
        return course_name.strip()

for title_div, content_div in zip(course_titles, course_contents):
    course_name = title_div.get_text(strip=True)
    course_code = extract_course_code(course_name)

    # Filter only if course_code in your lists
    if course_code not in level_1_courses.union(level_2_courses, level_3_courses, level_4_courses):
        continue

    course_data = {"Course Name": course_name, "Course Code": course_code}

    table = content_div.find("table")
    if not table:
        continue

    rows = table.find_all("tr")
    course_info = {}

    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 2:
            key = cols[0].get_text(strip=True).rstrip(':')
            value = cols[1].get_text(strip=True)
            course_info[key] = value
        elif len(cols) > 2:
            key = cols[0].get_text(strip=True).rstrip(':')
            value_parts = []
            for col in cols[1:]:
                ul = col.find("ul")
                if ul:
                    items = [li.get_text(strip=True) for li in ul.find_all("li")]
                    value_parts.extend(items)
                else:
                    text = col.get_text(strip=True)
                    if text:
                        value_parts.append(text)
            course_info[key] = value_parts if len(value_parts) > 1 else (value_parts[0] if value_parts else "")

    course_data.update(course_info)
    all_courses.append(course_data)

# Save filtered courses to JSON
with open("filtered_courses.json", "w", encoding="utf-8") as json_file:
    json.dump(all_courses, json_file, ensure_ascii=False, indent=4)

# Save filtered courses to text file
with open("filtered_courses.txt", "w", encoding="utf-8") as txt_file:
    for course in all_courses:
        txt_file.write(f"Course: {course.get('Course Name', 'N/A')}\n")
        for key, value in course.items():
            if key in ("Course Name", "Course Code"):
                continue
            if isinstance(value, list):
                txt_file.write(f"{key}:\n")
                for item in value:
                    txt_file.write(f"  - {item}\n")
            else:
                txt_file.write(f"{key}: {value}\n")
        txt_file.write("\n" + "-"*80 + "\n\n")

print(f"Scraped {len(all_courses)} courses matching the provided lists.")
print("Data saved to filtered_courses.json and filtered_courses.txt")
