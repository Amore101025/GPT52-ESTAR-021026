document:
  title: "Mock Application — Fillable PDF"
  page_size: "A4"          # A4 | LETTER
  orientation: "portrait"  # portrait | landscape
  unit: "mm"               # mm | pt
  margin:
    left: 12
    top: 12
    right: 12
    bottom: 12
pages:
  - number: 1
    elements:
      - type: "label"
        text: "Mock Application — Fillable PDF"
        x: 12
        y: 14
        size: 14
        style: "B"

      - type: "label"
        text: "Applicant Information"
        x: 12
        y: 26
        size: 12
        style: "B"

      - type: "label"
        text: "Full Name:"
        x: 12
        y: 34
      - type: "field"
        field_type: "text"
        id: "full_name"
        name: "Full_Name"
        x: 50
        y: 31.5
        w: 140
        h: 8
        required: true

      - type: "label"
        text: "Submission Type:"
        x: 12
        y: 46
      - type: "field"
        field_type: "dropdown"
        id: "submission_type"
        name: "Submission_Type"
        x: 50
        y: 43.5
        w: 60
        h: 8
        options: ["510(k)", "PMA", "De Novo"]

      - type: "label"
        text: "Confirm Accuracy:"
        x: 12
        y: 58
      - type: "field"
        field_type: "checkbox"
        id: "confirm"
        name: "Confirm"
        x: 50
        y: 56
        w: 5
        h: 5

      - type: "label"
        text: "Additional Notes:"
        x: 12
        y: 70
      - type: "field"
        field_type: "textarea"
        id: "notes"
        name: "Notes"
        x: 12
        y: 74
        w: 178
        h: 40
        multiline: true
