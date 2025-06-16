import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
import sqlite3
import os
import shutil

class SQLiteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SQLite Group Manager")

        self.db_path = None
        self.conn = None

        # --- Верхняя панель с кнопками и полями (горизонтально) ---
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10, fill=tk.X)

        # Кнопка открыть файл
        self.btn_open = tk.Button(top_frame, text="Открыть SQLite файл", command=self.open_db)
        self.btn_open.pack(side=tk.LEFT, padx=5)

        # Поле и кнопка для замены группы
        tk.Label(top_frame, text="Группа для замены:").pack(side=tk.LEFT, padx=2)
        self.entry_old_group = tk.Entry(top_frame, width=10)
        self.entry_old_group.pack(side=tk.LEFT, padx=2)
        tk.Label(top_frame, text="Новая группа:").pack(side=tk.LEFT, padx=2)
        self.entry_new_group = tk.Entry(top_frame, width=10)
        self.entry_new_group.pack(side=tk.LEFT, padx=2)
        self.btn_replace = tk.Button(top_frame, text="Заменить группу", command=self.replace_group, state=tk.DISABLED)
        self.btn_replace.pack(side=tk.LEFT, padx=5)

        # Поле и кнопка для просмотра группы
        tk.Label(top_frame, text="Просмотр группы:").pack(side=tk.LEFT, padx=2)
        self.entry_view_group = tk.Entry(top_frame, width=10)
        self.entry_view_group.pack(side=tk.LEFT, padx=2)
        self.btn_view_group = tk.Button(top_frame, text="Просмотр", command=self.view_group, state=tk.DISABLED)
        self.btn_view_group.pack(side=tk.LEFT, padx=5)

        # Кнопка показать всех студентов
        self.btn_show_students = tk.Button(top_frame, text="Показать всех студентов", command=self.show_students, state=tk.DISABLED)
        self.btn_show_students.pack(side=tk.LEFT, padx=5)

        # Кнопка выполнить SQL код
        self.btn_run_sql = tk.Button(top_frame, text="Выполнить SQL код", command=self.run_sql_code, state=tk.DISABLED)
        self.btn_run_sql.pack(side=tk.LEFT, padx=5)

        # Кнопка переименовать кнопки
        self.btn_rename_buttons = tk.Button(top_frame, text="Переименовать кнопки", command=self.rename_buttons)
        self.btn_rename_buttons.pack(side=tk.LEFT, padx=5)

        # Кнопка очистить окно вывода
        self.btn_clear = tk.Button(top_frame, text="Очистить", command=self.clear_output)
        self.btn_clear.pack(side=tk.LEFT, padx=5)

        # Кнопка сохранить как
        self.btn_save_as = tk.Button(top_frame, text="Сохранить как...", command=self.save_as, state=tk.DISABLED)
        self.btn_save_as.pack(side=tk.LEFT, padx=5)

        # --- Текстовое поле для вывода результатов ---
        self.text_output = tk.Text(root, height=20, width=120, bg="black", fg="lime", insertbackground="lime")
        self.text_output.pack(padx=10, pady=10)

    def open_db(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл SQLite",
            filetypes=[("SQLite files", "*.sqlite *.db"), ("All files", "*.*")]
        )
        if file_path:
            if self.conn:
                self.conn.close()
            self.db_path = file_path
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.text_output.insert(tk.END, f"База данных открыта: {self.db_path}\n")
                self.btn_replace.config(state=tk.NORMAL)
                self.btn_show_students.config(state=tk.NORMAL)
                self.btn_run_sql.config(state=tk.NORMAL)
                self.btn_view_group.config(state=tk.NORMAL)
                self.btn_save_as.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть базу данных:\n{e}")

    def replace_group(self):
        old_group = self.entry_old_group.get().strip()
        new_group = self.entry_new_group.get().strip()

        if not old_group or not new_group:
            messagebox.showwarning("Внимание", "Пожалуйста, введите обе группы.")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE students SET "group" = ? WHERE "group" = ?',
                (new_group, old_group)
            )
            self.conn.commit()
            count = cursor.rowcount
            self.text_output.insert(tk.END, f"Заменено {count} записей группы '{old_group}' на '{new_group}'.\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при замене групп:\n{e}")

    def show_students(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, fam, name, "group", kurs, year FROM students')
            rows = cursor.fetchall()
            self.text_output.insert(tk.END, "Список студентов:\n")
            self.text_output.insert(tk.END, "-"*100 + "\n")
            for row in rows:
                self.text_output.insert(tk.END, f"ID: {row[0]}, Фамилия: {row[1]}, Имя: {row[2]}, Группа: {row[3]}, Курс: {row[4]}, Год: {row[5]}\n")
            self.text_output.insert(tk.END, "-"*100 + "\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении списка студентов:\n{e}")

    def view_group(self):
        group_name = self.entry_view_group.get().strip()
        if not group_name:
            messagebox.showwarning("Внимание", "Пожалуйста, введите название группы для просмотра.")
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, fam, name, kurs, year FROM students WHERE "group" = ?', (group_name,))
            rows = cursor.fetchall()
            if not rows:
                self.text_output.insert(tk.END, f"Группа '{group_name}' не найдена или в ней нет студентов.\n")
                return
            self.text_output.insert(tk.END, f"Студенты группы '{group_name}':\n")
            self.text_output.insert(tk.END, "-"*80 + "\n")
            for row in rows:
                self.text_output.insert(tk.END, f"ID: {row[0]}, Фамилия: {row[1]}, Имя: {row[2]}, Курс: {row[3]}, Год: {row[4]}\n")
            self.text_output.insert(tk.END, "-"*80 + "\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при просмотре группы:\n{e}")

    def run_sql_code(self):
        sql_code = simpledialog.askstring("Выполнить SQL", "Введите SQL код для выполнения:")
        if not sql_code:
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_code)
            if sql_code.strip().lower().startswith("select"):
                rows = cursor.fetchall()
                self.text_output.insert(tk.END, f"Результат запроса:\n")
                self.text_output.insert(tk.END, "-"*100 + "\n")
                for row in rows:
                    self.text_output.insert(tk.END, f"{row}\n")
                self.text_output.insert(tk.END, "-"*100 + "\n")
            else:
                self.conn.commit()
                self.text_output.insert(tk.END, "SQL код успешно выполнен.\n")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при выполнении SQL кода:\n{e}")

    def rename_buttons(self):
        def apply_renames():
            new_replace = entry_replace.get().strip()
            new_show = entry_show.get().strip()
            new_run_sql = entry_run_sql.get().strip()
            new_rename = entry_rename.get().strip()
            new_view = entry_view.get().strip()
            new_clear = entry_clear.get().strip()
            new_save = entry_save.get().strip()

            if new_replace:
                self.btn_replace.config(text=new_replace)
            if new_show:
                self.btn_show_students.config(text=new_show)
            if new_run_sql:
                self.btn_run_sql.config(text=new_run_sql)
            if new_rename:
                self.btn_rename_buttons.config(text=new_rename)
            if new_view:
                self.btn_view_group.config(text=new_view)
            if new_clear:
                self.btn_clear.config(text=new_clear)
            if new_save:
                self.btn_save_as.config(text=new_save)

            rename_win.destroy()

        rename_win = tk.Toplevel(self.root)
        rename_win.title("Переименовать кнопки")

        tk.Label(rename_win, text="Заменить текст кнопки 'Заменить группу':").pack(pady=2)
        entry_replace = tk.Entry(rename_win, width=40)
        entry_replace.pack(pady=2)

        tk.Label(rename_win, text="Заменить текст кнопки 'Показать всех студентов':").pack(pady=2)
        entry_show = tk.Entry(rename_win, width=40)
        entry_show.pack(pady=2)

        tk.Label(rename_win, text="Заменить текст кнопки 'Выполнить SQL код':").pack(pady=2)
        entry_run_sql = tk.Entry(rename_win, width=40)
        entry_run_sql.pack(pady=2)

        tk.Label(rename_win, text="Заменить текст кнопки 'Переименовать кнопки':").pack(pady=2)
        entry_rename = tk.Entry(rename_win, width=40)
        entry_rename.pack(pady=2)

        tk.Label(rename_win, text="Заменить текст кнопки 'Просмотр':").pack(pady=2)
        entry_view = tk.Entry(rename_win, width=40)
        entry_view.pack(pady=2)

        tk.Label(rename_win, text="Заменить текст кнопки 'Очистить':").pack(pady=2)
        entry_clear = tk.Entry(rename_win, width=40)
        entry_clear.pack(pady=2)

        tk.Label(rename_win, text="Заменить текст кнопки 'Сохранить как...':").pack(pady=2)
        entry_save = tk.Entry(rename_win, width=40)
        entry_save.pack(pady=2)

        btn_apply = tk.Button(rename_win, text="Применить", command=apply_renames)
        btn_apply.pack(pady=10)

    def clear_output(self):
        self.text_output.delete(1.0, tk.END)

    def save_as(self):
        if not self.db_path:
            messagebox.showwarning("Внимание", "Сначала откройте базу данных.")
            return
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        save_path = filedialog.asksaveasfilename(
            initialdir=desktop,
            defaultextension=".sqlite",
            filetypes=[("SQLite files", "*.sqlite *.db"), ("All files", "*.*")],
            title="Сохранить базу данных как"
        )
        if save_path:
            try:
                # Закрываем соединение перед копированием
                self.conn.close()
                shutil.copy2(self.db_path, save_path)
                # Открываем новую копию
                self.conn = sqlite3.connect(save_path)
                self.db_path = save_path
                self.text_output.insert(tk.END, f"База данных сохранена как: {save_path}\n")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении файла:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLiteApp(root)
    root.mainloop()
