import os
import win32com.client


def vss_list():
	wcd = win32com.client.Dispatch("WbemScripting.SWbemLocator")
	wmi = wcd.ConnectServer(".","root\cimv2")
	obj = wmi.ExecQuery("SELECT * FROM Win32_ShadowCopy")
	return [x.DeviceObject for x in obj]def vss_list():
	wcd = win32com.client.Dispatch("WbemScripting.SWbemLocator")
	wmi = wcd.ConnectServer(".","root\cimv2")
	obj = wmi.ExecQuery("SELECT * FROM Win32_ShadowCopy")
	return [x.DeviceObject for x in obj]

def create_shadow_volume(local_drives):

    return vss.ShadowCopy(local_drives)

def get_shadow_copy