import json
import requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread
from PIL import Image, ImageTk
from io import BytesIO


class GitHubUserFinder:
    def __init__(self, window):
        self.window = window
        self.window.title("GitHub User Finder - Поиск пользователей GitHub")
        self.window.geometry("900x700")
        
        self.favorites = []
        self.current_favorites_file = None
        self.current_user_data = None
        
        self.setup_ui()
        self.load_favorites_from_file()
        
    def setup_ui(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Панель поиска
        search_frame = ttk.LabelFrame(main_frame, text="Поиск пользователя GitHub", padding=10)
        search_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(search_frame, text="Имя пользователя:").pack(side="left", padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=30, font=('Arial', 10))
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_user())
        
        self.search_button = ttk.Button(search_frame, text="Поиск", command=self.search_user)
        self.search_button.pack(side="left", padx=(0, 10))
        
        self.status_label = ttk.Label(search_frame, text="Готов к поиску", foreground="green")
        self.status_label.pack(side="left", padx=(10, 0))
        
        # Панель результатов поиска
        result_frame = ttk.LabelFrame(main_frame, text="Результат поиска", padding=10)
        result_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Информация о пользователе
        self.user_info_frame = ttk.Frame(result_frame)
        self.user_info_frame.pack(fill="both", expand=True)
        
        # Аватар
        self.avatar_label = ttk.Label(self.user_info_frame, text="Аватар не загружен")
        self.avatar_label.pack(pady=5)
        
        # Информационные поля
        info_grid = ttk.Frame(self.user_info_frame)
        info_grid.pack(pady=10)
        
        ttk.Label(info_grid, text="Логин:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.login_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.login_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_grid, text="Имя:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.name_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.name_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_grid, text="Компания:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.company_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.company_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_grid, text="Локация:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.location_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.location_label.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_grid, text="Публичные репозитории:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.repos_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.repos_label.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_grid, text="Подписчики:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.followers_label = ttk.Label(info_grid, text="-", font=('Arial', 10))
        self.followers_label.grid(row=5, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(info_grid, text="Профиль GitHub:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky="w", padx=5, pady=2)
        self.url_label = ttk.Label(info_grid, text="-", foreground="blue", cursor="hand2", font=('Arial', 10))
        self.url_label.grid(row=6, column=1, sticky="w", padx=5, pady=2)
        
        # Кнопка добавления в избранное
        self.fav_button = ttk.Button(self.user_info_frame, text="Добавить в избранное", command=self.add_to_favorites, state="disabled")
        self.fav_button.pack(pady=10)
        
        # Панель избранного
        favorites_frame = ttk.LabelFrame(main_frame, text="Избранные пользователи", padding=10)
        favorites_frame.pack(fill="both", expand=True)
        
        # Кнопки управления избранным
        fav_buttons_frame = ttk.Frame(favorites_frame)
        fav_buttons_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(fav_buttons_frame, text="Сохранить избранное", command=self.save_favorites_to_json).pack(side="left", padx=5)
        ttk.Button(fav_buttons_frame, text="Загрузить избранное", command=self.load_favorites_from_json).pack(side="left", padx=5)
        ttk.Button(fav_buttons_frame, text="Очистить избранное", command=self.clear_favorites).pack(side="left", padx=5)
        
        # Список избранных
        list_frame = ttk.Frame(favorites_frame)
        list_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.favorites_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=8, font=('Arial', 10))
        self.favorites_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.favorites_listbox.yview)
        
        self.favorites_listbox.bind("<Double-Button-1>", self.load_favorite_user)
        
        # Кнопка удаления из избранного
        ttk.Button(favorites_frame, text="Удалить из избранного", command=self.remove_from_favorites).pack(pady=5)
        
    def search_user(self):
        username = self.search_entry.get().strip()
        
        # Валидация
        if not username:
            messagebox.showwarning("Предупреждение", "Введите имя пользователя GitHub")
            return
        
        # Отключаем кнопку поиска на время запроса
        self.search_button.config(state="disabled")
        self.status_label.config(text="Поиск...", foreground="orange")
        
        # Запускаем запрос в отдельном потоке
        Thread(target=self.fetch_user_data, args=(username,), daemon=True).start()
    
    def fetch_user_data(self, username):
        try:
            # Запрос к GitHub API
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                self.window.after(0, self.display_user_data, user_data)
                self.window.after(0, self.status_label.config, {"text": "Пользователь найден", "foreground": "green"})
            elif response.status_code == 404:
                self.window.after(0, messagebox.showerror, "Ошибка", f"Пользователь '{username}' не найден")
                self.window.after(0, self.status_label.config, {"text": "Пользователь не найден", "foreground": "red"})
                self.window.after(0, self.clear_user_display)
            else:
                self.window.after(0, messagebox.showerror, "Ошибка", f"Ошибка API: {response.status_code}")
                self.window.after(0, self.status_label.config, {"text": "Ошибка API", "foreground": "red"})
                
        except requests.exceptions.Timeout:
            self.window.after(0, messagebox.showerror, "Ошибка", "Превышено время ожидания")
            self.window.after(0, self.status_label.config, {"text": "Таймаут", "foreground": "red"})
        except requests.exceptions.ConnectionError:
            self.window.after(0, messagebox.showerror, "Ошибка", "Ошибка подключения к интернету")
            self.window.after(0, self.status_label.config, {"text": "Нет подключения", "foreground": "red"})
        except Exception as e:
            self.window.after(0, messagebox.showerror, "Ошибка", f"Произошла ошибка: {str(e)}")
            self.window.after(0, self.status_label.config, {"text": "Ошибка", "foreground": "red"})
        finally:
            self.window.after(0, self.search_button.config, {"state": "normal"})
    
    def display_user_data(self, user_data):
        self.current_user_data = user_data
        
        # Загрузка аватара
        if user_data.get('avatar_url'):
            Thread(target=self.load_avatar, args=(user_data['avatar_url'],), daemon=True).start()
        
        # Заполнение информации
        self.login_label.config(text=user_data.get('login', '-'))
        self.name_label.config(text=user_data.get('name', '-') or '-')
        self.company_label.config(text=user_data.get('company', '-') or '-')
        self.location_label.config(text=user_data.get('location', '-') or '-')
        self.repos_label.config(text=user_data.get('public_repos', 0))
        self.followers_label.config(text=user_data.get('followers', 0))
        
        # Ссылка на профиль
        profile_url = user_data.get('html_url', '#')
        self.url_label.config(text=profile_url)
        self.url_label.bind("<Button-1>", lambda e: self.open_url(profile_url))
        
        # Проверяем, есть ли пользователь в избранном
        if self.is_in_favorites(user_data['login']):
            self.fav_button.config(text="Уже в избранном", state="disabled")
        else:
            self.fav_button.config(text="Добавить в избранное", state="normal")
    
    def load_avatar(self, avatar_url):
        try:
            response = requests.get(avatar_url, timeout=10)
            img_data = Image.open(BytesIO(response.content))
            img_data = img_data.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_data)
            
            self.window.after(0, self.update_avatar, photo)
        except Exception as e:
            print(f"Ошибка загрузки аватара: {e}")
    
    def update_avatar(self, photo):
        self.avatar_label.config(image=photo)
        self.avatar_label.image = photo  # Сохраняем ссылку
    
    def clear_user_display(self):
        self.avatar_label.config(image="", text="Аватар не загружен")
        self.login_label.config(text="-")
        self.name_label.config(text="-")
        self.company_label.config(text="-")
        self.location_label.config(text="-")
        self.repos_label.config(text="-")
        self.followers_label.config(text="-")
        self.url_label.config(text="-")
        self.fav_button.config(state="disabled")
        self.current_user_data = None
    
    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)
    
    def add_to_favorites(self):
        if not self.current_user_data:
            messagebox.showwarning("Предупреждение", "Нет данных о пользователе")
            return
        
        username = self.current_user_data['login']
        
        if self.is_in_favorites(username):
            messagebox.showinfo("Информация", "Пользователь уже в избранном")
            return
        
        favorite = {
            "login": self.current_user_data['login'],
            "name": self.current_user_data.get('name', ''),
            "avatar_url": self.current_user_data.get('avatar_url', ''),
            "html_url": self.current_user_data.get('html_url', ''),
            "company": self.current_user_data.get('company', ''),
            "location": self.current_user_data.get('location', ''),
            "public_repos": self.current_user_data.get('public_repos', 0),
            "followers": self.current_user_data.get('followers', 0)
        }
        
        self.favorites.append(favorite)
        self.update_favorites_list()
        self.fav_button.config(text="Уже в избранном", state="disabled")
        messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное")
    
    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления")
            return
        
        index = selection[0]
        removed_user = self.favorites.pop(index)
        self.update_favorites_list()
        messagebox.showinfo("Успех", f"Пользователь {removed_user['login']} удален из избранного")
        
        # Если удаленный пользователь сейчас отображается, обновляем кнопку
        if self.current_user_data and self.current_user_data['login'] == removed_user['login']:
            self.fav_button.config(text="Добавить в избранное", state="normal")
    
    def load_favorite_user(self, event):
        selection = self.favorites_listbox.curselection()
        if selection:
            index = selection[0]
            username = self.favorites[index]['login']
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, username)
            self.search_user()
    
    def update_favorites_list(self):
        self.favorites_listbox.delete(0, tk.END)
        for fav in self.favorites:
            display_text = f"{fav['login']} - {fav.get('name', 'Без имени')}"
            self.favorites_listbox.insert(tk.END, display_text)
    
    def is_in_favorites(self, username):
        return any(fav['login'] == username for fav in self.favorites)
    
    def save_favorites_to_json(self):
        if not self.favorites:
            messagebox.showwarning("Предупреждение", "Нет избранных пользователей для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить избранное"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.favorites, f, ensure_ascii=False, indent=4)
                self.current_favorites_file = file_path
                messagebox.showinfo("Успех", f"Избранное сохранено в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
    
    def load_favorites_from_json(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Загрузить избранное"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    loaded_favorites = json.load(f)
                
                # Валидация загруженных данных
                for fav in loaded_favorites:
                    if not all(k in fav for k in ("login", "name", "html_url")):
                        raise ValueError("Неверный формат данных в файле")
                
                self.favorites = loaded_favorites
                self.current_favorites_file = file_path
                self.update_favorites_list()
                messagebox.showinfo("Успех", f"Загружено {len(self.favorites)} избранных пользователей")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    
    def load_favorites_from_file(self):
        """Загрузка избранного из файла по умолчанию"""
        default_file = "favorites.json"
        if os.path.exists(default_file):
            try:
                with open(default_file, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
                    self.update_favorites_list()
            except Exception as e:
                print(f"Не удалось загрузить {default_file}: {e}")
    
    def clear_favorites(self):
        if self.favorites:
            if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить весь список избранного?"):
                self.favorites.clear()
                self.update_favorites_list()
                if self.current_user_data:
                    self.fav_button.config(text="Добавить в избранное", state="normal")
                messagebox.showinfo("Успех", "Список избранного очищен")


if __name__ == "__main__":
    import os
    
    # Проверка наличия необходимых библиотек
    try:
        import requests
        from PIL import Image, ImageTk
    except ImportError as e:
        print("Ошибка: Отсутствуют необходимые библиотеки")
        print("Установите их командой:")
        print("pip install requests pillow")
        input("Нажмите Enter для выхода...")
        exit(1)
    
    try:
        window = tk.Tk()
        app = GitHubUserFinder(window)
        window.mainloop()
    except ImportError:
        print("Ошибка: Tkinter не установлен.")
        print("На Linux установите: sudo apt-get install python3-tk")
        input("Нажмите Enter для выхода...")
