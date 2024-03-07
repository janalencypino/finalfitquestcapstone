if __name__ == "__main__":
    from admin.admin_page import MyAppPreload, MyApp

    MyAppPreload()
    _app = MyApp(debug_mode=False, override_play_music=False)
    _app.run()
