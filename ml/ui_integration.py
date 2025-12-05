"""
UI Integration Module for Failure Predictions
Provides Tkinter widgets to display ML predictions in the CMMS application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from typing import Optional
from ml.predictor import FailurePredictor


class FailurePredictionPanel:
    """
    Tkinter panel for displaying failure predictions

    Can be integrated into the main CMMS application
    """

    def __init__(self, parent, connection):
        """
        Initialize prediction panel

        Args:
            parent: Parent Tkinter widget
            connection: Database connection
        """
        self.parent = parent
        self.conn = connection
        self.predictor = None

        # Try to load predictor
        try:
            self.predictor = FailurePredictor(connection)
        except Exception as e:
            print(f"Warning: Could not load failure predictor: {e}")

        self.window = None
        self.tree = None

    def show_prediction_window(self):
        """Display prediction results in a new window"""
        if self.predictor is None or self.predictor.model is None:
            messagebox.showwarning(
                "Model Not Available",
                "Failure prediction model is not trained.\n\n"
                "Please train the model first using:\n"
                "python -m ml.train_model"
            )
            return

        # Create window
        self.window = tk.Toplevel(self.parent)
        self.window.title("Equipment Failure Risk Predictions")
        self.window.geometry("1200x700")

        # Title
        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        title_label = ttk.Label(
            title_frame,
            text="Equipment Failure Risk Predictions",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        # Refresh button
        refresh_btn = ttk.Button(
            title_frame,
            text="Refresh Predictions",
            command=self._refresh_predictions
        )
        refresh_btn.pack(side=tk.RIGHT)

        # Risk filter
        filter_frame = ttk.Frame(self.window)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Filter by Risk:").pack(side=tk.LEFT, padx=5)

        self.risk_filter = tk.StringVar(value="All")
        risk_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.risk_filter,
            values=["All", "Critical", "High", "Medium", "Low"],
            state="readonly",
            width=15
        )
        risk_combo.pack(side=tk.LEFT, padx=5)
        risk_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_filter())

        # Summary frame
        self.summary_frame = ttk.LabelFrame(self.window, text="Risk Summary")
        self.summary_frame.pack(fill=tk.X, padx=10, pady=5)

        self.summary_labels = {}
        for risk_type in ['Total', 'Critical', 'High', 'Medium', 'Low']:
            label = ttk.Label(self.summary_frame, text=f"{risk_type}: 0")
            label.pack(side=tk.LEFT, padx=15, pady=5)
            self.summary_labels[risk_type] = label

        # Treeview for predictions
        tree_frame = ttk.Frame(self.window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

        # Create treeview
        columns = ('BFM #', 'Description', 'Location', 'Probability', 'Risk Level', 'Recommendation')
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        # Configure scrollbars
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Define column headings and widths
        self.tree.heading('BFM #', text='BFM #')
        self.tree.heading('Description', text='Description')
        self.tree.heading('Location', text='Location')
        self.tree.heading('Probability', text='Failure Prob.')
        self.tree.heading('Risk Level', text='Risk Level')
        self.tree.heading('Recommendation', text='Recommendation')

        self.tree.column('BFM #', width=120)
        self.tree.column('Description', width=250)
        self.tree.column('Location', width=120)
        self.tree.column('Probability', width=100)
        self.tree.column('Risk Level', width=100)
        self.tree.column('Recommendation', width=400)

        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Configure row colors based on risk
        self.tree.tag_configure('critical', background='#ffcccc')
        self.tree.tag_configure('high', background='#ffe6cc')
        self.tree.tag_configure('medium', background='#ffffcc')
        self.tree.tag_configure('low', background='#ccffcc')

        # Button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(
            button_frame,
            text="Export Report",
            command=self._export_report
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

        # Load predictions
        self._refresh_predictions()

    def _refresh_predictions(self):
        """Refresh predictions from database"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Generate predictions
            self.predictions = self.predictor.predict_all_equipment()

            # Update summary
            self._update_summary()

            # Populate tree
            self._populate_tree(self.predictions)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate predictions:\n{str(e)}")

    def _populate_tree(self, data: pd.DataFrame):
        """Populate treeview with prediction data"""
        for _, row in data.iterrows():
            # Determine row tag based on risk level
            risk_level = row['risk_level']
            tag = risk_level.lower() if risk_level else 'low'

            # Format probability as percentage
            prob_str = f"{row['failure_probability']:.1%}"

            self.tree.insert(
                '',
                'end',
                values=(
                    row['bfm_equipment_no'],
                    row['description'][:50],
                    row['location'],
                    prob_str,
                    risk_level,
                    row['recommendation'][:80]
                ),
                tags=(tag,)
            )

    def _update_summary(self):
        """Update summary statistics"""
        if not hasattr(self, 'predictions'):
            return

        total = len(self.predictions)
        critical = (self.predictions['failure_probability'] > 0.7).sum()
        high = ((self.predictions['failure_probability'] > 0.4) &
                (self.predictions['failure_probability'] <= 0.7)).sum()
        medium = ((self.predictions['failure_probability'] > 0.2) &
                  (self.predictions['failure_probability'] <= 0.4)).sum()
        low = (self.predictions['failure_probability'] <= 0.2).sum()

        self.summary_labels['Total'].config(text=f"Total: {total}")
        self.summary_labels['Critical'].config(text=f"Critical: {critical}")
        self.summary_labels['High'].config(text=f"High: {high}")
        self.summary_labels['Medium'].config(text=f"Medium: {medium}")
        self.summary_labels['Low'].config(text=f"Low: {low}")

    def _apply_filter(self):
        """Apply risk level filter"""
        if not hasattr(self, 'predictions'):
            return

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Filter data
        filter_value = self.risk_filter.get()

        if filter_value == "All":
            filtered_data = self.predictions
        else:
            filtered_data = self.predictions[
                self.predictions['risk_level'] == filter_value
            ]

        # Populate tree with filtered data
        self._populate_tree(filtered_data)

    def _export_report(self):
        """Export risk report to file"""
        try:
            from tkinter import filedialog

            # Ask for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile="failure_risk_report.txt"
            )

            if filename:
                self.predictor.generate_risk_report(output_file=filename)
                messagebox.showinfo("Success", f"Report exported to:\n{filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report:\n{str(e)}")


def add_ml_menu_item(main_window, menubar, connection):
    """
    Add ML prediction menu item to main CMMS application

    Args:
        main_window: Main application window
        menubar: Menu bar to add to
        connection: Database connection

    Example:
        # In AIT_CMMS_REV3.py, add this to create_menu():
        from ml.ui_integration import add_ml_menu_item
        add_ml_menu_item(self, menubar, self.conn)
    """
    # Create Analytics menu if it doesn't exist
    analytics_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Analytics", menu=analytics_menu)

    # Add prediction item
    def show_predictions():
        panel = FailurePredictionPanel(main_window, connection)
        panel.show_prediction_window()

    analytics_menu.add_command(
        label="Failure Risk Predictions",
        command=show_predictions
    )

    analytics_menu.add_separator()

    # Add training option
    def train_model():
        response = messagebox.askyesno(
            "Train Model",
            "This will train a new failure prediction model.\n\n"
            "This process may take several minutes.\n\n"
            "Continue?"
        )

        if response:
            messagebox.showinfo(
                "Training",
                "Model training has been initiated.\n\n"
                "Please run: python -m ml.train_model\n\n"
                "in a terminal window."
            )

    analytics_menu.add_command(
        label="Train Prediction Model",
        command=train_model
    )
