import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch  # Import the Switch widget
from kivy.uix.image import Image

# Set background to white by default for light mode
Window.clearcolor = (1, 1, 1, 1)

# File to store data
expense_file = "expenses.json"

def load_data():
    if os.path.exists(expense_file):
        with open(expense_file, "r") as file:
            return json.load(file)
    return {"balance": 0, "expenses": []}

def save_data(data):
    with open(expense_file, "w") as file:
        json.dump(data, file, indent=4)

class ExpenseTracker(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        self.data = load_data()
        self.is_dark_mode = False  # Variable to track dark mode

        # Logo at the top
        self.logo = Image(source="logo.png", size_hint=(1, 3.0), allow_stretch=True, keep_ratio=True)
        self.add_widget(self.logo)

        # Balance Label
        self.balance_label = Label(text="", font_size=24, bold=True, color=(0, 0.2, 0.6, 1))
        self.update_balance_text()
        self.add_widget(self.balance_label)

        # Input for amount spent
        self.amount_input = TextInput(hint_text="Amount Spent (Naira)", multiline=False, input_filter='float')
        self.add_widget(self.amount_input)

        # Input for expense description
        self.description_input = TextInput(hint_text="What did you spend on?", multiline=False)
        self.add_widget(self.description_input)

        # Add Expense Button
        self.add_expense_btn = Button(text="Add Expense", background_color=(0.2, 0.4, 1, 1), color=(1, 1, 1, 1))
        self.add_expense_btn.bind(on_press=self.add_expense)
        self.add_widget(self.add_expense_btn)

        # View Balance Button
        self.view_balance_btn = Button(text="View Balance", background_color=(0.2, 0.4, 0.9, 1), color=(1, 1, 1, 1))
        self.view_balance_btn.bind(on_press=self.update_balance_text)
        self.add_widget(self.view_balance_btn)

        # Set Balance Input
        self.set_balance_input = TextInput(hint_text="Set your balance (Naira)", multiline=False, input_filter='float')
        self.add_widget(self.set_balance_input)

        # Set Balance Button
        self.set_balance_btn = Button(text="Set Balance", background_color=(0, 0.5, 1, 1), color=(1, 1, 1, 1))
        self.set_balance_btn.bind(on_press=self.set_balance)
        self.add_widget(self.set_balance_btn)

        # View Expenses Button
        self.view_expenses_btn = Button(text="View Expenses", background_color=(0.1, 0.3, 0.6, 1), color=(1, 1, 1, 1))
        self.view_expenses_btn.bind(on_press=self.view_expenses)
        self.add_widget(self.view_expenses_btn)

        # Dark Mode Switch
        self.dark_mode_switch = Switch(active=self.is_dark_mode)
        self.dark_mode_switch.bind(active=self.toggle_dark_mode)
        self.add_widget(Label(text="Dark Mode:", color=(0, 0, 0, 1), font_size=18))
        self.add_widget(self.dark_mode_switch)

        # Label above history
        self.history_title = Label(text="EXPENSE HISTORY:", bold=True, font_size=18, color=(0, 0, 0, 1))
        self.add_widget(self.history_title)

        # Scrollable area for expenses
        self.scroll = ScrollView(size_hint=(1, 0.4))
        self.expenses_label = Label(text="", markup=True, font_size=16, size_hint_y=None)
        self.expenses_label.bind(texture_size=self.adjust_label_height)
        self.scroll.add_widget(self.expenses_label)
        self.add_widget(self.scroll)

    def adjust_label_height(self, instance, value):
        instance.height = value[1]

    def update_balance_text(self, *args):
        self.balance_label.text = f"Current Balance: N{self.data['balance']:.2f}"

    def set_balance(self, instance):
        try:
            amount = float(self.set_balance_input.text)
            self.data['balance'] = amount
            self.data['expenses'] = []
            save_data(self.data)
            self.update_balance_text()
            self.expenses_label.text = ""
            self.set_balance_input.text = ""
        except ValueError:
            self.expenses_label.text = "[color=ff0000]Invalid balance amount[/color]"

    def add_expense(self, instance):
        try:
            amount = float(self.amount_input.text)
            description = self.description_input.text.strip()

            if amount > self.data['balance']:
                self.expenses_label.text = "[color=ff0000]Insufficient funds![/color]"
                return

            self.data['balance'] -= amount
            self.data['expenses'].append({"amount": amount, "description": description})
            save_data(self.data)
            self.update_balance_text()

            self.amount_input.text = ""
            self.description_input.text = ""
            self.expenses_label.text = f"[color=ff0000]Added: N{amount:.2f} {description}[/color]"
        except ValueError:
            self.expenses_label.text = "[color=ff0000]Enter a valid amount[/color]"

    def view_expenses(self, instance):
        if not self.data['expenses']:
            self.expenses_label.text = "[color=ff0000]No expenses recorded yet[/color]"
            return

        expense_list = "\n".join(
            [f"[color=ff0000]N{e['amount']:.2f}[/color]   [color=444444]{e['description']}[/color]" for e in self.data["expenses"]]
        )

        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        scroll = ScrollView(size_hint=(1, 0.9), bar_width=8)
        label = Label(
            text=expense_list,
            markup=True,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=16,
        )
        label.bind(texture_size=lambda instance, value: setattr(label, 'height', value[1]))
        scroll.add_widget(label)

        close_btn = Button(
            text="Close", 
            size_hint=(1, 0.1), 
            background_color=(0, 0, 1, 1),  # Dark blue for the close button
            color=(1, 1, 1, 1),
            bold=True
        )
        content.add_widget(scroll)
        content.add_widget(close_btn)

        # Store popup as instance attribute to prevent immediate closure
        self.popup = Popup(
            title="Expense History",
            content=content,
            size_hint=(0.95, 0.9),
            auto_dismiss=False,
            separator_color=(0, 0.4, 1, 1),
            background_color=(0, 0.5, 1, 1),
        )
        close_btn.bind(on_press=self.popup.dismiss)
        self.popup.open()

    def toggle_dark_mode(self, instance, value):
        self.is_dark_mode = value
        if self.is_dark_mode:
            Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Dark background
            self.balance_label.color = (1, 1, 1, 1)  # White text for dark mode
            self.history_title.color = (1, 1, 1, 1)  # White text for dark mode
            self.amount_input.background_color = (0.2, 0.2, 0.2, 1)
            self.description_input.background_color = (0.2, 0.2, 0.2, 1)
            self.set_balance_input.background_color = (0.2, 0.2, 0.2, 1)
            self.expenses_label.color = (1, 1, 1, 1)
            self.add_expense_btn.background_color = (0.3, 0.3, 0.3, 1)
            self.view_balance_btn.background_color = (0.3, 0.3, 0.3, 1)
            self.set_balance_btn.background_color = (0.3, 0.3, 0.3, 1)
            self.view_expenses_btn.background_color = (0.3, 0.3, 0.3, 1)
        else:
            Window.clearcolor = (1, 1, 1, 1)  # Light background (original mode)
            self.balance_label.color = (0, 0.2, 0.6, 1)  # Original text color for light mode
            self.history_title.color = (0, 0, 0, 1)  # Black text for light mode
            self.amount_input.background_color = (1, 1, 1, 1)
            self.description_input.background_color = (1, 1, 1, 1)
            self.set_balance_input.background_color = (1, 1, 1, 1)
            self.expenses_label.color = (0, 0, 0, 1)
            self.add_expense_btn.background_color = (0.2, 0.4, 1, 1)
            self.view_balance_btn.background_color = (0.2, 0.4, 0.9, 1)
            self.set_balance_btn.background_color = (0, 0.5, 1, 1)
            self.view_expenses_btn.background_color = (0.1, 0.3, 0.6, 1)


class ExpenseTrackerApp(App):
    def build(self):
        return ExpenseTracker()

if __name__ == "__main__":
    ExpenseTrackerApp().run()

