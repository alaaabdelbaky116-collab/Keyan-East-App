import flet as ft
import inspect
from supabase import create_client, Client

# ==========================================
# طبقة التوافق الشاملة مع إصدارات Flet 1.0+
# ==========================================
if hasattr(ft, "Icons"):
    ft.icons = ft.Icons
if hasattr(ft, "Colors"):
    ft.colors = ft.Colors
if hasattr(ft, "BoxFit"):
    ft.ImageFit = ft.BoxFit
if hasattr(ft, "Margin"):
    ft.margin = ft.Margin
    if not hasattr(ft.margin, "only"):
        ft.margin.only = staticmethod(lambda left=0, top=0, right=0, bottom=0: ft.Margin(left=left, top=top, right=right, bottom=bottom))
    if not hasattr(ft.margin, "symmetric"):
        ft.margin.symmetric = staticmethod(lambda vertical=0, horizontal=0: ft.Margin(left=horizontal, top=vertical, right=horizontal, bottom=vertical))
if hasattr(ft, "Padding"):
    ft.padding = ft.Padding

_BtnCls = getattr(ft, "ElevatedButton", None) or getattr(ft, "Button", None) or getattr(ft, "FilledButton", None)
def _compat_elevated_button(*args, **kwargs):
    sig = inspect.signature(_BtnCls.__init__).parameters
    if "text" in kwargs and "text" not in sig:
        t = kwargs.pop("text")
        if not args:
            args = (t,)
    if kwargs.get("width") == float("inf"):
        kwargs["width"] = 350
    bg = kwargs.get("bgcolor")
    fg = kwargs.get("color")
    if ("bgcolor" not in sig or "color" not in sig) and hasattr(ft, "ButtonStyle"):
        kwargs.pop("bgcolor", None)
        kwargs.pop("color", None)
        kwargs["style"] = ft.ButtonStyle(bgcolor=bg, color=fg)
    valid = {k: v for k, v in kwargs.items() if k in sig or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.values())}
    return _BtnCls(*args, **valid)
ft.ElevatedButton = _compat_elevated_button

_OrigTF = ft.TextField
def _compat_textfield(*args, **kwargs):
    sig = inspect.signature(_OrigTF.__init__).parameters
    if "icon" in kwargs and "icon" not in sig and "prefix_icon" in sig:
        kwargs["prefix_icon"] = kwargs.pop("icon")
    valid = {k: v for k, v in kwargs.items() if k in sig or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.values())}
    return _OrigTF(*args, **valid)
ft.TextField = _compat_textfield

_OrigImg = ft.Image
def _compat_image(*args, **kwargs):
    sig = inspect.signature(_OrigImg.__init__).parameters
    valid = {k: v for k, v in kwargs.items() if k in sig or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.values())}
    return _OrigImg(*args, **valid)
ft.Image = _compat_image

# ==========================================
# إعدادات الاتصال بـ Supabase
# ==========================================
SUPABASE_URL = 'https://paarkycuhrljagdiqkdo.supabase.co'
SUPABASE_KEY = 'sb_publishable_IJDNFFyeIOxYyPXUJFjN4w_l9WIAxOP'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Keyan-East App"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    def open_dlg(dlg):
        page.dialog = dlg
        dlg.open = True
        for m in ("show_dialog", "open"):
            if hasattr(page, m):
                try:
                    getattr(page, m)(dlg)
                    return
                except Exception:
                    pass
        if dlg not in page.overlay:
            page.overlay.append(dlg)
        page.update()

    def close_dlg(dlg=None):
        target = dlg or getattr(page, "dialog", None)
        if target:
            target.open = False
        for m in ("pop_dialog", "close"):
            if hasattr(page, m):
                try:
                    getattr(page, m)() if m == "pop_dialog" else getattr(page, m)(target)
                    return
                except Exception:
                    pass
        page.update()

    def show_snack(msg, color=ft.colors.GREEN):
        snack = ft.SnackBar(ft.Text(msg), bgcolor=color, open=True)
        open_dlg(snack)

    def open_external_link(url):
        if not url:
            show_snack("الرابط غير متوفر حالياً", ft.colors.ORANGE_800)
            return
        try:
            page.launch_url(url)
        except Exception as ex:
            show_snack(f"تعذر فتح الرابط: {ex}", ft.colors.RED)

    def show_loading(title="جاري التحميل..."):
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text(title), bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE)
        page.add(
            ft.Container(height=100),
            ft.ProgressRing(color=ft.colors.INDIGO_900),
            ft.Text("يرجى الانتظار...", size=16, color=ft.colors.GREY_700)
        )
        page.update()

    # ==========================================
    # --- قسم الإدارة وخدمة العملاء (Admin & CS Panel) ---
    # ==========================================
    def load_admin_panel(role="admin"):
        page.clean()
        panel_title = "لوحة الإدارة العليا (Keyan-East)" if role == "admin" else "لوحة خدمة العملاء (Keyan-East)"
        panel_color = ft.colors.RED_900 if role == "admin" else ft.colors.TEAL_800

        page.appbar = ft.AppBar(
            title=ft.Text(panel_title),
            bgcolor=panel_color,
            color=ft.colors.WHITE,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: load_intro_screen(), icon_color=ft.colors.WHITE)
        )

        controls_list = []

        if role == "admin":
            logo_url_field = ft.TextField(label="رابط اللوجو", width=300)
            about_text_field = ft.TextField(label="وصف الشركة", multiline=True, width=300)
            ann_field = ft.TextField(label="شريط الأخبار العاجلة (يظهر بأعلى التطبيق)", width=300)
            wa_field = ft.TextField(label="رابط واتساب (مثال: https://wa.me/2010...)", width=300)
            map_field = ft.TextField(label="رابط موقع الشركة على Google Maps", width=300)

            def update_company(e):
                try:
                    supabase.table("company_info").insert({
                        "logo_url": logo_url_field.value,
                        "about_text": about_text_field.value,
                        "announcement": ann_field.value,
                        "whatsapp": wa_field.value,
                        "maps_url": map_field.value
                    }).execute()
                    show_snack("تم تحديث بيانات الشركة وشريط الأخبار!")
                except Exception as ex:
                    show_snack(f"خطأ: {ex}", ft.colors.RED)

            f_name = ft.TextField(label="اسم المؤسس", width=250)
            f_role = ft.TextField(label="المسمى الوظيفي", width=250)
            f_bio = ft.TextField(label="نبذة تعريفية", width=300, multiline=True)
            def add_founder(e):
                try:
                    supabase.table("founders").insert({"name": f_name.value, "role": f_role.value, "bio": f_bio.value}).execute()
                    show_snack("تم إضافة المؤسس!")
                    f_name.value = f_role.value = f_bio.value = ""
                    page.update()
                except Exception as ex:
                    show_snack(f"خطأ: {ex}", ft.colors.RED)

            p_id = ft.TextField(label="كود المشروع", width=180)
            p_name = ft.TextField(label="اسم المشروع", width=220)
            p_loc = ft.TextField(label="الموقع", width=200)
            p_prog = ft.TextField(label="نسبة الإنجاز (0-100)", width=180)
            p_phase = ft.TextField(label="المرحلة الحالية", width=220)
            p_desc = ft.TextField(label="وصف المشروع", width=300, multiline=True)
            p_img = ft.TextField(label="رابط الصورة الرئيسية", width=300)
            def add_curr_proj(e):
                try:
                    supabase.table("projects").insert({
                        "project_id": p_id.value.strip(), "name": p_name.value, "location": p_loc.value,
                        "progress": float(p_prog.value) / 100, "phase": p_phase.value,
                        "description": p_desc.value, "image_url": p_img.value
                    }).execute()
                    show_snack("تم إضافة المشروع الحالي!")
                    p_id.value = p_name.value = p_loc.value = p_prog.value = p_phase.value = p_desc.value = p_img.value = ""
                    page.update()
                except Exception as ex:
                    show_snack(f"خطأ: {ex}", ft.colors.RED)

            up_pid = ft.TextField(label="كود المشروع المراد تحديثه", width=200)
            up_prog = ft.TextField(label="نسبة الإنجاز الجديدة (0-100)", width=200)
            up_phase = ft.TextField(label="المرحلة الحالية الجديدة", width=250)
            def update_proj_progress(e):
                try:
                    data = {}
                    if up_prog.value.strip():
                        data["progress"] = float(up_prog.value.strip()) / 100
                    if up_phase.value.strip():
                        data["phase"] = up_phase.value.strip()
                    supabase.table("projects").update(data).eq("project_id", up_pid.value.strip()).execute()
                    show_snack("تم تحديث نسبة إنجاز المشروع بنجاح!")
                    up_pid.value = up_prog.value = up_phase.value = ""
                    page.update()
                except Exception as ex:
                    show_snack(f"خطأ: {ex}", ft.colors.RED)

            tl_pid = ft.TextField(label="كود المشروع", width=180)
            tl_date = ft.TextField(label="التاريخ (مثال: أكتوبر 2026)", width=200)
            tl_title = ft.TextField(label="وصف التطور (مثال: صب سقف الدور الثالث)", width=300)
            tl_img = ft.TextField(label="رابط صورة الموقع", width=300)
            def add_timeline_update(e):
                try:
                    supabase.table("project_updates").insert({
                        "project_id": tl_pid.value.strip(),
                        "update_date": tl_date.value,
                        "title": tl_title.value,
                        "image_url": tl_img.value
                    }).execute()
                    show_snack("تم نشر التطور الجديد في يوميات المشروع!")
                    tl_pid.value = tl_date.value = tl_title.value = tl_img.value = ""
                    page.update()
                except Exception as ex:
                    show_snack(f"خطأ: {ex}", ft.colors.RED)

            fp_name = ft.TextField(label="اسم المشروع", width=250)
            fp_date = ft.TextField(label="موعد الطرح", width=200)
            fp_desc = ft.TextField(label="التفاصيل", width=300, multiline=True)
            fp_img = ft.TextField(label="رابط الصورة", width=300)
            def add_fut_proj(e):
                try:
                    supabase.table("future_projects").insert({
                        "name": fp_name.value, "date": fp_date.value,
                        "description": fp_desc.value, "image_url": fp_img.value
                    }).execute()
                    show_snack("تم إضافة المشروع المستقبلي!")
                    fp_name.value = fp_date.value = fp_desc.value = fp_img.value = ""
                    page.update()
                except Exception as ex:
                    show_snack(f"خطأ: {ex}", ft.colors.RED)

            s_title = ft.TextField(label="اسم الخدمة", width=250)
            s_details = ft.TextField(label="تفاصيل الخدمة", width=300, multiline=True)
            s_img = ft.TextField(label="رابط صورة الخدمة", width=300)
            def add_srv(e):
                try:
                    supabase.table("services").insert({
                        "title": s_title.value, "details": s_details.value, "image_url": s_img.value
                    }).execute()
                    show_snack("تم إضافة الخدمة!")
                    s_title.value = s_details.value = s_img.value = ""
                    page.update()
                except Exception as ex:
                    show_snack(f"خطأ: {ex}", ft.colors.RED)

            controls_list.extend([
                ft.Text("1. إعدادات الشركة وشريط الأخبار والتواصل", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.RED_900),
                ft.Row([logo_url_field, about_text_field, ann_field, wa_field, map_field], wrap=True),
                ft.ElevatedButton("حفظ إعدادات الشركة", on_click=update_company),
                ft.Divider(),

                ft.Text("2. المؤسسون", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.RED_900),
                ft.Row([f_name, f_role, f_bio], wrap=True),
                ft.ElevatedButton("إضافة مؤسس", on_click=add_founder),
                ft.Divider(),

                ft.Text("3. إضافة مشروع حالي جديد", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.RED_900),
                ft.Row([p_id, p_name, p_loc, p_prog, p_phase, p_desc, p_img], wrap=True),
                ft.ElevatedButton("إضافة مشروع حالي", on_click=add_curr_proj),
                ft.Divider(),

                ft.Text("4. تعديل نسبة إنجاز مشروع قائم (Update)", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.INDIGO_900),
                ft.Row([up_pid, up_prog, up_phase], wrap=True),
                ft.ElevatedButton("تحديث نسبة الإنجاز والمرحلة", on_click=update_proj_progress, bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE),
                ft.Divider(),

                ft.Text("5. يوميات الموقع بالصور (Timeline)", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.INDIGO_900),
                ft.Row([tl_pid, tl_date, tl_title, tl_img], wrap=True),
                ft.ElevatedButton("نشر تطور جديد بالصور", on_click=add_timeline_update, bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE),
                ft.Divider(),

                ft.Text("6. مشاريع مستقبلية", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.RED_900),
                ft.Row([fp_name, fp_date, fp_desc, fp_img], wrap=True),
                ft.ElevatedButton("إضافة مشروع مستقبلي", on_click=add_fut_proj),
                ft.Divider(),

                ft.Text("7. الخدمات", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.RED_900),
                ft.Row([s_title, s_details, s_img], wrap=True),
                ft.ElevatedButton("إضافة خدمة", on_click=add_srv),
                ft.Divider(),
            ])

        c_user = ft.TextField(label="اسم مستخدم العميل", width=200)
        c_pass = ft.TextField(label="كلمة المرور", width=200)
        c_pid = ft.TextField(label="كود المشروع", width=180)
        c_total = ft.TextField(label="إجمالي قيمة الوحدة (ج.م)", width=220)
        c_paid = ft.TextField(label="إجمالي المدفوع (ج.م)", width=220)
        c_contract = ft.TextField(label="رابط ملف العقد (PDF/صورة)", width=300)
        c_drawings = ft.TextField(label="رابط الرسومات الهندسية 2D/3D", width=300)

        def add_cli(e):
            try:
                supabase.table("clients").insert({
                    "username": c_user.value.strip(),
                    "password": c_pass.value.strip(),
                    "project_id": c_pid.value.strip(),
                    "total_price": c_total.value.strip() or "0",
                    "paid_amount": c_paid.value.strip() or "0",
                    "contract_url": c_contract.value.strip(),
                    "drawings_url": c_drawings.value.strip()
                }).execute()
                show_snack("تم إنشاء حساب العميل وربط العقود والرسومات!")
                c_user.value = c_pass.value = c_pid.value = c_total.value = c_paid.value = c_contract.value = c_drawings.value = ""
                page.update()
            except Exception as ex:
                show_snack(f"خطأ: {ex}", ft.colors.RED)

        ins_user = ft.TextField(label="اسم مستخدم العميل", width=200)
        ins_amount = ft.TextField(label="قيمة القسط (ج.م)", width=200)
        ins_date = ft.TextField(label="تاريخ الاستحقاق (مثال: 2026-12-01)", width=250)
        ins_status = ft.TextField(label="الحالة (اكتب: مستحق أو مدفوع)", value="مستحق", width=220)

        def add_installment(e):
            try:
                supabase.table("installments").insert({
                    "username": ins_user.value.strip(),
                    "amount": ins_amount.value.strip(),
                    "due_date": ins_date.value.strip(),
                    "status": ins_status.value.strip() or "مستحق"
                }).execute()
                show_snack("تم تسجيل القسط للعميل بنجاح!")
                ins_amount.value = ins_date.value = ""
                page.update()
            except Exception as ex:
                show_snack(f"خطأ: {ex}", ft.colors.RED)

        del_c_user = ft.TextField(label="اسم مستخدم العميل المراد حذفه", width=280)
        def delete_cli(e):
            try:
                res = supabase.table("clients").delete().eq("username", del_c_user.value.strip()).execute()
                if res.data:
                    show_snack("تم حذف العميل بنجاح!")
                else:
                    show_snack("لم يتم العثور على العميل!", ft.colors.RED)
                del_c_user.value = ""
                page.update()
            except Exception as ex:
                show_snack(f"خطأ: {ex}", ft.colors.RED)

        controls_list.extend([
            ft.Text("إدارة حسابات العملاء والعقود والرسومات", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.TEAL_900),
            ft.Row([c_user, c_pass, c_pid, c_total, c_paid], wrap=True),
            ft.Row([c_contract, c_drawings], wrap=True),
            ft.ElevatedButton("إنشاء حساب عميل متكامل", on_click=add_cli, bgcolor=ft.colors.TEAL_800, color=ft.colors.WHITE),
            ft.Divider(),

            ft.Text("جدولة الأقساط والدفعات المالية للعملاء", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.TEAL_900),
            ft.Row([ins_user, ins_amount, ins_date, ins_status], wrap=True),
            ft.ElevatedButton("إضافة دفعة / قسط للعميل", on_click=add_installment, bgcolor=ft.colors.TEAL_800, color=ft.colors.WHITE),
            ft.Divider(),

            ft.Text("حذف حساب عميل", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.RED_900),
            ft.Row([del_c_user], wrap=True),
            ft.ElevatedButton("حذف العميل", on_click=delete_cli, bgcolor=ft.colors.RED_700, color=ft.colors.WHITE),
            ft.Divider(),
        ])

        controls_list.append(ft.Text("طلبات المعاينة وتسعير التشطيبات الواردة", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.INDIGO_900))
        try:
            reqs = supabase.table("service_requests").select("*").execute().data
            if not reqs:
                controls_list.append(ft.Text("لا توجد طلبات معاينة حالياً.", color=ft.colors.GREY_700))
            else:
                for rq in reqs:
                    controls_list.append(
                        ft.Card(
                            margin=ft.margin.only(bottom=8),
                            content=ft.ListTile(
                                leading=ft.Icon(ft.icons.PHONE, color=ft.colors.GREEN_700),
                                title=ft.Text(f"العميل: {rq.get('client_name', '')} | هاتف: {rq.get('phone', '')}", weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(f"الخدمة: {rq.get('service_type', '')} | المساحة: {rq.get('area', '')} م²\nملاحظات: {rq.get('notes', '')}")
                            )
                        )
                    )
        except Exception:
            controls_list.append(ft.Text("تأكد من تشغيل كود SQL لجدول service_requests", color=ft.colors.RED))

        if role == "admin":
            new_admin_pass = ft.TextField(label="باسورد الإدارة العليا الجديد", width=250, password=True, can_reveal_password=True)
            new_cs_pass = ft.TextField(label="باسورد خدمة العملاء الجديد", width=250, password=True, can_reveal_password=True)
            def change_passwords(e):
                try:
                    upd = {}
                    if new_admin_pass.value.strip():
                        upd["password"] = new_admin_pass.value.strip()
                    if new_cs_pass.value.strip():
                        upd["cs_password"] = new_cs_pass.value.strip()
                    if upd:
                        supabase.table("admin_auth").update(upd).eq("id", 1).execute()
                        show_snack("تم تحديث كلمات المرور بنجاح!")
                        new_admin_pass.value = new_cs_pass.value = ""
                        page.update()
                except Exception as ex:
                    show_snack(f"خطأ: {ex}", ft.colors.RED)

            controls_list.extend([
                ft.Divider(),
                ft.Text("إعدادات الأمان وصلاحيات الدخول", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.RED_900),
                ft.Row([new_admin_pass, new_cs_pass], wrap=True),
                ft.ElevatedButton("تحديث كلمات المرور", on_click=change_passwords, bgcolor=ft.colors.RED_700, color=ft.colors.WHITE),
            ])

        controls_list.append(ft.Container(height=40))
        page.add(ft.Container(padding=20, content=ft.Column(controls_list)))
        page.update()

    def show_admin_login_dialog(e):
        pass_field = ft.TextField(label="كلمة المرور (أدمن أو خدمة عملاء)", password=True, can_reveal_password=True, width=300)
        err = ft.Text("", color=ft.colors.RED)

        def verify(e):
            err.value = "جاري التحقق..."
            page.update()
            try:
                res = supabase.table("admin_auth").select("*").eq("id", 1).execute()
                row = res.data[0] if res.data else {}
                admin_pass = row.get("password", "admin123")
                cs_pass = row.get("cs_password", "cs123")
            except Exception:
                admin_pass = "admin123"
                cs_pass = "cs123"

            entered = pass_field.value.strip()
            if entered == admin_pass:
                close_dlg(dlg)
                load_admin_panel(role="admin")
            elif entered == cs_pass:
                close_dlg(dlg)
                load_admin_panel(role="cs")
            else:
                err.value = "كلمة المرور غير صحيحة!"
                page.update()

        dlg = ft.AlertDialog(
            title=ft.Text("دخول الإدارة / خدمة العملاء"),
            content=ft.Column([pass_field, err], tight=True),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda _: close_dlg(dlg)),
                ft.ElevatedButton("دخول", on_click=verify)
            ]
        )
        open_dlg(dlg)

    # ==========================================
    # --- قسم لوحة متابعة المشترك (Client Dashboard) ---
    # ==========================================
    def show_project_dashboard(project, client_row):
        show_loading("لوحة متابعة المشترك")
        progress_percent = int(project.get('progress', 0) * 100)
        username = client_row.get('username', '')
        project_id = project.get('project_id', '')

        try:
            installments = supabase.table("installments").select("*").eq("username", username).execute().data
        except Exception:
            installments = []

        try:
            timeline = supabase.table("project_updates").select("*").eq("project_id", project_id).execute().data
        except Exception:
            timeline = []

        page.clean()
        page.appbar = ft.AppBar(title=ft.Text(f"مرحباً، {username}"), bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE)

        dash_items = [
            ft.Text(project.get('name', ''), size=22, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900),
            ft.Text(f"الموقع: {project.get('location', '')} | كود المشروع: {project_id}", color=ft.colors.GREY_700),
            ft.Divider(height=20),

            ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Row([
                            ft.Text("نسبة الإنجاز الهندسي", weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"{progress_percent}%", weight=ft.FontWeight.BOLD, size=20, color=ft.colors.INDIGO_900)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(height=10),
                        ft.ProgressBar(value=project.get('progress', 0), color=ft.colors.GREEN_700, bgcolor=ft.colors.GREY_300, height=12),
                        ft.Container(height=12),
                        ft.Text(f"المرحلة الحالية: {project.get('phase', '')}", size=15, weight=ft.FontWeight.BOLD),
                    ])
                )
            ),
            ft.Container(height=10),

            ft.Text("العقود والرسومات الهندسية", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900),
            ft.Row([
                ft.ElevatedButton(
                    "استعراض العقد",
                    icon=ft.icons.DESCRIPTION,
                    bgcolor=ft.colors.INDIGO_800,
                    color=ft.colors.WHITE,
                    on_click=lambda _: open_external_link(client_row.get("contract_url", ""))
                ),
                ft.ElevatedButton(
                    "الرسومات 2D / 3D",
                    icon=ft.icons.ARCHITECTURE,
                    bgcolor=ft.colors.TEAL_700,
                    color=ft.colors.WHITE,
                    on_click=lambda _: open_external_link(client_row.get("drawings_url", ""))
                ),
            ], wrap=True),
            ft.Divider(height=25),

            ft.Text("الموقف المالي وجدول الأقساط", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900),
            ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=15,
                    content=ft.Row([
                        ft.Column([
                            ft.Text("إجمالي قيمة الوحدة", size=13, color=ft.colors.GREY_700),
                            ft.Text(f"{client_row.get('total_price', '0')} ج.م", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.INDIGO_900),
                        ]),
                        ft.Column([
                            ft.Text("إجمالي المدفوع", size=13, color=ft.colors.GREY_700),
                            ft.Text(f"{client_row.get('paid_amount', '0')} ج.م", weight=ft.FontWeight.BOLD, size=16, color=ft.colors.GREEN_700),
                        ]),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
                )
            ),
        ]

        if not installments:
            dash_items.append(ft.Text("لا توجد أقساط مسجلة حالياً.", color=ft.colors.GREY_700))
        else:
            for ins in installments:
                is_paid = "مدفوع" in ins.get("status", "")
                dash_items.append(
                    ft.Card(
                        margin=ft.margin.only(bottom=6),
                        content=ft.ListTile(
                            leading=ft.Icon(
                                ft.icons.CHECK_CIRCLE if is_paid else ft.icons.SCHEDULE,
                                color=ft.colors.GREEN_700 if is_paid else ft.colors.ORANGE_800
                            ),
                            title=ft.Text(f"قيمة القسط: {ins.get('amount', '')} ج.م", weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(f"تاريخ الاستحقاق: {ins.get('due_date', '')} | الحالة: {ins.get('status', '')}")
                        )
                    )
                )

        dash_items.append(ft.Divider(height=25))

        dash_items.append(ft.Text("يوميات الموقع وتطورات التنفيذ", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900))
        if not timeline:
            dash_items.append(ft.Text("سيتم رفع صور تطورات المراحل قريباً.", color=ft.colors.GREY_700))
        else:
            for up in timeline:
                up_img = up.get("image_url", "")
                dash_items.append(
                    ft.Card(
                        margin=ft.margin.only(bottom=12),
                        elevation=2,
                        content=ft.Column([
                            ft.Image(src=up_img, width=350, height=180, fit=ft.ImageFit.COVER) if up_img else ft.Container(),
                            ft.ListTile(
                                leading=ft.Icon(ft.icons.HISTORY, color=ft.colors.INDIGO_900),
                                title=ft.Text(up.get("title", ""), weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(f"التاريخ: {up.get('update_date', '')}")
                            )
                        ])
                    )
                )

        dash_items.extend([
            ft.Container(height=20),
            ft.ElevatedButton("تسجيل خروج والعودة", on_click=lambda _: go_to_main_hub(None), width=350, bgcolor=ft.colors.RED_700, color=ft.colors.WHITE),
            ft.Container(height=30)
        ])

        page.add(ft.Container(padding=20, content=ft.Column(dash_items)))
        page.update()

    def open_login_dialog(project):
        user_field = ft.TextField(label="اسم المستخدم", icon=ft.icons.PERSON)
        pass_field = ft.TextField(label="كلمة المرور", password=True, can_reveal_password=True, icon=ft.icons.LOCK)
        error_text = ft.Text("", color=ft.colors.RED)

        def verify_login(e):
            error_text.value = "جاري التحقق..."
            page.update()
            try:
                res = supabase.table("clients").select("*").eq("username", user_field.value.strip()).eq("password", pass_field.value.strip()).eq("project_id", project['project_id']).execute()
                if res.data and len(res.data) > 0:
                    close_dlg(dlg)
                    show_project_dashboard(project, res.data[0])
                else:
                    error_text.value = "البيانات غير صحيحة"
                    page.update()
            except Exception as ex:
                error_text.value = f"خطأ في الاتصال: {ex}"
                page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(f"دخول المشترك - {project.get('name', '')}", size=16),
            content=ft.Column([user_field, pass_field, error_text], tight=True),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda _: close_dlg(dlg)),
                ft.ElevatedButton("دخول", on_click=verify_login, bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE)
            ],
        )
        open_dlg(dlg)

    def load_cost_calculator(e):
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text("حاسبة تكلفة التشطيبات"), bgcolor=ft.colors.TEAL_800, color=ft.colors.WHITE)

        area_field = ft.TextField(label="مساحة الوحدة بالمتر المربع (مثال: 150)", width=300)
        result_text = ft.Text("أدخل المساحة واختر باقة التشطيب لحساب التكلفة التقريبية", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900)

        def calc_cost(rate, level_name):
            try:
                area = float(area_field.value.strip())
                min_cost = int(area * rate * 0.9)
                max_cost = int(area * rate * 1.1)
                result_text.value = f"باقة ({level_name}) لمساحة {int(area)} م²:\nالتكلفة التقديرية من {min_cost:,} إلى {max_cost:,} ج.م"
                page.update()
            except Exception:
                result_text.value = "يرجى إدخال رقم صحيح في خانة المساحة أولاً!"
                page.update()

        page.add(
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Icon(ft.icons.CALCULATE, size=70, color=ft.colors.TEAL_800),
                    ft.Text("احسب التكلفة المبدئية لتشطيب وحدتك", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    area_field,
                    ft.Text("اختر مستوى التشطيب المطلوب:", weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton("تشطيب لوكس", on_click=lambda _: calc_cost(4500, "لوكس"), bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE),
                        ft.ElevatedButton("سوبر لوكس", on_click=lambda _: calc_cost(6500, "سوبر لوكس"), bgcolor=ft.colors.TEAL_700, color=ft.colors.WHITE),
                        ft.ElevatedButton("ألترا لوكس", on_click=lambda _: calc_cost(9000, "ألترا لوكس"), bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE),
                    ], wrap=True, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=15),
                    ft.Card(
                        elevation=3,
                        content=ft.Container(padding=20, content=result_text)
                    ),
                    ft.Container(height=15),
                    ft.ElevatedButton("اطلب معاينة رسمية الآن", icon=ft.icons.SEND, on_click=load_request_form, bgcolor=ft.colors.ORANGE_800, color=ft.colors.WHITE, width=300),
                    ft.Container(height=10),
                    ft.ElevatedButton("رجوع للقائمة", on_click=go_to_main_hub)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        )
        page.update()

    def load_request_form(e):
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text("طلب معاينة أو تسعير"), bgcolor=ft.colors.ORANGE_800, color=ft.colors.WHITE)

        r_name = ft.TextField(label="الاسم بالكامل", width=320, icon=ft.icons.PERSON)
        r_phone = ft.TextField(label="رقم الهاتف / واتساب", width=320, icon=ft.icons.PHONE)
        r_area = ft.TextField(label="مساحة الشقة / الوحدة (م²)", width=320)
        r_type = ft.TextField(label="نوع الخدمة (تشطيب متكامل / تصميم 3D / إشراف)", width=320)
        r_notes = ft.TextField(label="عنوان الوحدة أو ملاحظات إضافية", width=320, multiline=True)

        def submit_req(e):
            if not r_name.value.strip() or not r_phone.value.strip():
                show_snack("يرجى كتابة الاسم ورقم الهاتف!", ft.colors.RED)
                return
            try:
                supabase.table("service_requests").insert({
                    "client_name": r_name.value.strip(),
                    "phone": r_phone.value.strip(),
                    "area": r_area.value.strip(),
                    "service_type": r_type.value.strip(),
                    "notes": r_notes.value.strip()
                }).execute()
                show_snack("تم إرسال طلبك بنجاح! سيتواصل معك فريق خدمة العملاء قريباً.")
                r_name.value = r_phone.value = r_area.value = r_type.value = r_notes.value = ""
                page.update()
            except Exception as ex:
                show_snack(f"حدث خطأ: {ex}", ft.colors.RED)

        page.add(
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text("سجل بياناتك ليتواصل معك مهندسو Keyan-East", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900),
                    r_name, r_phone, r_area, r_type, r_notes,
                    ft.Container(height=10),
                    ft.ElevatedButton("إرسال الطلب", icon=ft.icons.SEND, on_click=submit_req, bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE, width=320),
                    ft.Container(height=10),
                    ft.ElevatedButton("رجوع للقائمة", on_click=go_to_main_hub)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        )
        page.update()

    def load_current_projects(e):
        show_loading("المشاريع الحالية")
        try:
            res = supabase.table("projects").select("*").execute()
            projects = res.data
            page.clean()
            page.appbar = ft.AppBar(title=ft.Text("المشاريع الحالية"), bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE)
            if not projects:
                page.add(ft.Text("لا توجد مشاريع مضافة حالياً.", size=16, color=ft.colors.GREY_700))
            else:
                for prj in projects:
                    img_url = prj.get('image_url', '')
                    page.add(
                        ft.Card(
                            margin=ft.margin.only(bottom=15, left=15, right=15),
                            elevation=3,
                            content=ft.Column([
                                ft.Image(src=img_url, width=350, height=200, fit=ft.ImageFit.COVER) if img_url else ft.Container(height=10),
                                ft.Container(
                                    padding=15,
                                    content=ft.Column([
                                        ft.Text(prj.get('name', ''), weight=ft.FontWeight.BOLD, size=18, color=ft.colors.INDIGO_900),
                                        ft.Text(f"الموقع: {prj.get('location', '')}", color=ft.colors.GREY_700),
                                        ft.Text(prj.get('description', ''), size=14),
                                        ft.Container(height=10),
                                        ft.ElevatedButton("دخول المشترك (الأقساط والعقود والإنجاز)", on_click=lambda e, p=prj: open_login_dialog(p), bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE, width=350)
                                    ])
                                )
                            ])
                        )
                    )
            page.add(ft.ElevatedButton("رجوع للقائمة", on_click=go_to_main_hub))
            page.update()
        except Exception as ex:
            page.clean()
            page.add(ft.Text(f"حدث خطأ: {ex}", color=ft.colors.RED))
            page.update()

    def load_future_projects(e):
        show_loading("المشاريع المستقبلية")
        try:
            res = supabase.table("future_projects").select("*").execute()
            projects = res.data
            page.clean()
            page.appbar = ft.AppBar(title=ft.Text("المشاريع المستقبلية"), bgcolor=ft.colors.GREEN_800, color=ft.colors.WHITE)
            if not projects:
                page.add(ft.Text("ترقبوا مشاريعنا القادمة قريباً.", size=16, color=ft.colors.GREY_700))
            else:
                for prj in projects:
                    img_url = prj.get('image_url', '')
                    page.add(
                        ft.Card(
                            margin=ft.margin.only(bottom=15, left=15, right=15),
                            content=ft.Column([
                                ft.Image(src=img_url, width=350, height=180, fit=ft.ImageFit.COVER) if img_url else ft.Container(),
                                ft.ListTile(
                                    title=ft.Text(prj.get('name', ''), weight=ft.FontWeight.BOLD, size=18),
                                    subtitle=ft.Text(f"موعد الطرح: {prj.get('date', '')}\n\n{prj.get('description', '')}")
                                )
                            ])
                        )
                    )
            page.add(ft.ElevatedButton("رجوع للقائمة", on_click=go_to_main_hub))
            page.update()
        except Exception as ex:
            page.clean()
            page.add(ft.Text(f"حدث خطأ: {ex}", color=ft.colors.RED))
            page.update()

    def load_services(e):
        show_loading("خدمات الشركة")
        try:
            res = supabase.table("services").select("*").execute()
            services = res.data
            page.clean()
            page.appbar = ft.AppBar(title=ft.Text("خدمات الشركة"), bgcolor=ft.colors.BROWN_700, color=ft.colors.WHITE)
            if not services:
                page.add(ft.Text("لا توجد خدمات مضافة حالياً.", size=16))
            else:
                for srv in services:
                    img_url = srv.get('image_url', '')
                    page.add(
                        ft.Card(
                            margin=ft.margin.only(bottom=15, left=15, right=15),
                            elevation=3,
                            content=ft.Column([
                                ft.Image(src=img_url, width=350, height=180, fit=ft.ImageFit.COVER) if img_url else ft.Container(),
                                ft.ListTile(
                                    leading=ft.Icon(ft.icons.DESIGN_SERVICES, color=ft.colors.BROWN_700, size=35),
                                    title=ft.Text(srv.get('title', ''), weight=ft.FontWeight.BOLD, size=18),
                                    subtitle=ft.Text(srv.get('details', '')),
                                )
                            ])
                        )
                    )
            page.add(
                ft.Container(height=10),
                ft.ElevatedButton("اطلب معاينة أو تسعير تشطيب", icon=ft.icons.SEND, on_click=load_request_form, bgcolor=ft.colors.ORANGE_800, color=ft.colors.WHITE, width=300),
                ft.Container(height=10),
                ft.ElevatedButton("رجوع للقائمة", on_click=go_to_main_hub)
            )
            page.update()
        except Exception as ex:
            page.clean()
            page.add(ft.Text(f"حدث خطأ: {ex}", color=ft.colors.RED))
            page.update()

    def go_to_main_hub(e):
        page.clean()
        page.appbar = ft.AppBar(title=ft.Text("أقسام شركة Keyan-East"), bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE)
        page.add(
            ft.Container(height=10),
            ft.ListTile(
                leading=ft.Icon(ft.icons.ENGINEERING, color=ft.colors.INDIGO_900, size=40),
                title=ft.Text("المشاريع الحالية ومتابعة المشتركين", weight=ft.FontWeight.BOLD, size=18),
                subtitle=ft.Text("نسب الإنجاز • الأقساط • العقود • يوميات الموقع"),
                on_click=load_current_projects
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.icons.LOCATION_CITY, color=ft.colors.GREEN_700, size=40),
                title=ft.Text("المشاريع المستقبلية", weight=ft.FontWeight.BOLD, size=18),
                subtitle=ft.Text("أحدث الطروحات والفرص الاستثمارية"),
                on_click=load_future_projects
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.icons.DESIGN_SERVICES, color=ft.colors.BROWN_700, size=40),
                title=ft.Text("خدمات الشركة", weight=ft.FontWeight.BOLD, size=18),
                subtitle=ft.Text("التشطيبات • الرسومات الهندسية 2D/3D • الإشراف"),
                on_click=load_services
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.icons.CALCULATE, color=ft.colors.TEAL_700, size=40),
                title=ft.Text("حاسبة تكلفة التشطيبات", weight=ft.FontWeight.BOLD, size=18),
                subtitle=ft.Text("احسب التكلفة التقريبية لتشطيب وحدتك فوراً"),
                on_click=load_cost_calculator
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.icons.SEND, color=ft.colors.ORANGE_800, size=40),
                title=ft.Text("اطلب معاينة أو عرض سعر", weight=ft.FontWeight.BOLD, size=18),
                subtitle=ft.Text("سجل بياناتك ليتواصل معك فريقنا الهندسي"),
                on_click=load_request_form
            ),
            ft.Container(height=25),
            ft.ElevatedButton("رجوع للشاشة الرئيسية", on_click=lambda _: load_intro_screen())
        )
        page.update()

    def load_intro_screen():
        show_loading("Keyan-East")
        try:
            company_res = supabase.table("company_info").select("*").order("id", desc=True).limit(1).execute()
            company_data = company_res.data[0] if company_res.data else {}
            founders_res = supabase.table("founders").select("*").execute()
            founders_data = founders_res.data

            page.clean()
            page.appbar = ft.AppBar(
                title=ft.Text(""),
                actions=[
                    ft.IconButton(ft.icons.LOCK, on_click=show_admin_login_dialog, tooltip="لوحة الإدارة وخدمة العملاء")
                ]
            )

            announcement = company_data.get("announcement", "")
            if announcement:
                page.add(
                    ft.Container(
                        bgcolor=ft.colors.AMBER_100,
                        padding=12,
                        margin=ft.margin.symmetric(horizontal=15, vertical=5),
                        content=ft.Row([
                            ft.Icon(ft.icons.CAMPAIGN, color=ft.colors.ORANGE_900),
                            ft.Text(announcement, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_900, size=14)
                        ], wrap=True)
                    )
                )

            logo_url = company_data.get("logo_url", "")
            if logo_url:
                page.add(ft.Container(height=10), ft.Image(src=logo_url, width=220, height=220, fit=ft.ImageFit.CONTAIN))
            else:
                page.add(ft.Container(height=10), ft.Icon(ft.icons.APARTMENT, size=110, color=ft.colors.INDIGO_900))

            page.add(
                ft.Text("Keyan-East", size=34, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900),
                ft.Text("للاستثمار والتطوير الهندسي", size=18, color=ft.colors.GREY_700),
                ft.Container(height=10)
            )

            about_text = company_data.get("about_text", "شركة رائدة في المقاولات والتشطيبات الهندسية.")
            page.add(
                ft.Card(
                    elevation=2,
                    margin=ft.margin.symmetric(horizontal=15),
                    content=ft.Container(
                        padding=20,
                        content=ft.Column([
                            ft.Text("من نحن", weight=ft.FontWeight.BOLD, size=20, color=ft.colors.INDIGO_900),
                            ft.Text(about_text, size=15)
                        ])
                    )
                )
            )

            if founders_data:
                page.add(ft.Container(height=10), ft.Text("المؤسسون ومجلس الإدارة", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900))
                for founder in founders_data:
                    page.add(
                        ft.Card(
                            margin=ft.margin.symmetric(horizontal=15, vertical=5),
                            content=ft.ListTile(
                                leading=ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON, color=ft.colors.WHITE), bgcolor=ft.colors.INDIGO_900),
                                title=ft.Text(founder.get('name', ''), weight=ft.FontWeight.BOLD),
                                subtitle=ft.Text(f"{founder.get('role', '')}\n{founder.get('bio', '')}")
                            )
                        )
                    )

            wa_url = company_data.get("whatsapp", "")
            maps_url = company_data.get("maps_url", "")
            if wa_url or maps_url:
                page.add(
                    ft.Container(height=10),
                    ft.Row([
                        ft.ElevatedButton("تواصل عبر واتساب", icon=ft.icons.PHONE, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE, on_click=lambda _: open_external_link(wa_url)) if wa_url else ft.Container(),
                        ft.ElevatedButton("موقعنا على الخريطة", icon=ft.icons.MAP, bgcolor=ft.colors.BLUE_800, color=ft.colors.WHITE, on_click=lambda _: open_external_link(maps_url)) if maps_url else ft.Container(),
                    ], alignment=ft.MainAxisAlignment.CENTER, wrap=True)
                )

            page.add(
                ft.Container(height=15),
                ft.ElevatedButton(
                    "استكشف مشاريعنا وخدماتنا",
                    icon=ft.icons.EXPLORE,
                    bgcolor=ft.colors.INDIGO_900,
                    color=ft.colors.WHITE,
                    on_click=go_to_main_hub,
                    height=55,
                    width=300
                ),
                ft.Container(height=40)
            )
            page.update()
        except Exception as ex:
            page.clean()
            page.add(ft.Text(f"حدث خطأ: {ex}", color=ft.colors.RED))
            page.update()

    load_intro_screen()

if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
