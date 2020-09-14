import os
import win32com.client
import win32api
import re
import shutil

class files_utils():

	def __init__(self, file_path, shadow_copy):

		self.file_path = file_path
		self.shadow_copy = shadow_copy
		self.default_config = {
			"WMI_Query": "SELECT * FROM Win32_ShadowCopy where ID='{0}'".format(vss_id),
			"WMI_Shadow_Copy": "winmgmts:\\\\.\\root\\cimv2:Win32_ShadowCopy"
		}


	def get(self, key):

		return self.default_config[key]

	def get_vss_by_id(self, vss_id):
		wcd = win32com.client.Dispatch("WbemScripting.SWbemLocator")
		wmi = wcd.ConnectServer(".","root\cimv2")
		obj = wmi.ExecQuery(self.get("WMI_Query"))
		return [x.DeviceObject for x in obj]

	def open(self):

		local_drives = get_local_drives()
		vss = dict()
		for local_drive in local_drives:

			vss[local_drive] = self.create_shadow_copy(local_drive)
		self.vss = vss

	def create_shadow_copy(self,drive_letter):

		wmi = win32com.client.GetObject(self.get("WMI_Shadow_Copy"))
		createmethod = wmi.Methods_("Create")
		createparams = createmethod.InParameters
		createparams.Properties_[1].value = "{0}:\\".format(drive_letter)
		results = wmi.ExecMethod_("Create", createparams)
		return results.Properties_[1].value

	def copy_file(self, source, destination):

		splited_source = source.split(":\\")
		drive = splited_source[0].upper()
		if not drive in self.vss.keys():

			raise "Unknown local drive"

		path = splited_source[1]
		shadow_path = self.get_vss_by_id(self.vss[drive])
		full_path = os.path.join(shadow_path,path)
		try: shutil.copyfile(full_path,destination)
		except: return 1
		else: return 0

def get_local_drives():

	local_drives = win32api.GetLogicalDriveStrings()
	return re.findall("[A-Z]", local_drives)