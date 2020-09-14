import os
import win32com.client
import win32api
import re
import shutil

class files_utils():

	def __init__(self):

		self.default_config = {
			"WMI_Query": "SELECT * FROM Win32_ShadowCopy where ID='{0}'",
			"WMI_Shadow_Copy": "winmgmts:\\\\.\\root\\cimv2:Win32_ShadowCopy"
		}
		self.opened = False


	def __get(self, key):

		return self.default_config[key]

	def __get_vss_by_id(self, vss_id):
		wcd = win32com.client.Dispatch("WbemScripting.SWbemLocator")
		wmi = wcd.ConnectServer(".","root\cimv2")
		obj = wmi.ExecQuery(self.__get("WMI_Query").format(vss_id))
		return [x.DeviceObject for x in obj]

	def open(self):

		if self.opened:
			raise "The shadow copy already open"
		local_drives = get_local_drives()
		vss = dict()
		for local_drive in local_drives:

			vss[local_drive] = self.__create_shadow_copy(local_drive)
		self.vss = vss
		self.opened = True

	def __create_shadow_copy(self,drive_letter):

		wmi = win32com.client.GetObject(self.__get("WMI_Shadow_Copy"))
		createmethod = wmi.Methods_("Create")
		createparams = createmethod.InParameters
		createparams.Properties_[1].value = "{0}:\\".format(drive_letter)
		results = wmi.ExecMethod_("Create", createparams)
		return results.Properties_[1].value

	def __get_shadow_path(self, source):

		splited_source = source.split(":\\")
		drive = splited_source[0].upper()
		if not drive in self.vss.keys():
			raise "Unknown local drive"

		path = splited_source[1]
		shadow_path = self.__get_vss_by_id(self.vss[drive])
		full_path = os.path.join(shadow_path, path)
		return full_path

	def copy_file(self, source, destination):

		path = self.__get_shadow_path(source)
		try: shutil.copyfile(path,destination)
		except: return 1
		else: return 0

	def send_file(self, source, destination):

		path = self.get_shadow_path(source)
		# TODO: a module for sending with socket than use it here

	def __vss_delete(self, shadow_id):
		wcd = win32com.client.Dispatch("WbemScripting.SWbemLocator")
		wmi = wcd.ConnectServer(".", "root\cimv2")
		obj = wmi.ExecQuery(
			self.__get("WMI_Query").format(
				shadow_id))
		try: obj[0].Delete_()
		except: return 1
		else: return 0

	def close(self):

		if not self.opened:
			raise "There is no open shadow copy"
		result = 0
		for drive in self.vss.values():
			result = self.__vss_delete(drive) & result
		self.opened = False
		return 0

def get_local_drives():

	local_drives = win32api.GetLogicalDriveStrings()
	return re.findall("[A-Z]", local_drives)