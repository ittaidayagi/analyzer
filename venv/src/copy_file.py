import os
import win32com.client
import win32api
import re
import shutil

class files_utils():
	"""
	Utils for copy and send files with shadow copies
	"""

	def __init__(self):

		# Constants
		self.default_config = {
			"WMI_Query": "SELECT * FROM Win32_ShadowCopy where ID='{0}'",
			"WMI_Shadow_Copy": "winmgmts:\\\\.\\root\\cimv2:Win32_ShadowCopy"
		}

		# The state of the object - open or close
		self.opened = False


	def __get(self, key):
		"""
		Get consstans from default config
		:param key: The name of the constant
		:return: The value of the constant
		"""

		return self.default_config[key]

	def __get_vss_by_id(self, vss_id):
		"""
		Get the path of the shadow copy by its ID
		:param vss_id: The ID of the shadow copy
		:return: The path of the shadow copy
		"""

		# Create a wmi client
		wcd = win32com.client.Dispatch("WbemScripting.SWbemLocator")
		wmi = wcd.ConnectServer(".","root\cimv2")

		# Query the shadow copy where the ID is the asked ID
		obj = wmi.ExecQuery(self.__get("WMI_Query").format(vss_id))
		return [x.DeviceObject for x in obj]

	def open(self):
		"""
		Create a shadow copy for every volume
		:return: None
		"""
		# Check if the shadow copy already open
		if self.opened:
			raise "The shadow copy already open"

		# Get local drives
		local_drives = get_local_drives()

		# Create the shadow copies and put their ID in dictionary
		vss = dict()
		for local_drive in local_drives:

			vss[local_drive] = self.__create_shadow_copy(local_drive)

		# Put the vss dictionary in class variable
		self.vss = vss

		# Change vss status to open
		self.opened = True

	def __create_shadow_copy(self,drive_letter):
		"""
		Create shadow copy of the given local drive
		:param drive_letter: The letter of the local drive
		:return: The ID of the shadow copy
		"""

		# Create a wmi client
		wmi = win32com.client.GetObject(self.__get("WMI_Shadow_Copy"))

		# Create the "create" method
		createmethod = wmi.Methods_("Create")
		createparams = createmethod.InParameters

		# Add the drive to the properties of the method
		createparams.Properties_[1].value = "{0}:\\".format(drive_letter)

		# Execute the wmi query that create the shadow copy
		results = wmi.ExecMethod_("Create", createparams)

		# Return the ID
		return results.Properties_[1].value

	def __get_shadow_path(self, source):
		"""
		Return the shadow copy path of the original path
		:param source: The original path
		:return: The shadow copy path
		"""

		# Split the path to the local drive and the path
		splited_source = source.split(":\\")
		drive = splited_source[0].upper()
		path = splited_source[1]

		# Check if drive exists in vss
		if not drive in self.vss.keys():
			raise "Unknown local drive"

		# Get the path of the vss
		shadow_path = self.__get_vss_by_id(self.vss[drive])

		# Join the path of the vss with the original path(without the drive letter) and return it
		full_path = os.path.join(shadow_path, path)
		return full_path

	def copy_file(self, source, destination):
		"""
		Copy the given file(with the shadow copy)
		:param source: Path of the file to copy
		:param destination: The destination to copy
		:return: Bool
		"""

		# Get the shadow copy path
		path = self.__get_shadow_path(source)

		# Copy the file
		try: shutil.copyfile(path,destination)
		except: return 1
		else: return 0

	def send_file(self, source, destination):

		path = self.get_shadow_path(source)
		# TODO: a module for sending with socket than use it here

	def __vss_delete(self, shadow_id):
		"""
		Delete shadow copy according to the given ID
		:param shadow_id: The shadow copy ID
		:return: Bool
		"""

		# Create a wmi client
		wcd = win32com.client.Dispatch("WbemScripting.SWbemLocator")
		wmi = wcd.ConnectServer(".", "root\cimv2")

		# Execute the wmi query that delete the shadow copy by ID
		obj = wmi.ExecQuery(
			self.__get("WMI_Query").format(
				shadow_id))
		try: obj[0].Delete_()

		# Return status
		except: return 1
		else: return 0

	def close(self):
		"""
		Close all of the shadow copies
		:return: Bool
		"""

		# Check if not already close
		if not self.opened:
			raise "There is no open shadow copy"

		# Try to delete every vss and update the result
		result = 0
		for drive in self.vss.values():
			result = self.__vss_delete(drive) + result

		# Update open/close status
		self.opened = False

		# Return success status
		return result

def get_local_drives():
	"""
	Get the local drives of the computer
	:return: List of local drives
	"""

	# Get the local drives
	local_drives = win32api.GetLogicalDriveStrings()

	# Return only the letter of the local drive
	return re.findall("[A-Z]", local_drives)