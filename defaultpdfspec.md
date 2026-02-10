document:
  title: "申請表 — Mock Application (Unicode)"
  page_size: "A4"
  orientation: "portrait"
  unit: "mm"
  margin:
    left: 12
    top: 12
    right: 12
    bottom: 12
fonts:
  default:
    family: "DejaVuSans"
    size: 11
  cjk:
    family: "NotoSansTC"
    size: 11

pages:
  - number: 1
    elements:
      - type: "label"
        text: "申請表 — Mock Application (Unicode)"
        x: 12
        y: 14
        size: 14
        style: "B"

      - type: "label"
        text: "Applicant Information / 申請人資料"
        x: 12
        y: 26
        size: 12
        style: "B"

      - type: "label"
        text: "Full Name / 姓名:"
        x: 12
        y: 36
      - type: "field"
        field_type: "text"
        id: "full_name"
        name: "Full_Name"
        x: 55
        y: 33.5
        w: 140
        h: 8
        required: true

      - type: "label"
        text: "Submission Type / 送件類型:"
        x: 12
        y: 48
      - type: "field"
        field_type: "dropdown"
        id: "submission_type"
        name: "Submission_Type"
        x: 55
        y: 45.5
        w: 70
        h: 8
        options: ["510(k)", "PMA", "De Novo"]

      - type: "label"
        text: "Confirm Accuracy / 確認資料正確:"
        x: 12
        y: 60
      - type: "field"
        field_type: "checkbox"
        id: "confirm"
        name: "Confirm"
        x: 75
        y: 58
        w: 5
        h: 5

      - type: "label"
        text: "Additional Notes / 補充說明:"
        x: 12
        y: 72
      - type: "field"
        field_type: "textarea"
        id: "notes"
        name: "Notes"
        x: 12
        y: 76
        w: 183
        h: 40
        multiline: true
