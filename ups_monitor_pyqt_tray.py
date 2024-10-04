import sys
from PyQt5.QtWidgets import (
	QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
	QProgressBar, QSystemTrayIcon, QMenu, QAction, QWidgetAction
)
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPainter, QBrush, QPalette, QCursor

import subprocess

# Replace with your UPS IP address
UPS_IP = '192.168.0.146'

def get_ups_data():
	"""
	Executes the 'upsc' command to fetch UPS data and parses the output.
	Returns a dictionary with UPS variables and their corresponding values.
	"""
	try:
		# Execute the upsc command and capture the output
		output = subprocess.check_output(['upsc', f'ups@{UPS_IP}'], universal_newlines=True)
		data = {}
		for line in output.strip().split('\n'):
			if ':' in line:
				key, value = line.split(':', 1)
				data[key.strip()] = value.strip()
		return data
	except subprocess.CalledProcessError as e:
		print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
		return {}
	except Exception as e:
		print(f"Error fetching UPS data: {e}")
		return {}

class UPSMonitorApp(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("CyberPower UPS Status")
		self.setGeometry(100, 100, 400, 500)  # x, y, width, height
		self.setFixedSize(400, 500)  # Make window size fixed

		self.initUI()
		self.init_tray()
		self.update_data()  # Initial data fetch

		# Set up a timer to update data every 5 seconds (5000 milliseconds)
		self.timer = QTimer()
		self.timer.timeout.connect(self.update_data)
		self.timer.start(5000)

	def initUI(self):
		"""
		Initializes the user interface components.
		"""
		# Main layout
		main_layout = QVBoxLayout()

		# Title
		title_label = QLabel("CyberPower UPS Status")
		title_font = QFont("Helvetica", 18, QFont.Bold)
		title_label.setFont(title_font)
		title_label.setAlignment(Qt.AlignCenter)
		main_layout.addWidget(title_label)

		# Separator
		separator = QLabel("----------------------------------------")
		main_layout.addWidget(separator)

		# UPS Status
		self.status_label = QLabel("UPS Status: N/A")
		self.status_label.setFont(QFont("Helvetica", 12, QFont.Bold))
		main_layout.addWidget(self.status_label)

		# Battery Charge
		charge_layout = QHBoxLayout()
		self.charge_text = QLabel("Battery Charge:")
		self.charge_text.setFont(QFont("Helvetica", 12, QFont.Bold))
		self.charge_value = QLabel("N/A%")
		self.charge_value.setFont(QFont("Helvetica", 12))
		charge_layout.addWidget(self.charge_text)
		charge_layout.addWidget(self.charge_value)
		main_layout.addLayout(charge_layout)

		# Battery Charge Progress Bar
		self.charge_progress = QProgressBar()
		self.charge_progress.setMaximum(100)
		self.charge_progress.setValue(0)        
		main_layout.addWidget(self.charge_progress)

		# Runtime
		runtime_layout = QHBoxLayout()
		self.runtime_text = QLabel("Estimated Runtime:")
		self.runtime_text.setFont(QFont("Helvetica", 12, QFont.Bold))
		self.runtime_value = QLabel("N/A minutes")
		self.runtime_value.setFont(QFont("Helvetica", 12))
		runtime_layout.addWidget(self.runtime_text)
		runtime_layout.addWidget(self.runtime_value)
		main_layout.addLayout(runtime_layout)

		# Input Voltage
		input_voltage_layout = QHBoxLayout()
		self.input_voltage_text = QLabel("Input Voltage:")
		self.input_voltage_text.setFont(QFont("Helvetica", 12, QFont.Bold))
		self.input_voltage_value = QLabel("N/A V")
		self.input_voltage_value.setFont(QFont("Helvetica", 12))
		input_voltage_layout.addWidget(self.input_voltage_text)
		input_voltage_layout.addWidget(self.input_voltage_value)
		main_layout.addLayout(input_voltage_layout)

		# Output Voltage
		output_voltage_layout = QHBoxLayout()
		self.output_voltage_text = QLabel("Output Voltage:")
		self.output_voltage_text.setFont(QFont("Helvetica", 12, QFont.Bold))
		self.output_voltage_value = QLabel("N/A V")
		self.output_voltage_value.setFont(QFont("Helvetica", 12))
		output_voltage_layout.addWidget(self.output_voltage_text)
		output_voltage_layout.addWidget(self.output_voltage_value)
		main_layout.addLayout(output_voltage_layout)

		# UPS Load
		load_layout = QHBoxLayout()
		self.load_text = QLabel("UPS Load:")
		self.load_text.setFont(QFont("Helvetica", 12, QFont.Bold))
		self.load_value = QLabel("N/A%")
		self.load_value.setFont(QFont("Helvetica", 12))
		load_layout.addWidget(self.load_text)
		load_layout.addWidget(self.load_value)
		main_layout.addLayout(load_layout)

		# UPS Load Progress Bar
		self.load_progress = QProgressBar()
		self.load_progress.setMaximum(100)
		self.load_progress.setValue(0)
		main_layout.addWidget(self.load_progress)

		# Separator
		separator2 = QLabel("----------------------------------------")
		main_layout.addWidget(separator2)

		# Manufacturer
		mfr_layout = QHBoxLayout()
		self.mfr_text = QLabel("Manufacturer:")
		self.mfr_text.setFont(QFont("Helvetica", 12, QFont.Bold))
		self.mfr_value = QLabel("N/A")
		self.mfr_value.setFont(QFont("Helvetica", 12))
		mfr_layout.addWidget(self.mfr_text)
		mfr_layout.addWidget(self.mfr_value)
		main_layout.addLayout(mfr_layout)

		# Model
		model_layout = QHBoxLayout()
		self.model_text = QLabel("Model:")
		self.model_text.setFont(QFont("Helvetica", 12, QFont.Bold))
		self.model_value = QLabel("N/A")
		self.model_value.setFont(QFont("Helvetica", 12))
		model_layout.addWidget(self.model_text)
		model_layout.addWidget(self.model_value)
		main_layout.addLayout(model_layout)

		# Serial Number
		serial_layout = QHBoxLayout()
		self.serial_text = QLabel("Serial Number:")
		self.serial_text.setFont(QFont("Helvetica", 12, QFont.Bold))
		self.serial_value = QLabel("N/A")
		self.serial_value.setFont(QFont("Helvetica", 12))
		serial_layout.addWidget(self.serial_text)
		serial_layout.addWidget(self.serial_value)
		main_layout.addLayout(serial_layout)

		# Last Test Result
		test_result_layout = QHBoxLayout()
		self.test_result_text = QLabel("Last Test Result:")
		self.test_result_text.setFont(QFont("Helvetica", 12, QFont.Bold))
		self.test_result_value = QLabel("N/A")
		self.test_result_value.setFont(QFont("Helvetica", 12))
		test_result_layout.addWidget(self.test_result_text)
		test_result_layout.addWidget(self.test_result_value)
		main_layout.addLayout(test_result_layout)

		# Set the main layout
		self.setLayout(main_layout)

	def init_tray(self):
		"""
		Initializes the system tray icon and its context menu.
		"""
		# Create the tray icon
		self.tray_icon = QSystemTrayIcon(self)
		self.update_tray_icon(0)  # Initialize with 0% charge

		# Create the context menu
		tray_menu = QMenu()

		show_action = QAction("Show", self)
		hide_action = QAction("Hide", self)
		show_action.triggered.connect(self.show_window)
		hide_action.triggered.connect(self.hide_window)
		tray_menu.addAction(show_action)
		tray_menu.addAction(hide_action)

		exit_action = QAction("Exit", self)
		exit_action.triggered.connect(self.exit_app)
		tray_menu.addAction(exit_action)

		self.tray_icon.setContextMenu(tray_menu)
		self.tray_icon.show()

		# Handle double-click on tray icon to show the window, even if the window is minimized
		self.tray_icon.activated.connect(self.on_tray_icon_activated)

	def on_tray_icon_activated(self, reason):
		if reason == QSystemTrayIcon.DoubleClick:
			self.show_window()
			self.show_battery_status()
			print("Tray icon double clicked")
		elif reason == QSystemTrayIcon.Click:
			self.show_battery_status()
			print("Tray icon clicked")

	def show_window(self):
		self.showNormal()  # This will restore the window if it's minimized
		self.activateWindow()  # This will bring the window to the foreground
		self.tray_icon.activated.connect(self.on_tray_icon_activated)

	def get_color_based_on_value(self, value, reverse=False):
		"""
		Calculates color based on the given value (0-100).
		If reverse is True, the gradient is from green (0%) to red (100%).
		If reverse is False, the gradient is from red (0%) to green (100%).
		Return a QColor object.
		"""

		# Ensure value is within 0-100
		value = max(0, min(100, value))
		if reverse:
			red = int(255 * value / 100)
			green = int(255 * (100 - value) / 100)
		else:
			red = int(255 * (100 - value) / 100)
			green = int(255 * value / 100)
		blue = 0
		return QColor(red, green, blue)
		#return f"rgb({red}, {green}, {blue})"

	def update_tray_icon(self, charge):
		"""
		Updates the tray icon based on the battery charge percentage.
		"""
		# Create a pixmap to draw the battery icon with charge
		pixmap = QPixmap(64, 64)
		pixmap.fill(Qt.transparent)  # Transparent background

		painter = QPainter(pixmap)
		painter.setRenderHint(QPainter.Antialiasing)

		# Draw battery outline
		pen_color = self.palette().color(QPalette.Text)  # Use system text color
		painter.setPen(pen_color)
		painter.setBrush(Qt.NoBrush)
		battery_rect = QRect(10, 20, 40, 24)
		painter.drawRect(battery_rect)

		# Draw battery positive terminal
		painter.drawRect(50, 25, 4, 14)

		# Determine fill color based on charge using get_color_based_on_value
		fill_color = self.get_color_based_on_value(charge, reverse=False)

		# Draw battery charge
		fill_width = int((charge / 100) * 40)
		if fill_width > 38:
			fill_width = 38  # Prevent overflow
		charge_rect = QRect(12, 22, fill_width, 20)
		painter.setBrush(QBrush(fill_color))
		painter.setPen(Qt.NoPen)
		painter.drawRect(charge_rect)

		painter.end()

		# Set the pixmap as the tray icon
		icon = QIcon(pixmap)
		self.tray_icon.setIcon(icon)
		self.setWindowIcon(icon)  # Optional: set window icon

	def on_tray_icon_activated(self, reason):
		"""
		Handles the activation of the tray icon.
		"""
		if reason == QSystemTrayIcon.DoubleClick:
			self.show_window()

	def hide_window(self):
		"""
		Hides the main window.
		"""
		self.hide()
		self.tray_icon.showMessage(
			"UPS Monitor",
			"Application was minimized to Tray.",
			QSystemTrayIcon.Information,
			2000
		)
		# Update the tray option menu to show the show option
		self.tray_icon.setContextMenu(self.tray_menu)
		
	def show_window(self):
		"""
		Shows the main window and brings it to the front.
		"""
		self.show()
		self.raise_()
		self.activateWindow()

		# Update the tray option menu to show the hide option
		self.tray_icon.setContextMenu(self.tray_menu)


	def closeEvent(self, event):
		"""
		Overrides the default close event to minimize to tray instead of exiting.
		"""
		event.ignore()
		self.hide()
		self.tray_icon.showMessage(
			"UPS Monitor",
			"Application was minimized to Tray.",
			QSystemTrayIcon.Information,
			2000
		)

	def exit_app(self):
		"""
		Exits the application completely.
		"""
		self.tray_icon.hide()
		QApplication.quit()

	def update_data(self):
		"""
		Fetches UPS data and updates the UI components and tray icon.
		"""
		data = get_ups_data()
		palette = self.palette()  # Fetch current system palette
		if data:
			# Update UPS Status
			self.status_label.setText(f"UPS Status: {data.get('ups.status', 'N/A')}")

			# Update Battery Charge
			charge = data.get('battery.charge', 'N/A')
			self.charge_value.setText(f"{charge}%")
			try:
				charge_int = int(charge)
				self.charge_progress.setValue(charge_int)
				# Calculate color based on charge (0% = red, 100% = green)
				charge_color = self.get_color_based_on_value(charge_int, reverse=False)
				# Apply color to charge progress bar using QPalette
				palette.setColor(QPalette.Highlight, charge_color)
				self.charge_progress.setPalette(palette)
				# Update tray icon
				self.update_tray_icon(charge_int)
			except ValueError:
				self.charge_progress.setValue(0)
				self.update_tray_icon(0)

			# Update Runtime, converted from seconds to minutes
			# Convert runtime from seconds to minutes, to the nearest tenth of a minute

			runtime = data.get('battery.runtime', 'N/A')
			if runtime != 'N/A':
				try:
					runtime_minutes = round(int(runtime) / 60, 1)
					runtime = f"{runtime_minutes}"
				except ValueError:
					pass  # If conversion fails, keep the original value
			self.runtime_value.setText(f"{runtime} minutes")

			# Update Input Voltage
			input_voltage = data.get('input.voltage', 'N/A')
			self.input_voltage_value.setText(f"{input_voltage} V")

			# Update Output Voltage
			output_voltage = data.get('output.voltage', 'N/A')
			self.output_voltage_value.setText(f"{output_voltage} V")

			# Update UPS Load
			load = data.get('ups.load', 'N/A')
			self.load_value.setText(f"{load}%")
			try:
				load_int = int(load)
				self.load_progress.setValue(load_int)
				# Calculate color based on load (0% = green, 100% = red)
				load_color = self.get_color_based_on_value(load_int, reverse=True)
				# Apply color to load progress bar using QPalette
				palette.setColor(QPalette.Highlight, load_color)
				self.load_progress.setPalette(palette)
			except ValueError:
				self.load_progress.setValue(0)
				self.update_tray_icon(0)
			# Update Manufacturer
			manufacturer = data.get('device.mfr', 'N/A')
			self.mfr_value.setText(manufacturer)

			# Update Model
			model = data.get('device.model', 'N/A')
			self.model_value.setText(model)

			# Update Serial Number
			serial = data.get('device.serial', 'N/A')
			self.serial_value.setText(serial)

			# Update Last Test Result
			test_result = data.get('ups.test.result', 'N/A')
			self.test_result_value.setText(test_result)
		else:
			# If data fetching failed, reset all fields to N/A
			self.status_label.setText("UPS Status: N/A")
			self.charge_value.setText("N/A%")
			self.charge_progress.setValue(0)
			self.runtime_value.setText("N/A seconds")
			self.input_voltage_value.setText("N/A V")
			self.output_voltage_value.setText("N/A V")
			self.load_value.setText("N/A%")
			self.load_progress.setValue(0)
			self.mfr_value.setText("N/A")
			self.model_value.setText("N/A")
			self.serial_value.setText("N/A")
			self.test_result_value.setText("N/A")
			# Update tray icon to default
			self.update_tray_icon(0)

	def show_battery_status(self):
		battery_percentage = self.get_battery_percentage()  # Implement this method to get the current battery percentage
		
		# Create a QWidget to hold the battery status bar
		status_widget = QWidget()
		layout = QVBoxLayout(status_widget)
		
		# Create a vertical progress bar
		progress_bar = QProgressBar()
		progress_bar.setOrientation(Qt.Vertical)
		progress_bar.setRange(0, 100)
		progress_bar.setValue(battery_percentage)
		progress_bar.setTextVisible(False)
		progress_bar.setFixedSize(30, 100)
		
		# Create a label for the percentage text
		percentage_label = QLabel(f"{battery_percentage}%")
		percentage_label.setAlignment(Qt.AlignCenter)
		
		layout.addWidget(progress_bar)
		layout.addWidget(percentage_label)
		
		# Create a QMenu to hold the status widget
		menu = QMenu()
		action = QWidgetAction(menu)
		action.setDefaultWidget(status_widget)
		menu.addAction(action)
		
		# Show the menu at the cursor position
		cursor_pos = QCursor.pos()
		menu.exec_(cursor_pos)

	def get_battery_percentage(self):
		# Implement this method to return the current battery percentage
		# You may need to use your existing code or add new logic to fetch this information
		pass

if __name__ == "__main__":
	app = QApplication(sys.argv)
	
	# Optional: Set the application style to 'Fusion' for better theme support
	app.setStyle("Fusion")
	
	# Optional: Apply a dark palette manually if system palette doesn't apply automatically
	dark_palette = QPalette()
	
	# Set palette colors for dark mode
	dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
	dark_palette.setColor(QPalette.WindowText, Qt.white)
	dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
	dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
	dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
	dark_palette.setColor(QPalette.ToolTipText, Qt.white)
	dark_palette.setColor(QPalette.Text, Qt.white)
	dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
	dark_palette.setColor(QPalette.ButtonText, Qt.white)
	dark_palette.setColor(QPalette.BrightText, Qt.red)
	dark_palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
	dark_palette.setColor(QPalette.HighlightedText, Qt.black)
	
	app.setPalette(dark_palette)

	window = UPSMonitorApp()
	window.show()
	sys.exit(app.exec_())