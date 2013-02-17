import sublime_plugin
import sublime
import time


class MaxTabsListener(sublime_plugin.EventListener):
    # Holds the time each tab has been active
    tabs_active = {}
    # Holds the time each tab has been alive
    tabs_alive_since = {}
    # Holds the tab timers
    tab_timer = {}
    max_tabs = 0

    def __init__(self):
        settings = sublime.load_settings(__name__ + '.sublime-settings')
        self.max_tabs = settings.get('maxtabs_tab_limit')

    def close_files(self):
        # Get the window
        window = sublime.active_window()
        views = window.views()

        close = len(self.tabs_active) - self.max_tabs

        if (close < 1):
            return

        for i in range(close):
            # Get the least used view
            least_used = self.least_used()

            group = index = 0
            for view in views:
                if (view.id() == least_used):
                    sublime.active_window().focus_view(view)
                    (group, index) = window.get_view_index(view)
                    break

            if (not index):
                break

            sublime.active_window().run_command('close_by_index', {
                'group': group,
                'index': index
            })

    def on_new(self, view):
        if (view.id() not in self.tabs_alive_since):
            self.register_view(view)

        self.close_files()

    def on_load(self, view):
        if (view.id() not in self.tabs_alive_since):
            self.register_view(view)

        self.close_files()

    def on_close(self, view):
        if (view.id() in self.tabs_alive_since):
            del self.tabs_active[view.id()]
            del self.tabs_alive_since[view.id()]
            del self.tab_timer[view.id()]

    def on_activated(self, view):
        if (view.id() not in self.tabs_alive_since):
            self.register_view(view)
        self.tab_timer[view.id()] = time.time()

    def on_deactivated(self, view):
        if (view.id() not in self.tabs_alive_since):
            self.register_view(view)
        else:
            self.tabs_active[view.id()] += time.time() - self.tab_timer[view.id()]

    def register_view(self, view):
        self.tabs_active[view.id()] = 0.
        self.tabs_alive_since[view.id()] = time.time()

    def least_used(self):
        highest = highest_view_id = 0

        # Loop through all the open tabs
        for view_id, born in self.tabs_alive_since.iteritems():
            alive = (time.time() - born)
            active = self.tabs_active[view_id]

            if (alive != 0. and active != 0. and (alive / active) > highest):
                highest = alive / active
                highest_view_id = view_id

        return highest_view_id
