import flet as ft
import subprocess

class Tasker:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.page.on_route_change = self.on_change_root
        self.page.on_view_pop = self.on_pop_view
        self.page.title = "Tasker for Windows"
        self.page.go("/")

    def on_change_root(self, route) -> None:
        self.page.views.clear()
        if self.page.route == "/":
            self.page.views.append(
                ft.View(
                    "/",
                    [
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.TextButton(text="Создать задачу", width=300, height=300, style=ft.ButtonStyle(color=ft.colors.LIGHT_BLUE_ACCENT, shape=ft.RoundedRectangleBorder(radius=10), side=ft.border.BorderSide(1, ft.colors.BLACK)), icon=ft.icons.ADD_TASK, on_click=self.create_task_button, icon_color=ft.colors.GREEN),
                                        ft.TextButton(text="Посмотреть задачи", width=300, height=300, style=ft.ButtonStyle(color=ft.colors.LIGHT_BLUE_ACCENT, shape=ft.RoundedRectangleBorder(radius=10), side=ft.border.BorderSide(1, ft.colors.BLACK)), icon=ft.icons.TASK, on_click=self.manage_task_button, icon_color=ft.colors.RED),
                                    ],
                                    alignment="center",
                                    spacing=20
                                )
                            ]
                        )
                    ],
                    vertical_alignment="center"
                )
            )
            self.page.update()

        elif self.page.route == "/create":
            self.choose_schedule = ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="При входе", on_click=self.schedule_item_clicked),
                    ft.PopupMenuItem(text="При запуске", on_click=self.schedule_item_clicked),
                    ft.PopupMenuItem(text="Каждый месяц", on_click=self.schedule_item_clicked),
                    ft.PopupMenuItem(text="Каждую неделю", on_click=self.schedule_item_clicked)
                    ],
                    content=ft.Text("Выбор...")
                    )
            self.path_to_programm = ft.TextButton(text="Выбрать...", on_click=self.choose_file_button)
            self.chooser = ft.FilePicker(on_result=self.on_choose_file)
            self.page.overlay.append(self.chooser)
            self.name_task = ft.TextField(tooltip="Название вашей задачи")
                                            
            self.page.views.append(
                ft.View(
                    "/create",
                    [
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(value="Название:", color=ft.colors.WHITE, size=20),
                                        self.name_task
                                    ],
                                    alignment="center"
                                ),
                                ft.Row(
                                    [
                                        ft.Text(value="Программа/скрипт:", color=ft.colors.WHITE, size=20),
                                        self.path_to_programm
                                    ],
                                    alignment="center"
                                ),
                                ft.Row(
                                    [
                                        ft.Text(value="Выполнять при:", color=ft.colors.WHITE, size=20),
                                        self.choose_schedule
                                    ],
                                    alignment="center"
                                )
                            ],
                        ),
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.TextButton(text="Создать", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), bgcolor=ft.colors.GREEN, color=ft.colors.WHITE), width=150, height=60, on_click=self.create)
                                    ],
                                    alignment="center",
                                )
                            ]
                        )
                    ],
                    appbar=ft.AppBar(title=ft.Text("Создать"), center_title=False, bgcolor=ft.colors.GREEN, leading_width=30, leading=ft.IconButton(ft.icons.ARROW_BACK_IOS, on_click=self.back_button)),
                    vertical_alignment="center"
                )
            )
            self.page.update()


        elif self.page.route == "/manage":
            self.list_tasks = ft.ListView(width=500)
            self.update_task_list()
            self.page.views.append(
                ft.View(
                    "/create",
                    [
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        self.list_tasks
                                    ],
                                    alignment="center"
                                )
                            ]
                        )
                    ],
                    vertical_alignment="center",              
                    appbar=ft.AppBar(title=ft.Text("Задачи"), center_title=False, bgcolor=ft.colors.RED, leading_width=30, leading=ft.IconButton(ft.icons.ARROW_BACK_IOS, on_click=self.back_button))
                )
            )
            self.page.update()
    
    def on_pop_view(self) -> None:
        self.page.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)

    def create_task_button(self, e) -> None:
        self.page.go("/create")

    def back_button(self, e) -> None:
        self.page.go("/")

    def manage_task_button(self, e) -> None:
        self.page.go("/manage")

    def schedule_item_clicked(self, e: ft.ControlEvent) -> None:
        name = e.control.text
        self.choose_schedule.content.value = name
        self.page.update()

    def on_choose_file(self, e: ft.FilePickerResultEvent):
        try:
            path = e.files[0].path
            self.path_to_programm.text = path
            self.page.update()
        except TypeError:
            pass

    def choose_file_button(self, e):
        self.chooser.pick_files("Выбор программы/скрипта", allow_multiple=False, file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["exe", "bat"])

    def create(self, e):
        path = self.path_to_programm.text
        name = self.name_task.value
        match self.choose_schedule.content.value:
            case "При входе":
                interval = "onlogon"
            case "При запуске":
                interval = "onstart"
            case "Каждый месяц":
                interval = "monthly"
            case "Каждую неделю":
                interval = "weekly"
            case _:
                interval = None
        if path != "Выбрать..." and name != "" and not interval is None:
            cmd = f"schtasks /create /tn Tasker\{name} /tr {path} /sc {interval}"
            result = subprocess.run(cmd, shell=True, capture_output=True)
            code = result.stdout.decode("cp866").split(".")
            if code[0] == "УСПЕХ":
                dialog = ft.AlertDialog(title=ft.Text("Успешно!"), actions_alignment="center", on_dismiss=lambda e: self.page.go("/"))
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
            else:
                dialog = ft.AlertDialog(title=ft.Text("Попробуйте другое имя!"), actions_alignment="center")
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
        else:
            dialog = ft.AlertDialog(title=ft.Text("Заполните все поля!"), actions_alignment="center")
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

    def delete_task(self, e: ft.ControlEvent) -> None:
        name_task = e.control.data
        result = subprocess.run(f"schtasks /delete /tn Tasker\{name_task} /f", shell=True, capture_output=True).stdout.decode("cp866").split(".")[0]
        if result == "УСПЕХ":
            self.update_task_list()
            dialog = ft.AlertDialog(title=ft.Text("Успешно!"))
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        else:
            dialog = ft.AlertDialog(title=ft.Text("Ошибка!"))
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

    def update_task_list(self, e=None) -> None:
        self.list_tasks.controls.clear()
        tasks = list(map(lambda x: x.split()[0], subprocess.run("schtasks /query /tn Tasker\\", shell=True, capture_output=True).stdout.decode("cp866").split("\n")[4:-1]))
        for i in tasks:
            self.list_tasks.controls.append(ft.ListTile(leading=ft.Icon(ft.icons.TASK), title=ft.Text(i), trailing=ft.PopupMenuButton(icon=ft.icons.MORE_VERT, items=[ft.PopupMenuItem(text="Удалить", on_click=self.delete_task, data=i)])))
        self.page.update()

ft.app(target=Tasker, view=ft.FLET_APP)