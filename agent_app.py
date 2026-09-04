import os
import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ضبط إعدادات الصفحة
st.set_page_config(page_title="واجهة الوكيل - مراجعة التقارير", layout="wide")
st.title("📋 لوحة مراجعة التقارير اليومية (الوكيل)")

# 1. الاتصال بـ Google Sheets API
@st.cache_resource
def init_google_sheets():
    gcp_key_str = os.environ.get("GCP_SA_KEY")
    if not gcp_key_str and "GCP_SA_KEY" in st.secrets:
        gcp_key_str = st.secrets["GCP_SA_KEY"]
        
    creds_dict = json.loads(gcp_key_str)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return build('sheets', 'v4', credentials=creds)

spreadsheet_id = os.environ.get("SPREADSHEET_ID") or st.secrets.get("SPREADSHEET_ID")

try:
    service = init_google_sheets()
except Exception as e:
    st.error(f"خطأ في الاتصال بـ Google Cloud: يرجى التأكد من ضبط متغيرات البيئة SPREADSHEET_ID و GCP_SA_KEY ({e})")
    st.stop()

# 2. دالة جلب اسم الورقة الأولى ديناميكياً
def get_first_sheet_name():
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return sheet_metadata.get('sheets', '')[0].get("properties", {}).get("title", "Sheet1")

sheet_name = get_first_sheet_name()

# 3. دالة جلب التقارير التي لم تُراجع بعد (IsCommentSeen == 'No')
def get_unseen_reports():
    range_name = f"'{sheet_name}'!A:I"
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name
    ).execute()
    rows = result.get('values', [])
    
    unseen = []
    for idx, row in enumerate(rows[1:], start=2):
        is_seen = row[8] if len(row) >= 9 else "No"
        if is_seen.strip().lower() == "no":
            unseen.append({
                "row_index": idx,
                "report_id": row[0] if len(row) > 0 else "",
                "emp_id": row[1] if len(row) > 1 else "",
                "date": row[2] if len(row) > 2 else "",
                "achievement": row[3] if len(row) > 3 else "",
                "challenges": row[4] if len(row) > 4 else "",
                "solution": row[5] if len(row) > 5 else "",
                "is_resolved": row[6] if len(row) > 6 else ""
            })
    return unseen

# 4. دالة تحديث التقرير بإضافة التعليق وتعديل الحالة إلى Yes
def submit_review(row_index, comment):
    range_name = f"'{sheet_name}'!H{row_index}:I{row_index}"
    body = {'values': [[comment, 'Yes']]}
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

# --- عرض الواجهة ---
reports = get_unseen_reports()

if not reports:
    st.success("🎉 لا توجد تقارير جديدة بانتظار المراجعة حالياً!")
else:
    st.info(f"يوجد **{len(reports)}** تقرير جديد يتطلب المراجعة:")

    for report in reports:
        with st.expander(f"📌 تقرير رقم: {report['report_id']} | الموظف: {report['emp_id']} | التاريخ: {report['date']}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**الإنجازات:**\n{report['achievement']}")
                st.markdown(f"**التحديات:**\n{report['challenges']}")
            with col2:
                st.markdown(f"**الحلول المقترحة:**\n{report['solution']}")
                st.markdown(f"**هل تم حل التحدي؟** {report['is_resolved']}")
            
            st.divider()
            
            comment_input = st.text_area(
                "ملاحظات وتوجيهات الوكيل (ManageCo):", 
                key=f"comment_{report['row_index']}"
            )
            
            if st.button("حفظ وإخفاء التقرير", key=f"btn_{report['row_index']}"):
                if not comment_input.strip():
                    st.warning("يرجى كتابة ملاحظة قبل الإرسال.")
                else:
                    submit_review(report['row_index'], comment_input.strip())
                    st.success("تم حفظ الملاحظة وإخفاء التقرير!")
                    st.rerun()