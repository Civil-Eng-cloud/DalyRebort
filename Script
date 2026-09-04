// رابط تطبيق Google Apps Script (سيتم استبداله برابط مشروعك لاحقاً)
const GOOGLE_SCRIPT_URL = "YOUR_GOOGLE_APPS_SCRIPT_WEB_APP_URL";

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const message = document.getElementById('message');

    message.textContent = "جاري التحقق...";

    // محاكاة تسجيل الدخول (يمكن ربطها مباشرة بـ Google Apps Script)
    // الأدوار المتاحة: 'employee', 'agent', 'manager'
    
    setTimeout(() => {
        // اختبار تجريبي:
        if (username === "emp" && password === "123") {
            showDashboard("الموظف أحمد", "employee");
        } else if (username === "agent" && password === "123") {
            showDashboard("الوكيل خالد", "agent");
        } else if (username === "admin" && password === "123") {
            showDashboard("المدير العام", "manager");
        } else {
            message.style.color = "red";
            message.textContent = "اسم المستخدم أو كلمة المرور غير صحيحة";
        }
    }, 1000);
});

function showDashboard(name, role) {
    document.getElementById('loginBox').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
    document.getElementById('welcomeText').textContent = `مرحباً، ${name}`;

    // إخفاء جميع الأقسام أولاً
    document.querySelectorAll('.role-section').forEach(sec => sec.classList.add('hidden'));

    // إظهار الواجهة الخاصة بالدور
    if (role === 'employee') {
        document.getElementById('employeeView').classList.remove('hidden');
    } else if (role === 'agent') {
        document.getElementById('agentView').classList.remove('hidden');
    } else if (role === 'manager') {
        document.getElementById('managerView').classList.remove('hidden');
    }
}

function logout() {
    document.getElementById('dashboard').classList.add('hidden');
    document.getElementById('loginBox').classList.remove('hidden');
    document.getElementById('loginForm').reset();
    document.getElementById('message').textContent = "";
}