import streamlit as st
import os
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- إعدادات الصفحة والشعار ---
st.set_page_config(page_title="نظام التقارير اليومية 440440", page_icon="📋", layout="centered")

# الهيدر العلوي مع الرمز 440440
st.markdown("""
    <div style="text-align: center; padding: 12px; background-color: #0F172A; color: white; border-radius: 10px; margin-bottom: 25px;">
        <h2 style="margin:0; color: #38BDF8;">📋 نظام التقارير اليومية</h2>
        <span style="font-size: 14px; opacity: 0.8;">المعرف المرجعي: #440440</span>
    </div>
""", unsafe_allow_html=True)

# --- الاتصال بـ Google Sheets ---
@st.cache_resource
def init_google_sheets():
    # جلب الاعتمادات من Secrets
    if "GCP_SA_KEY" in st.secrets:
        gcp_key = st.secrets["GCP_SA_KEY"]
    else:
        gcp_key = os.environ.get("GCP_SA_KEY")

    # إذا كانت القيمة نصية JSON وليست Dictionary
    if isinstance(gcp_key, str):
        creds_dict = json.loads(gcp_key)
    else:
        # تحويل SecretsAttr إلى Dictionary بايثون عادي
        creds_dict = dict(gcp_key)

    # إصلاح ترميز الأسطر الجديدة في PEM
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return build('sheets', 'v4', credentials=creds)

try:
    service = init_google_sheets()
    SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID") or st.secrets.get("SPREADSHEET_ID")
except Exception as e:
    st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
    st.stop()

# --- القائمة الجانبية للتنقل ---
st.sidebar.title("📌 القائمة الرئيسية")
page = st.sidebar.radio("اختر الواجهة:", ["📝 تقديم تقرير جديد (للموظفين)", "🔍 لوحة المراجعة (للوكيل)"])

# ==========================================
# 1. واجهة الموظفين (إدخال البيانات)
# ==========================================
if page == "📝 تقديم تقرير جديد (للموظفين)":
    st.subheader("إرسال التقرير اليومي")
    st.write("قم بتعبئة الحقول التالية ثم اضغط على إرسال:")

    with st.form("employee_report_form", clear_on_submit=True):
        emp_name = st.text_input("اسم الموظف / الرقم الوظيفي:*")
        achievements = st.text_area("الإنجازات اليومية:*", help="ما هي المهام التي أتممتها اليوم؟")
        challenges = st.text_area("التحديات والصعوبات (إن وجدت):")
        notes = st.text_area("ملاحظات إضافية:")
        
        submit_btn = st.form_submit_button("🚀 إرسال التقرير الان")

    if submit_btn:
        if not emp_name.strip() or not achievements.strip():
            st.warning("⚠️ يرجى ملء الحقول الأساسية (الاسم والإنجازات).")
        else:
            try:
                # تجهيز الصف المراد إضافته في Google Sheets
                # الترتيب: [التاريخ والوقت, الاسم, الإنجازات, التحديات, الملاحظات, IsCommentSeen]
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = [current_time, emp_name, achievements, challenges, notes, "No"]

                # إضافة الصف إلى جدول Google Sheets مباشرة
                service.spreadsheets().values().append(
                    spreadsheetId=SPREADSHEET_ID,
                    range="Sheet1!A:F",
                    valueInputOption="USER_ENTERED",
                    body={"values": [new_row]}
                ).execute()

                st.success("✅ تم إرسال تقريرك بنجاح للوكيل دون الحاجة لأي حساب!")
                st.balloons()
            except Exception as ex:
                st.error(f"حدث خطأ أثناء حفظ التقرير: {ex}")

# ==========================================
# 2. واجهة الوكيل (مراجعة التقارير)
# ==========================================
elif page == "🔍 لوحة المراجعة (للوكيل)":
    st.subheader("لوحة مراجعة التقارير غير المقروءة")
    
    # حماية بسيطة بكلمة مرور للوكيل
    agent_pass = st.sidebar.text_input("كلمة مرور الوكيل:", type="password")
    
    if agent_pass == "440440":  # يمكنك تغيير كلمة المرور هنا
        try:
            # جلب كافة البيانات من Google Sheets
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range="Sheet1!A:F"
            ).execute()
            
            rows = result.get('values', [])
            
            if not rows or len(rows) <= 1:
                st.info("لا توجد تقارير مسجلة حتى الآن.")
            else:
                # تصفية التقارير التي تكون فيها حالة IsCommentSeen == 'No' (العمود السادس F)
                unseen_reports = []
                for idx, row in enumerate(rows[1:], start=2): # start=2 لأن السطر الأول هو الهيدر
                    is_seen = row[5] if len(row) > 5 else "No"
                    if is_seen == "No":
                        unseen_reports.append((idx, row))

                st.metric("عدد التقارير الجديدة غير المقروءة", len(unseen_reports))
                st.divider()

                if not unseen_reports:
                    st.success("🎉 جميع التقارير تم الاطلاع عليها ومراجعتها!")
                else:
                    for sheet_row_num, report in unseen_reports:
                        with st.expander(f"📌 تقرير: {report[1]} - {report[0] if len(report)>0 else ''}"):
                            st.write(f"**الإنجازات:**\n{report[2] if len(report)>2 else '-'}")
                            st.write(f"**التحديات:**\n{report[3] if len(report)>3 else '-'}")
                            st.write(f"**ملاحظات:**\n{report[4] if len(report)>4 else '-'}")
                            
                            # زر تحديد التقرير كمقروء
                            if st.button(f"تحديث كـ 'تمت المراجعة' ✅", key=f"btn_{sheet_row_num}"):
                                # تحديث القيمة في Google Sheets إلى 'Yes'
                                service.spreadsheets().values().update(
                                    spreadsheetId=SPREADSHEET_ID,
                                    range=f"Sheet1!F{sheet_row_num}",
                                    valueInputOption="USER_ENTERED",
                                    body={"values": [["Yes"]]}
                                ).execute()
                                
                                st.success("تم تحديث الحالة!")
                                st.rerun()
        except Exception as ex:
            st.error(f"خطأ في جلب البيانات: {ex}")
    else:
        st.warning("🔒 يرجى إدخال كلمة مرور الوكيل في الشريط الجانبي لعرض التقارير.")