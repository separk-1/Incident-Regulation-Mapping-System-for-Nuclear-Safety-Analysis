import csv
import json

# JSON 데이터 로드
input_file = "kg_hr.json"  # JSON 파일 경로
output_file = "kg_hr.csv"  # 저장할 CSV 파일 경로

with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# CSV 저장
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)

    # CSV 헤더 작성
    writer.writerow([
        "Filename", "Task", "Event", "Cause", "Influence", "Corrective Actions",
        "Facility", "Unit", "Event Date", "Title", "Clause"
    ])

    # 데이터 작성
    for record in data:
        filename = record["filename"]
        attributes = record["attributes"]
        metadata = record["metadata"]

        # 여러 값이 있을 경우 리스트를 쉼표로 연결
        tasks = ", ".join(attributes.get("Task", []))
        events = ", ".join(attributes.get("Event", []))
        causes = ", ".join(attributes.get("Cause", []))
        influences = ", ".join(attributes.get("Influence", []))
        corrective_actions = ", ".join(attributes.get("Corrective Actions", []))

        facility = metadata["facility"]["name"]
        unit = metadata["facility"]["unit"]
        event_date = metadata["event_date"]
        title = metadata["title"]
        clause = metadata["clause"]

        # 한 줄 데이터 작성
        writer.writerow([
            filename, tasks, events, causes, influences, corrective_actions,
            facility, unit, event_date, title, clause
        ])

print(f"Data exported to {output_file}")
