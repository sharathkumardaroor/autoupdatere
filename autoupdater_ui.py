import os
import subprocess
import json
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to perform git add, commit, and push
def git_commit_and_push(repo_path, commit_message, branch='main'):
    try:
        # Change to the repository directory
        os.chdir(repo_path)
        # Stage all changes
        subprocess.run(['git', 'add', '--all'], check=True)
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        # Push to the origin
        subprocess.run(['git', 'push', 'origin', branch], check=True)
        print(f"Successfully pushed changes for repo: {repo_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred for repo: {repo_path}\n{e}")

# Functions to load and save settings (JSON file)
def load_settings(json_file='repos.json'):
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
    else:
        data = {"repos": [], "commit_message": "Automated commit"}
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)
    return data

def save_settings_to_file(data, json_file='repos.json'):
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)

# Main GUI class using Tkinter
class GitAutoUpdaterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Git Auto Updater")
        self.geometry("600x400")
        self.json_file = 'repos.json'
        self.settings = load_settings(self.json_file)
        self.auto_update_thread = None
        self.stop_event = threading.Event()
        self.create_widgets()

    def create_widgets(self):
        # Commit Message Section
        commit_frame = tk.Frame(self)
        commit_frame.pack(pady=5)
        commit_label = tk.Label(commit_frame, text="Commit Message:")
        commit_label.pack(side=tk.LEFT, padx=5)
        self.commit_entry = tk.Entry(commit_frame, width=50)
        self.commit_entry.pack(side=tk.LEFT)
        # Preload commit message from settings
        self.commit_entry.insert(0, self.settings.get("commit_message", "Automated commit"))

        # Repositories List Section
        list_frame = tk.Frame(self)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        list_label = tk.Label(list_frame, text="Repositories:")
        list_label.pack(anchor="w", padx=5)
        self.repo_listbox = tk.Listbox(list_frame, width=80, height=10)
        self.repo_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.repo_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.repo_listbox.config(yscrollcommand=scrollbar.set)
        self.update_repo_listbox()

        # Buttons Section
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Repository", command=self.add_repository).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Commit and Push Now", command=self.commit_and_push_now).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Start Auto Update", command=self.start_auto_update).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Stop Auto Update", command=self.stop_auto_update).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Save Settings", command=self.save_settings).grid(row=0, column=5, padx=5)

    def update_repo_listbox(self):
        self.repo_listbox.delete(0, tk.END)
        for repo in self.settings.get("repos", []):
            self.repo_listbox.insert(tk.END, repo)

    def add_repository(self):
        # Let user select a directory using a file dialog
        repo_dir = filedialog.askdirectory(title="Select Repository Directory")
        if repo_dir:
            if repo_dir not in self.settings.get("repos", []):
                self.settings["repos"].append(repo_dir)
                save_settings_to_file(self.settings, self.json_file)
                self.update_repo_listbox()
                messagebox.showinfo("Success", f"Repository added:\n{repo_dir}")
            else:
                messagebox.showinfo("Info", "Repository already exists.")

    def remove_selected(self):
        # Remove selected repositories from the list and update JSON file
        selected_indices = self.repo_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "No repository selected to remove.")
            return
        for index in reversed(selected_indices):
            repo = self.repo_listbox.get(index)
            self.settings["repos"].remove(repo)
        save_settings_to_file(self.settings, self.json_file)
        self.update_repo_listbox()

    def commit_and_push_now(self):
        # Update settings with current commit message and process all repos
        commit_message = self.commit_entry.get()
        self.settings["commit_message"] = commit_message
        save_settings_to_file(self.settings, self.json_file)
        repos = self.settings.get("repos", [])
        for repo in repos:
            git_commit_and_push(repo, commit_message)

    def auto_update_loop(self):
        # This loop will run in a background thread.
        # Every 30 minutes, it will update settings and process all repositories.
        while not self.stop_event.is_set():
            commit_message = self.commit_entry.get()
            self.settings["commit_message"] = commit_message
            save_settings_to_file(self.settings, self.json_file)
            repos = self.settings.get("repos", [])
            for repo in repos:
                git_commit_and_push(repo, commit_message)
            # Wait for 30 minutes (1800 seconds), checking periodically for stop signal.
            for _ in range(1800):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

    def start_auto_update(self):
        if self.auto_update_thread is None or not self.auto_update_thread.is_alive():
            self.stop_event.clear()
            self.auto_update_thread = threading.Thread(target=self.auto_update_loop, daemon=True)
            self.auto_update_thread.start()
            messagebox.showinfo("Auto Update", "Auto update started.")
        else:
            messagebox.showinfo("Auto Update", "Auto update is already running.")

    def stop_auto_update(self):
        if self.auto_update_thread and self.auto_update_thread.is_alive():
            self.stop_event.set()
            self.auto_update_thread.join()
            messagebox.showinfo("Auto Update", "Auto update stopped.")
        else:
            messagebox.showinfo("Auto Update", "Auto update is not running.")

    def save_settings(self):
        commit_message = self.commit_entry.get()
        self.settings["commit_message"] = commit_message
        save_settings_to_file(self.settings, self.json_file)
        messagebox.showinfo("Settings", "Settings saved.")

if __name__ == "__main__":
    app = GitAutoUpdaterGUI()
    app.mainloop()
