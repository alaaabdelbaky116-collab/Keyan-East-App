import flet as ft
from supabase import create_client, Client

# ضع الـ URL والـ Key الخاص بمشروعك هنا
SUPABASE_URL = 'https://paarkycuhrljagdiqkdo.supabase.co'
SUPABASE_KEY = 'sb_secret_JukbE8tqqpQ6ZINV1PMlYA_mG8oNJRk'
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    page.title = "Keyan-East App"
    page.rtl = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    def show_snack(msg, color=ft.colors.GREEN):
        page.overlay.append(ft.SnackBar(ft.Text(msg), bgcolor=color, open=True))
        page.update()

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
    # --- قسم الإدارة (Admin Panel) المدمج ---
    # ==========================================
    def load_admin_panel():
        page.clean()
        page.appbar = ft.AppBar(
            title=ft.Text("لوحة تحكم الإدارة (Keyan-East)"), 
            bgcolor=ft.colors.RED_900, 
            color=ft.colors.WHITE,
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda _: load_intro_screen(), icon_color=ft.colors.WHITE)
        )

        # 1. إعدادات الشركة
        logo_url_field = ft.TextField(label="رابط اللوجو", width=600)
        about_text_field = ft.TextField(label="وصف الشركة", multiline=True, width=600)
        def update_company(e):
            try:
                supabase.table("company_info").insert({"logo_url": logo_url_field.value, "about_text": about_text_field.value}).execute()
                show_snack("تم تحديث بيانات الشركة!")
                logo_url_field.value = about_text_field.value = ""
                page.update()
            except Exception as ex: show_snack(f"خطأ: {ex}", ft.colors.RED)

        # 2. المؤسسين
        f_name_field = ft.TextField(label="اسم المؤسس", width=300)
        f_role_field = ft.TextField(label="المسمى الوظيفي", width=300)
        f_bio_field = ft.TextField(label="نبذة تعريفية", width=600, multiline=True)
        def add_founder(e):
            try:
                supabase.table("founders").insert({"name": f_name_field.value, "role": f_role_field.value, "bio": f_bio_field.value}).execute()
                show_snack("تم إضافة المؤسس!")
                f_name_field.value = f_role_field.value = f_bio_field.value = ""
                page.update()
            except Exception as ex: show_snack(f"خطأ: {ex}", ft.colors.RED)

        # 3. مشاريع حالية
        p_id = ft.TextField(label="كود المشروع", width=200)
        p_name = ft.TextField(label="اسم المشروع", width=200)
        p_loc = ft.TextField(label="الموقع", width=180)
        p_prog = ft.TextField(label="نسبة الإنجاز (مثال: 75)", width=200)
        p_phase = ft.TextField(label="المرحلة الحالية", width=200)
        p_desc = ft.TextField(label="وصف مبسط", width=300, multiline=True)
        p_img = ft.TextField(label="رابط الصورة", width=300)
        def add_curr_proj(e):
            try:
                supabase.table("projects").insert({
                    "project_id": p_id.value, "name": p_name.value, "location": p_loc.value,
                    "progress": float(p_prog.value)/100, "phase": p_phase.value,
                    "description": p_desc.value, "image_url": p_img.value
                }).execute()
                show_snack("تم إضافة المشروع الحالي!")
                page.update()
            except Exception as ex: show_snack(f"خطأ: {ex}", ft.colors.RED)

        # 4. مشاريع مستقبلية
        fp_name = ft.TextField(label="اسم المشروع", width=300)
        fp_date = ft.TextField(label="موعد الطرح", width=300)
        fp_desc = ft.TextField(label="التفاصيل", width=300, multiline=True)
        fp_img = ft.TextField(label="رابط الصورة", width=300)
        def add_fut_proj(e):
            try:
                supabase.table("future_projects").insert({"name": fp_name.value, "date": fp_date.value, "description": fp_desc.value, "image_url": fp_img.value}).execute()
                show_snack("تم إضافة المشروع المستقبلي!")
                page.update()
            except Exception as ex: show_snack(f"خطأ: {ex}", ft.colors.RED)

        # 5. خدمات
        s_title = ft.TextField(label="اسم الخدمة", width=300)
        s_details = ft.TextField(label="تفاصيل الخدمة", width=300, multiline=True)
        def add_srv(e):
            try:
                supabase.table("services").insert({"title": s_title.value, "details": s_details.value}).execute()
                show_snack("تم إضافة الخدمة!")
                page.update()
            except Exception as ex: show_snack(f"خطأ: {ex}", ft.colors.RED)

        # 6. عملاء
        c_user = ft.TextField(label="اسم المستخدم", width=200)
        c_pass = ft.TextField(label="كلمة المرور", width=200)
        c_pid = ft.TextField(label="كود المشروع", width=200)
        def add_cli(e):
            try:
                supabase.table("clients").insert({"username": c_user.value, "password": c_pass.value, "project_id": c_pid.value}).execute()
                show_snack("تم إنشاء حساب العميل!")
                c_user.value = c_pass.value = c_pid.value = ""
                page.update()
            except Exception as ex: show_snack(f"خطأ: {ex}", ft.colors.RED)

        # 7. حذف عميل
        del_c_user = ft.TextField(label="اسم مستخدم العميل المراد حذفه", width=300)
        def delete_cli(e):
            try:
                res = supabase.table("clients").delete().eq("username", del_c_user.value.strip()).execute()
                if res.data:
                    show_snack("تم حذف العميل بنجاح!")
                else:
                    show_snack("لم يتم العثور على العميل!", ft.colors.RED)
                del_c_user.value = ""
                page.update()
            except Exception as ex: show_snack(f"خطأ: {ex}", ft.colors.RED)

        # 8. تغيير باسورد الإدارة
        new_admin_pass = ft.TextField(label="الباسورد الجديد للإدارة", width=300, password=True, can_reveal_password=True)
        def change_admin_pass(e):
            try:
                supabase.table("admin_auth").update({"password": new_admin_pass.value.strip()}).eq("id", 1).execute()
                show_snack("تم تغيير باسورد الإدارة بنجاح!")
                new_admin_pass.value = ""
                page.update()
            except Exception as ex: show_snack(f"خطأ: {ex}", ft.colors.RED)

        page.add(
            ft.Container(padding=20, content=ft.Column([
                ft.Text("1. إعدادات الشركة", weight=ft.FontWeight.BOLD, color=ft.colors.RED_900),
                ft.Row([logo_url_field, about_text_field], wrap=True),
                ft.ElevatedButton("حفظ بيانات الشركة", on_click=update_company),
                ft.Divider(),
                
                ft.Text("2. المؤسسون", weight=ft.FontWeight.BOLD, color=ft.colors.RED_900),
                ft.Row([f_name_field, f_role_field, f_bio_field], wrap=True),
                ft.ElevatedButton("إضافة مؤسس", on_click=add_founder),
                ft.Divider(),
                
                ft.Text("3. مشاريع حالية", weight=ft.FontWeight.BOLD, color=ft.colors.RED_900),
                ft.Row([p_id, p_name, p_loc, p_prog, p_phase], wrap=True),
                ft.Row([p_desc, p_img], wrap=True),
                ft.ElevatedButton("إضافة مشروع حالي", on_click=add_curr_proj),
                ft.Divider(),
                
                ft.Text("4. مشاريع مستقبلية", weight=ft.FontWeight.BOLD, color=ft.colors.RED_900),
                ft.Row([fp_name, fp_date, fp_desc, fp_img], wrap=True),
                ft.ElevatedButton("إضافة مستقبلي", on_click=add_fut_proj),
                ft.Divider(),
                
                ft.Text("5. الخدمات", weight=ft.FontWeight.BOLD, color=ft.colors.RED_900),
                ft.Row([s_title, s_details], wrap=True),
                ft.ElevatedButton("إضافة خدمة", on_click=add_srv),
                ft.Divider(),
                
                ft.Text("6. حسابات العملاء", weight=ft.FontWeight.BOLD, color=ft.colors.RED_900),
                ft.Row([c_user, c_pass, c_pid], wrap=True),
                ft.ElevatedButton("إنشاء حساب عميل", on_click=add_cli),
                ft.Divider(),

                ft.Text("7. حذف حساب عميل", weight=ft.FontWeight.BOLD, color=ft.colors.RED_900),
                ft.Row([del_c_user], wrap=True),
                ft.ElevatedButton("حذف العميل", on_click=delete_cli, bgcolor=ft.colors.RED_700, color=ft.colors.WHITE),
                ft.Divider(),

                ft.Text("8. إعدادات الأمان (الإدارة)", weight=ft.FontWeight.BOLD, color=ft.colors.RED_900),
                ft.Row([new_admin_pass], wrap=True),
                ft.ElevatedButton("تغيير باسورد الإدارة", on_click=change_admin_pass, bgcolor=ft.colors.RED_700, color=ft.colors.WHITE),
                ft.Container(height=40)
            ]))
        )
        page.update()

    def show_admin_login_dialog(e):
        pass_field = ft.TextField(label="كلمة مرور الإدارة", password=True, can_reveal_password=True, width=300)
        err = ft.Text("", color=ft.colors.RED)
        
        def verify(e):
            err.value = "جاري التحقق..."
            page.update()
            try:
                # جلب الباسورد من الداتا بيز
                res = supabase.table("admin_auth").select("password").eq("id", 1).execute()
                real_pass = res.data[0]["password"] if res.data else "admin123"
            except Exception:
                real_pass = "admin123" # الباسورد الافتراضي في حالة وجود خطأ

            if pass_field.value == real_pass:
                page.dialog.open = False
                load_admin_panel()
            else:
                err.value = "كلمة المرور غير صحيحة!"
                page.update()

        dlg = ft.AlertDialog(title=ft.Text("تسجيل دخول الإدارة"), content=ft.Column([pass_field, err], tight=True),
                             actions=[ft.ElevatedButton("دخول", on_click=verify)])
        page.dialog = dlg
        dlg.open = True
        page.update()

    # ==========================================
    # --- قسم تطبيق العملاء (User App) ---
    # ==========================================

    def show_project_dashboard(project):
        page.clean()
        progress_percent = int(project.get('progress', 0) * 100)
        page.appbar = ft.AppBar(title=ft.Text("لوحة متابعة المشترك"), bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE)
        page.add(
            ft.Container(
                padding=20,
                content=ft.Column([
                    ft.Text(project.get('name', ''), size=22, weight=ft.FontWeight.BOLD),
                    ft.Text(f"الموقع: {project.get('location', '')} | كود: {project.get('project_id', '')}", color=ft.colors.GREY_700),
                    ft.Divider(height=30),
                    ft.Card(
                        elevation=2,
                        content=ft.Container(
                            padding=20,
                            content=ft.Column([
                                ft.Row([ft.Text("نسبة الإنجاز الإجمالية", weight=ft.FontWeight.BOLD, size=16),
                                        ft.Text(f"{progress_percent}%", weight=ft.FontWeight.BOLD, size=20, color=ft.colors.INDIGO_900)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Container(height=10),
                                ft.ProgressBar(value=project.get('progress', 0), color=ft.colors.GREEN_700, bgcolor=ft.colors.GREY_300, height=12),
                                ft.Container(height=15),
                                ft.Text(f"المرحلة الحالية: {project.get('phase', '')}", size=15),
                            ])
                        )
                    ),
                    ft.Container(height=20),
                    ft.ElevatedButton("تسجيل خروج والعودة", on_click=lambda _: go_to_main_hub(None), width=float('inf'), bgcolor=ft.colors.RED_700, color=ft.colors.WHITE)
                ])
            )
        )
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
                    page.dialog.open = False
                    show_project_dashboard(project)
                else:
                    error_text.value = "البيانات غير صحيحة"
                    page.update()
            except Exception as ex:
                error_text.value = "خطأ في الاتصال"
                page.update()
        dlg = ft.AlertDialog(
            title=ft.Text(f"دخول - {project.get('name', '')}", size=16),
            content=ft.Column([user_field, pass_field, error_text], tight=True),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda _: setattr(page.dialog, 'open', False) or page.update()),
                ft.ElevatedButton("دخول", on_click=verify_login, bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE)
            ],
        )
        page.dialog = dlg
        dlg.open = True
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
                                ft.Image(src=img_url, width=float('inf'), height=200, fit=ft.ImageFit.COVER) if img_url else ft.Container(height=10),
                                ft.Container(
                                    padding=15,
                                    content=ft.Column([
                                        ft.Text(prj.get('name', ''), weight=ft.FontWeight.BOLD, size=18, color=ft.colors.INDIGO_900),
                                        ft.Text(f"الموقع: {prj.get('location', '')}", color=ft.colors.GREY_700),
                                        ft.Text(prj.get('description', ''), size=14),
                                        ft.Container(height=10),
                                        ft.ElevatedButton("دخول المشترك لمتابعة الإنجاز", on_click=lambda e, p=prj: open_login_dialog(p), bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE, width=float('inf'))
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
                                ft.Image(src=img_url, width=float('inf'), height=180, fit=ft.ImageFit.COVER) if img_url else ft.Container(),
                                ft.ListTile(title=ft.Text(prj.get('name', ''), weight=ft.FontWeight.BOLD, size=18),
                                            subtitle=ft.Text(f"موعد الطرح: {prj.get('date', '')}\n\n{prj.get('description', '')}"))
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
                    page.add(ft.Card(margin=ft.margin.only(bottom=10, left=15, right=15),
                                     content=ft.ListTile(leading=ft.Icon(ft.icons.DESIGN_SERVICES, color=ft.colors.BROWN_700, size=35),
                                                         title=ft.Text(srv.get('title', ''), weight=ft.FontWeight.BOLD),
                                                         subtitle=ft.Text(srv.get('details', '')))))
            page.add(ft.Container(height=10), ft.ElevatedButton("رجوع للقائمة", on_click=go_to_main_hub))
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
            ft.ListTile(leading=ft.Icon(ft.icons.ENGINEERING, color=ft.colors.INDIGO_900, size=40),
                        title=ft.Text("المشاريع الحالية", weight=ft.FontWeight.BOLD, size=18),
                        subtitle=ft.Text("متابعة المشاريع القائمة وصور التنفيذ"), on_click=load_current_projects),
            ft.Divider(),
            ft.ListTile(leading=ft.Icon(ft.icons.LOCATION_CITY, color=ft.colors.GREEN_700, size=40),
                        title=ft.Text("المشاريع المستقبلية", weight=ft.FontWeight.BOLD, size=18),
                        subtitle=ft.Text("أحدث الطروحات والفرص الاستثمارية"), on_click=load_future_projects),
            ft.Divider(),
            ft.ListTile(leading=ft.Icon(ft.icons.DESIGN_SERVICES, color=ft.colors.BROWN_700, size=40),
                        title=ft.Text("خدمات الشركة", weight=ft.FontWeight.BOLD, size=18),
                        subtitle=ft.Text("التشطيبات • الرسومات الهندسية • الإشراف"), on_click=load_services),
            ft.Container(height=30),
            ft.ElevatedButton("رجوع للشاشة الرئيسية", on_click=lambda _: load_intro_screen())
        )
        page.update()

    def load_intro_screen():
        show_loading("Keyan-East")
        try:
            company_res = supabase.table("company_info").select("*").limit(1).execute()
            company_data = company_res.data[0] if company_res.data else {}
            founders_res = supabase.table("founders").select("*").execute()
            founders_data = founders_res.data
            
            page.clean()
            page.appbar = ft.AppBar(
                title=ft.Text(""),
                actions=[
                    ft.IconButton(ft.icons.LOCK_PERSON, on_click=show_admin_login_dialog, tooltip="لوحة الإدارة")
                ]
            )
            
            logo_url = company_data.get("logo_url", "")
            if logo_url:
                # تم تكبير اللوجو هنا
                page.add(ft.Container(height=20), ft.Image(src=logo_url, width=250, height=250, fit=ft.ImageFit.CONTAIN))
            else:
                page.add(ft.Container(height=20), ft.Icon(ft.icons.APARTMENT, size=120, color=ft.colors.INDIGO_900))
                
            page.add(
                ft.Text("Keyan-East", size=36, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900),
                ft.Text("للاستثمار والتطوير الهندسي", size=18, color=ft.colors.GREY_700),
                ft.Container(height=10)
            )

            about_text = company_data.get("about_text", "شركة رائدة في المقاولات والتشطيبات الهندسية.")
            page.add(
                ft.Card(elevation=2, margin=ft.margin.symmetric(horizontal=15),
                        content=ft.Container(padding=20, content=ft.Column([
                            ft.Text("من نحن", weight=ft.FontWeight.BOLD, size=20, color=ft.colors.INDIGO_900),
                            ft.Text(about_text, size=15)
                        ])))
            )

            if founders_data:
                page.add(ft.Container(height=10), ft.Text("المؤسسون ومجلس الإدارة", size=18, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_900))
                for founder in founders_data:
                    page.add(
                        ft.Card(margin=ft.margin.symmetric(horizontal=15, vertical=5),
                                content=ft.ListTile(leading=ft.CircleAvatar(content=ft.Icon(ft.icons.PERSON, color=ft.colors.WHITE), bgcolor=ft.colors.INDIGO_900),
                                                    title=ft.Text(founder.get('name', ''), weight=ft.FontWeight.BOLD),
                                                    subtitle=ft.Text(f"{founder.get('role', '')}\n{founder.get('bio', '')}")))
                    )
                page.add(ft.Container(height=10))

            page.add(
                ft.ElevatedButton(text="استكشف مشاريعنا وخدماتنا", icon=ft.icons.EXPLORE, bgcolor=ft.colors.INDIGO_900, color=ft.colors.WHITE, on_click=go_to_main_hub, height=55, width=300),
                ft.Container(height=40)
            )
            page.update()
        except Exception as ex:
            page.clean()
            page.add(ft.Text(f"حدث خطأ: {ex}", color=ft.colors.RED))
            page.update()

    load_intro_screen()

if __name__ == "__main__":
    ft.app(target=main)
