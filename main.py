import sqlite3
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.image import Image as CoreImage
from kivy.uix.screenmanager import ScreenManager, Screen
from io import BytesIO
import shutil

# إنشاء قاعدة البيانات
def create_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS work_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fonction TEXT,
        connector TEXT,
        image BLOB,
        outil TEXT
    )''')
    conn.commit()
    conn.close()

def search_data(connector, fonction=None, outil=None):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    query = "SELECT fonction, outil, image FROM work_data WHERE connector = ?"
    params = [connector]
    
    if fonction:
        query += " AND fonction LIKE ?"
        params.append(f'%{fonction}%')
    if outil:
        query += " AND outil LIKE ?"
        params.append(f'%{outil}%')
    
    cursor.execute(query, tuple(params))
    result = cursor.fetchone()
    conn.close()
    return result

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        # صورة الخلفية
        background_image = Image(source='race_car.jpg', allow_stretch=True, keep_ratio=False)
        self.layout.add_widget(background_image)

        # قسم البحث
        search_layout = BoxLayout(orientation='horizontal', size_hint=(0.9, None), height=50, pos_hint={'center_x': 0.5, 'top': 0.95})
        self.search_input = TextInput(hint_text="Enter connector to search", size_hint=(0.7, None), height=40, multiline=False)
        self.fonction_input = TextInput(hint_text="Enter fonction", size_hint=(0.7, None), height=40, multiline=False)
        self.outil_input = TextInput(hint_text="Enter outil", size_hint=(0.7, None), height=40, multiline=False)
        search_button = Button(text="Search", size_hint=(0.3, None), height=40, background_color=(0.1, 0.5, 0.9, 1))
        search_button.bind(on_press=self.search)

        search_layout.add_widget(self.search_input)
        search_layout.add_widget(self.fonction_input)
        search_layout.add_widget(self.outil_input)
        search_layout.add_widget(search_button)

        self.layout.add_widget(search_layout)

        # زر مخفي للانتقال إلى شاشة إدخال البيانات
        admin_button = Button(text="Go to Data Entry", size_hint=(0.3, None), height=40, background_color=(0.2, 0.6, 0.2, 1), pos_hint={'center_x': 0.5, 'y': 0.1})
        admin_button.bind(on_press=self.goto_data_entry)
        self.layout.add_widget(admin_button)

        # زر تحميل البيانات
        upload_button = Button(text="Upload Data", size_hint=(0.3, None), height=40, background_color=(0.5, 0.2, 0.2, 1), pos_hint={'center_x': 0.5, 'y': 0.05})
        upload_button.bind(on_press=self.goto_data_upload)
        self.layout.add_widget(upload_button)

        self.add_widget(self.layout)

    def search(self, instance):
        connector = self.search_input.text
        fonction = self.fonction_input.text
        outil = self.outil_input.text
        
        if not connector:
            self.show_popup("Please enter a connector to search.")
            return

        # البحث في قاعدة البيانات
        result = search_data(connector, fonction, outil)
        if result:
            fonction, outil, image_data = result
            # تم الانتقال إلى شاشة جديدة لعرض النتائج
            self.manager.current = "search_result"
            self.manager.get_screen("search_result").display_result(fonction, outil, image_data)
        else:
            self.show_popup("No data found for this connector.")

    def goto_data_entry(self, instance):
        self.manager.current = "data_entry"

    def goto_data_upload(self, instance):
        self.manager.current = "data_upload"

    def show_popup(self, message):
        popup = Popup(title="Message", content=Label(text=message), size_hint=(0.6, 0.4))
        popup.open()


class SearchResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # مكان عرض البيانات عند البحث
        self.result_label = Label(text="Search results will appear here", font_size=20)
        layout.add_widget(self.result_label)

        # عرض الصورة
        self.result_image = Image(size_hint=(1, 0.6))
        layout.add_widget(self.result_image)

        # إضافة زر العودة إلى الشاشة الرئيسية
        back_button = Button(text="Back", size_hint=(0.2, None), height=40, background_color=(0.7, 0.1, 0.1, 1))
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def display_result(self, fonction, outil, image_data):
        # عرض البيانات في الشاشة الجديدة
        self.result_label.text = f"Fonction: {fonction}\nOutil: {outil}"
        
        if image_data:
            image = CoreImage(BytesIO(image_data), ext='png')
            self.result_image.texture = image.texture
        else:
            self.result_image.source = ""  # إذا لم تكن هناك صورة

    def go_back(self, instance):
        self.manager.current = "main"


class DataEntryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        layout.add_widget(Label(text="Data Entry", size_hint_y=None, height=30, font_size=20, bold=True))

        self.fonction_input = TextInput(hint_text="Enter fonction", size_hint_y=None, height=40)
        self.connector_input = TextInput(hint_text="Enter connector", size_hint_y=None, height=40)
        self.outil_input = TextInput(hint_text="Enter outil", size_hint_y=None, height=40)

        layout.add_widget(Label(text="Fonction:"))
        layout.add_widget(self.fonction_input)
        layout.add_widget(Label(text="Connector:"))
        layout.add_widget(self.connector_input)
        layout.add_widget(Label(text="Outil:"))
        layout.add_widget(self.outil_input)

        # زر تحميل الصورة
        self.image_button = Button(text="Upload Image", size_hint_y=None, height=40, background_color=(0.1, 0.5, 0.9, 1))
        self.image_button.bind(on_press=self.open_filechooser)
        layout.add_widget(self.image_button)

        # مكان عرض نتيجة الحفظ (علامة الصح)
        self.success_label = Label(text="", size_hint_y=None, height=40)
        layout.add_widget(self.success_label)

        # أزرار الحفظ والتراجع
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        save_button = Button(text="Save", background_color=(0.1, 0.7, 0.1, 1))
        save_button.bind(on_press=self.save_data)
        back_button = Button(text="Back", background_color=(0.7, 0.1, 0.1, 1))
        back_button.bind(on_press=self.go_back)
        button_layout.add_widget(save_button)
        button_layout.add_widget(back_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def open_filechooser(self, instance):
        filechooser = FileChooserIconView(filters=['*.png', '*.jpg', '*.jpeg'])
        filechooser.bind(on_selection=self.on_file_selected)
        popup_layout = BoxLayout(orientation='vertical')
        popup_layout.add_widget(filechooser)

        validate_button = Button(text="Validate", size_hint_y=None, height=40)
        validate_button.bind(on_press=lambda x: self.select_image(filechooser))
        close_button = Button(text="Close", size_hint_y=None, height=40)
        close_button.bind(on_press=lambda x: self.popup.dismiss())
        popup_layout.add_widget(validate_button)
        popup_layout.add_widget(close_button)

        self.popup = Popup(title="Select Image", content=popup_layout, size_hint=(0.8, 0.8))
        self.popup.open()

    def on_file_selected(self, filechooser, selection):
        if selection:
            self.image_path = selection[0]

    def select_image(self, filechooser):
        if filechooser.selection:
            self.image_path = filechooser.selection[0]
            self.popup.dismiss()

    def save_data(self, instance):
        fonction = self.fonction_input.text
        connector = self.connector_input.text
        outil = self.outil_input.text

        if not fonction or not connector or not outil:
            self.success_label.text = "Please fill all fields!"
            return

        # حفظ البيانات في قاعدة البيانات
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        with open(self.image_path, 'rb') as file:
            image_data = file.read()
        cursor.execute("INSERT INTO work_data (fonction, connector, image, outil) VALUES (?, ?, ?, ?)",
                       (fonction, connector, image_data, outil))
        conn.commit()
        conn.close()

        self.success_label.text = "Data saved successfully!"
        self.fonction_input.text = ""
        self.connector_input.text = ""
        self.outil_input.text = ""

    def go_back(self, instance):
        self.manager.current = "main"


class DataUploadScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        layout.add_widget(Label(text="Upload Database", size_hint_y=None, height=30, font_size=20, bold=True))

        # زر تحميل قاعدة البيانات
        self.upload_button = Button(text="Choose File", size_hint_y=None, height=40)
        self.upload_button.bind(on_press=self.open_filechooser)
        layout.add_widget(self.upload_button)

        self.success_label = Label(text="", size_hint_y=None, height=40)
        layout.add_widget(self.success_label)

        # زر الرجوع
        back_button = Button(text="Back", size_hint=(0.2, None), height=40, background_color=(0.7, 0.1, 0.1, 1))
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def open_filechooser(self, instance):
        filechooser = FileChooserIconView(filters=['*.db'])
        filechooser.bind(on_selection=self.on_file_selected)
        popup_layout = BoxLayout(orientation='vertical')
        popup_layout.add_widget(filechooser)

        validate_button = Button(text="Validate", size_hint_y=None, height=40)
        validate_button.bind(on_press=lambda x: self.select_file(filechooser))
        close_button = Button(text="Close", size_hint_y=None, height=40)
        close_button.bind(on_press=lambda x: self.popup.dismiss())
        popup_layout.add_widget(validate_button)
        popup_layout.add_widget(close_button)

        self.popup = Popup(title="Select Database File", content=popup_layout, size_hint=(0.8, 0.8))
        self.popup.open()

    def on_file_selected(self, filechooser, selection):
        if selection:
            self.selected_file = selection[0]

    def select_file(self, filechooser):
        if filechooser.selection:
            self.selected_file = filechooser.selection[0]
            self.popup.dismiss()

    def go_back(self, instance):
        self.manager.current = "main"


class MyApp(App):
    def build(self):
        create_db()  # إنشاء قاعدة البيانات إذا لم تكن موجودة
        sm = ScreenManager()

        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(DataEntryScreen(name="data_entry"))
        sm.add_widget(DataUploadScreen(name="data_upload"))
        sm.add_widget(SearchResultScreen(name="search_result"))

        return sm

if __name__ == "__main__":
    MyApp().run()
