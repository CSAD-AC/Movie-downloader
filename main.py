from view import *

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()