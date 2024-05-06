#include <stdio.h>
#include <string.h>

#include "adt_srv_processcmd.h"
#include "adt_uart.h"
#include "adt_wifi_driver.h"
#include "adt_aht20.h"
#include "adt_irTx.h"
#include "adt_irRx.h"
#include "adt_eventHandler.h"
#include "adt_srv_onboarding.h"
#include "adt_cJSON.h"
#include "adt_httpc.h"
#include "adt_ota.h"
// #include "adt_mqtt.h"
#include "adt_awsMqtt.h"
#include "adt_httpd.h"

#define ADT_C_CMD_DELIM_TYPE ';'
#define ADT_C_CMD_DELIM_DATA '-'

#define ADT_C_FAC_HUMI_Y1	adt_deviceData.adt_calibrationData_Set[adt_enum_sensor_humidity][adt_enum_calibrationpoint_low]
#define ADT_C_FAC_HUMI_Y2	adt_deviceData.adt_calibrationData_Set[adt_enum_sensor_humidity][adt_enum_calibrationpoint_mid]
#define ADT_C_FAC_HUMI_Y3	adt_deviceData.adt_calibrationData_Set[adt_enum_sensor_humidity][adt_enum_calibrationpoint_high]
#define ADT_C_FAC_HUMI_X1	adt_deviceData.adt_calibrationData_Read[adt_enum_sensor_humidity][adt_enum_calibrationpoint_low]
#define ADT_C_FAC_HUMI_X2	adt_deviceData.adt_calibrationData_Read[adt_enum_sensor_humidity][adt_enum_calibrationpoint_mid]
#define ADT_C_FAC_HUMI_X3	adt_deviceData.adt_calibrationData_Read[adt_enum_sensor_humidity][adt_enum_calibrationpoint_high]

#define ADT_C_FAC_TEMP_Y1	adt_deviceData.adt_calibrationData_Set[adt_enum_sensor_temperature][adt_enum_calibrationpoint_low]
#define ADT_C_FAC_TEMP_Y2	adt_deviceData.adt_calibrationData_Set[adt_enum_sensor_temperature][adt_enum_calibrationpoint_mid]
#define ADT_C_FAC_TEMP_Y3	adt_deviceData.adt_calibrationData_Set[adt_enum_sensor_temperature][adt_enum_calibrationpoint_high]
#define ADT_C_FAC_TEMP_X1	adt_deviceData.adt_calibrationData_Read[adt_enum_sensor_temperature][adt_enum_calibrationpoint_low]
#define ADT_C_FAC_TEMP_X2	adt_deviceData.adt_calibrationData_Read[adt_enum_sensor_temperature][adt_enum_calibrationpoint_mid]
#define ADT_C_FAC_TEMP_X3	adt_deviceData.adt_calibrationData_Read[adt_enum_sensor_temperature][adt_enum_calibrationpoint_high]

#define ADT_C_USER_HUMI_I1	adt_applicationData.adt_calibrationData_Int[adt_enum_sensor_humidity][adt_enum_offsetpoint_low]
#define ADT_C_USER_HUMI_I2	adt_applicationData.adt_calibrationData_Int[adt_enum_sensor_humidity][adt_enum_offsetpoint_mid]
#define ADT_C_USER_HUMI_I3	adt_applicationData.adt_calibrationData_Int[adt_enum_sensor_humidity][adt_enum_offsetpoint_high]
#define ADT_C_USER_HUMI_E1	adt_applicationData.adt_calibrationData_Ext[adt_enum_sensor_humidity][adt_enum_offsetpoint_low]
#define ADT_C_USER_HUMI_E2	adt_applicationData.adt_calibrationData_Ext[adt_enum_sensor_humidity][adt_enum_offsetpoint_mid]
#define ADT_C_USER_HUMI_E3	adt_applicationData.adt_calibrationData_Ext[adt_enum_sensor_humidity][adt_enum_offsetpoint_high]

#define ADT_C_USER_TEMP_I1	adt_applicationData.adt_calibrationData_Int[adt_enum_sensor_temperature][adt_enum_offsetpoint_low]
#define ADT_C_USER_TEMP_I2	adt_applicationData.adt_calibrationData_Int[adt_enum_sensor_temperature][adt_enum_offsetpoint_mid]
#define ADT_C_USER_TEMP_I3	adt_applicationData.adt_calibrationData_Int[adt_enum_sensor_temperature][adt_enum_offsetpoint_high]
#define ADT_C_USER_TEMP_E1	adt_applicationData.adt_calibrationData_Ext[adt_enum_sensor_temperature][adt_enum_offsetpoint_low]
#define ADT_C_USER_TEMP_E2	adt_applicationData.adt_calibrationData_Ext[adt_enum_sensor_temperature][adt_enum_offsetpoint_mid]
#define ADT_C_USER_TEMP_E3	adt_applicationData.adt_calibrationData_Ext[adt_enum_sensor_temperature][adt_enum_offsetpoint_high]

int8_t adt_srv_processCmd (uint32_t adt_commandType, char *pcommandString)
{
//	uint8_t commandtype, commanddeliminator;
//	uint8_t maxcommandlength = 10;
//	uint8_t adt_command[maxcommandlength];

//	uint16_t maxdatalength = 128;//(128 + 64);
//	char adt_data[maxdatalength];
	char *adt_data;

	char *pdelimPos;
	bool uartrespond = 0;
//	uint8_t *pdataPos;
//	uint32_t in1, in2, in3;

	if (strlen(pcommandString) <= 2)
	{
		adt_util_printf(__LINE__, __FILE_NAME__, "Invalid length");
		return -1;
	}

	adt_util_printf(__LINE__, __FILE_NAME__, "%s", pcommandString);

	if (*(pcommandString + 1) == ADT_C_CMD_DELIM_TYPE)
	{
		switch (*pcommandString)
		{
		case '1':
			adt_commandType = 1;
			break;

		case '2':
			adt_commandType = 2;
			break;

		case '3':
			adt_commandType = 3;
			break;

		case '4':
			adt_commandType = 4;
			break;

		default:
			return -1;
		}

		pcommandString = pcommandString + 2;

		uartrespond = true;
	}
	else
	{
		uartrespond = false;
	}

	// if (xSemaphoreTake(adtprocesscommand_sema, (500/portTICK_RATE_MS)) == pdFALSE)
	// {
	// 	return -1;
	// }

	switch (adt_commandType)
	{
		case 1: //WiFi SSID
			strncpy(adt_wifiSSID, pcommandString, ADT_C_WIFI_SSID_BYTESIZE);
			adt_util_printf(__LINE__, __FILE_NAME__, "@ADT-WiFi SSID = %s",adt_wifiSSID);

			if (uartrespond == true)
			{
				adt_data = malloc(128);
				snprintf(adt_data, 128, "1:%s",adt_wifiSSID);
				adt_sendData_uarttx(adt_data);
				free(adt_data);
			}
			break;
		
		case 2: //WiFi Password
			strncpy(adt_wifiPassword, pcommandString, ADT_C_WIFI_PASSWORD_BYTESIZE);
			adt_util_printf(__LINE__, __FILE_NAME__, "@ADT-WiFi Password = %s",adt_wifiPassword);

			if (uartrespond == true)
			{
				adt_data = malloc(128);
				snprintf(adt_data, 128, "2:%s",adt_wifiPassword);
				adt_sendData_uarttx(adt_data);
				free(adt_data);
			}
			break;

		case 3:
			pdelimPos = strchr(pcommandString, ADT_C_CMD_DELIM_DATA);
			if (pdelimPos == 0) //not found
			{
				/***			WiFi Action 			***/

				if (strncmp(pcommandString,"connectwifi",strlen(pcommandString)) == 0)
				{
					adt_util_printf(__LINE__, __FILE_NAME__, ".......... Run Connect WiFi ..........");
					adt_set_wifi_connection(NULL);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
				}
				else if (strncmp(pcommandString,"disconnectwifi",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"erasewifi",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"showwifi",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"startap",strlen(pcommandString)) == 0)
				{
				}

				/***			System Action 			***/

				else if (strncmp(pcommandString,"exit",strlen(pcommandString)) == 0)
				{
					return 2;
				}
				else if (strncmp(pcommandString,"reboot",strlen(pcommandString)) == 0)
				{
					adt_util_rebootDevice();
				}
				else if (strncmp(pcommandString,"factoryRST",strlen(pcommandString)) == 0) //factoryreset
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
					}

//					adt_util_factoryReset(); // add 231123 Fazreen,adt factory reset
//					factory_reset(); // add 231123 Fazreen,Matter factory reset

//					adt_util_rebootDevice();

					adt_eventPost(ADT_EVENT_SYSTEM,ADT_EVENT_FACTORY_RESET,NULL,0);

				}
				// Added new command for device reset (factoryRST --> resetDevice)
				else if (strncmp(pcommandString,"resetDevice",strlen(pcommandString)) == 0) //factoryreset
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
					}

//					adt_util_factoryReset(); // add 231123 Fazreen,adt factory reset
//					factory_reset(); // add 231123 Fazreen,Matter factory reset

//					adt_util_rebootDevice();

					adt_eventPost(ADT_EVENT_SYSTEM, ADT_EVENT_FACTORY_RESET, NULL, NULL);

				} 

				else if (strncmp(pcommandString,"sensorTemp?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %.2f",pcommandString, adt_get_aht20_temperatureFloat());
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %.2f",pcommandString, adt_get_aht20_temperatureFloat());
//					}
				}
				else if (strncmp(pcommandString,"sensorRawTemp?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %lX",pcommandString, adt_get_aht20_temperatureData());
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %lX",pcommandString, adt_get_aht20_temperatureData());
//					}
				}
				else if (strncmp(pcommandString,"sensorHumi?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %.2f",pcommandString, adt_get_aht20_humidityFloat());
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %.2f",pcommandString, adt_get_aht20_humidityFloat());
//					}
				}
				else if (strncmp(pcommandString,"sensorRawHumi?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %lX",pcommandString, adt_get_aht20_humidityData());
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %lX",pcommandString, adt_get_aht20_humidityData());
//					}
				}
				else if (strncmp(pcommandString,"sensorTempHex?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %#lX",pcommandString, adt_get_aht20_temperatureUint32());
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
					}
				}
				else if (strncmp(pcommandString,"sensorHumiHex?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %#lX",pcommandString, adt_get_aht20_humidityUint32());
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
					}
				}
				else if (strncmp(pcommandString,"485Address?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %2X",pcommandString, adt_deviceData.adt_rs485Address);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
					}
				}
				else if (strncmp(pcommandString,"revertFW",strlen(pcommandString)) == 0)
				{

				} 
				else if (strncmp(pcommandString,"newFW",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"MTQRS?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %s",pcommandString, adt_deviceData.adt_matterQRString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %s",pcommandString, adt_deviceData.adt_matterQRString);
//					}
				}
				else if (strncmp(pcommandString,"PRD?",strlen(pcommandString)) == 0)
				{
//					if (strlen(adt_deviceData.adt_productName) > 2)
//					{
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s = %s",pcommandString, adt_deviceData.adt_productName);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						else
						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %s",pcommandString, adt_deviceData.adt_productName);
						}
//					}
//					else
//					{
//
//					}
				}
				else if (strncmp(pcommandString,"DID?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %s",pcommandString, adt_applicationData.adt_deviceUserID);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %s",pcommandString, adt_applicationData.adt_deviceUserID);
					}
				}
				else if (strncmp(pcommandString,"FWV?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						// snprintf(adt_data, 128, "3:%s = %d.%d.%d",pcommandString, adt_fwVersion_major, adt_fwVersion_minor, adt_fwVersion_build);
						snprintf(adt_data, 128, "3:%s = %s",pcommandString, adt_fwVersionString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
						// adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %d.%d.%d",pcommandString, adt_fwVersion_major, adt_fwVersion_minor, adt_fwVersion_build);
						snprintf(adt_data, 128, "3:%s = %s",pcommandString, adt_fwVersionString);
					}
				}
				else if (strncmp(pcommandString,"HWV?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						// snprintf(adt_data, 128, "3:%s = %d.%d.%d",pcommandString, adt_deviceData.adt_hwVersion_major, adt_deviceData.adt_hwVersion_minor, adt_deviceData.adt_hwVersion_build);
						snprintf(adt_data, 128, "3:%s = %s",pcommandString, adt_hwVersionString); 
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
						// adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %d.%d.%d",pcommandString, adt_deviceData.adt_hwVersion_major, adt_deviceData.adt_hwVersion_minor, adt_deviceData.adt_hwVersion_build);
						snprintf(adt_data, 128, "3:%s = %s",pcommandString, adt_hwVersionString); 
					}
				}
				else if (strncmp(pcommandString,"SRN?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s = %s",pcommandString, adt_deviceData.adt_serialNumber);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %s",pcommandString, adt_deviceData.adt_serialNumber);
					}
				}
				else if (strncmp(pcommandString,"SSID?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						if (strlen(adt_wifiSSID) < ADT_C_WIFI_SSID_BYTESIZE)
						{
							snprintf(adt_data, 128, "3:%s = %s",pcommandString, adt_wifiSSID);
						}
						else
						{
							snprintf(adt_data, 128, "3:%s = Invalid!",pcommandString);
						}
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
						if (strlen(adt_wifiSSID) < ADT_C_WIFI_SSID_BYTESIZE)
						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %s",pcommandString, adt_wifiSSID);
						}
						else
						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = Invalid!",pcommandString);
						}
					}
				}
				else if (strncmp(pcommandString,"deviceinfo",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"current_state",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"current_status",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"test_bcastM",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"test_httpc",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"test_buttonshort",strlen(pcommandString)) == 0)
				{
					adt_data = malloc(128);
					snprintf(adt_data, 128, "3:%s = pressed",pcommandString);
					adt_sendData_uarttx(adt_data);
					free(adt_data);
				}
				else if (strncmp(pcommandString,"test_buttonlong",strlen(pcommandString)) == 0)
				{
					adt_data = malloc(128);
					snprintf(adt_data, 128, "3:%s = pressed",pcommandString);
					adt_sendData_uarttx(adt_data);
					free(adt_data);
				}
				else if (strncmp(pcommandString,"saveDevData",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_SYSTEM, ADT_EVENT_NVS_ADT0_WRITE,NULL,0);
				}
				else if (strncmp(pcommandString,"saveAppData",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_SYSTEM, ADT_EVENT_NVS_ADT1_WRITE,NULL,0);
				}
				else if (strncmp(pcommandString,"readDevData",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_SYSTEM,ADT_EVENT_NVS_ADT0_READ,NULL,0);
				}
				else if (strncmp(pcommandString,"readAppData",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_SYSTEM,ADT_EVENT_NVS_ADT1_READ,NULL,0);
				}
				else if (strncmp(pcommandString,"deleteDevData",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_SYSTEM,ADT_EVENT_NVS_ADT0_DELETE,NULL,0);
				}
				else if (strncmp(pcommandString,"deleteAppData",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_SYSTEM,ADT_EVENT_NVS_ADT1_DELETE,NULL,0);
				}
				else if (strncmp(pcommandString,"debugHeap",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_SYSTEM,ADT_EVENT_DEBUG_HEAP,NULL,0);
				}
				else if (strncmp(pcommandString,"secureCert",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_SYSTEM,ADT_EVENT_SECURE_CERT_READ,NULL,0);
				}
				else if (strncmp(pcommandString,"facCalibData?",strlen(pcommandString)) == 0)
				{
					// int i,j,k;
					int i,j;

					if (uartrespond == true)
					{
						adt_data = malloc(256);

						for (i = 0; i < adt_enum_sensor_max; i++)
						{
							for (j = 0; j < adt_enum_calibrationpoint_max; j++)
							{
								snprintf(adt_data, 256, "3:%s = [%d][%d][set]:%f",pcommandString, i, j, adt_deviceData.adt_calibrationData_Set[i][j]);
								adt_sendData_uarttx(adt_data);

								snprintf(adt_data, 256, "3:%s = [%d][%d][reading]:%lX",pcommandString, i, j, adt_deviceData.adt_calibrationData_Read[i][j]);
								adt_sendData_uarttx(adt_data);
							}
						}

						free(adt_data);
					}
//					else
//					{
						for (i = 0; i < adt_enum_sensor_max; i++)
						{
							for (j = 0; j < adt_enum_calibrationpoint_max; j++)
							{
								adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = [%d][%d][set]:%f",pcommandString, i, j, adt_deviceData.adt_calibrationData_Set[i][j]);

								adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = [%d][%d][reading]:%lX",pcommandString, i, j, adt_deviceData.adt_calibrationData_Read[i][j]);
							}
						}
//					}
				}
				else if (strncmp(pcommandString,"userCalibData?",strlen(pcommandString)) == 0)
				{
					// int i,j,k;
					int i,j;

					if (uartrespond == true)
					{
						adt_data = malloc(256);

						for (i = 0; i < adt_enum_sensor_max; i++)
						{
							for (j = 0; j < adt_enum_calibrationpoint_max; j++)
							{
								snprintf(adt_data, 256, "3:%s = [%d][%d][set]:%f",pcommandString, i, j, adt_applicationData.adt_calibrationData_Ext[i][j]);
								adt_sendData_uarttx(adt_data);

								snprintf(adt_data, 256, "3:%s = [%d][%d][reading]:%f",pcommandString, i, j, adt_applicationData.adt_calibrationData_Int[i][j]);
								adt_sendData_uarttx(adt_data);
							}
						}

						free(adt_data);
					}
//					else
//					{
						for (i = 0; i < adt_enum_sensor_max; i++)
						{
							for (j = 0; j < adt_enum_calibrationpoint_max; j++)
							{
								adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = [%d][%d][set]:%f",pcommandString, i, j, adt_applicationData.adt_calibrationData_Ext[i][j]);

								adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = [%d][%d][reading]:%f",pcommandString, i, j, adt_applicationData.adt_calibrationData_Int[i][j]);
							}
						}
//					}
				}
//				else if (strncmp(pcommandString,"postlearn",strlen(pcommandString)) == 0)
//				{
//					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IRRX_SEND_DATA,NULL,0);
//					if (uartrespond == true)
//					{
//						adt_data = malloc(128);
//						snprintf(adt_data, 128, "3:%s",pcommandString);
//						adt_sendData_uarttx(adt_data);
//						free(adt_data);
//					}
//					else
//					{
//					}
//				}
				else if (strncmp(pcommandString,"matterclosecommissionwindow",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_SYSTEM,ADT_EVENT_MATTER_CLOSECOMMISSIONWINDOW,NULL,0);
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
					}
				}


				/***			IR Action 			***/

				else if (strncmp(pcommandString,"on_ac",strlen(pcommandString)) == 0)
				{
					kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 1; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
											// you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"off_ac",strlen(pcommandString)) == 0)
				{
					kk_controlACPower = 1; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 1; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"cool_mode",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					kk_controlACMode = 0; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 2; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"heat_mode",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					kk_controlACMode = 1; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 2; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}

				}
				else if (strncmp(pcommandString,"auto_mode",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 2; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"fan_mode",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					kk_controlACMode = 3; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 2; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"dry_mode",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					kk_controlACMode = 4; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 2; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"auto_fan",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					kk_controlACWindSpeeds = 0; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 5; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"turbo_fan",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					kk_controlACWindSpeeds = 3; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 5; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"high_fan",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					kk_controlACWindSpeeds = 3; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 5; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"med_fan",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					kk_controlACWindSpeeds = 2; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 5; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"low_fan",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					kk_controlACWindSpeeds = 1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 5; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"quiet_fan",strlen(pcommandString)) == 0)
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					kk_controlACWindSpeeds = 1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 5; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"on_vflap",strlen(pcommandString)) == 0) //on_vlouver
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 6; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"off_vflap",strlen(pcommandString)) == 0) //off_vlouver
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 6; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"top_vflap",strlen(pcommandString)) == 0) //off_vlouver
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 6; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"bottom_vflap",strlen(pcommandString)) == 0) //off_vlouver
				{
					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					// kk_controlACTemperature = -1; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 6; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
                                             // you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"on_hflap",strlen(pcommandString)) == 0) //on_hlouver
				{

				}
				else if (strncmp(pcommandString,"off_hflap",strlen(pcommandString)) == 0) //off_hlouver
				{

				}
				else if (strncmp(pcommandString,"left_hflap",strlen(pcommandString)) == 0) //off_hlouver
				{

				}
				else if (strncmp(pcommandString,"midleft_hflap",strlen(pcommandString)) == 0) //off_hlouver
				{

				}
				else if (strncmp(pcommandString,"mid_hflap",strlen(pcommandString)) == 0) //off_hlouver
				{

				}
				else if (strncmp(pcommandString,"midright_hflap",strlen(pcommandString)) == 0) //off_hlouver
				{
					
				}
				else if (strncmp(pcommandString,"right_hflap",strlen(pcommandString)) == 0) //off_hlouver
				{

				}
				else if (strncmp(pcommandString,"irdevconf?",strlen(pcommandString)) == 0)
				{
					if (uartrespond == true)
					{
						adt_data = malloc(1024 + 256);
						snprintf(adt_data, (1024 + 256), "3:%s = %s",pcommandString, adt_applicationData.adt_irACHexData[adt_active_irdev]);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s = %s",pcommandString, adt_applicationData.adt_irACHexData[adt_active_irdev]);
					}
				}
				else if (strncmp(pcommandString,"learn",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_AC_AUTO_DETECT,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"auto_detect",strlen(pcommandString)) == 0) // H3.32 Start IRRX
				{
					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_AC_AUTO_DETECT,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					// else
					// {
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
					// }
				}

			}
			else //found
			{
				adt_util_printf(__LINE__, __FILE_NAME__, "Found data deliminator");
				adt_util_printf(__LINE__, __FILE_NAME__, "data = %s", (pdelimPos + 1));
				*pdelimPos = '\0';

				/***			WiFi Action 			***/

				if (strncmp(pcommandString,"hello",strlen(pcommandString)) == 0)
				{

				}

				/***			System Action 			***/

				else if (strncmp(pcommandString,"upgradeFW",strlen(pcommandString)) == 0) //upgradefirmware //doublecheck this message
				{
					printf("WOOIIIIIIIIIIIIIIII\n\n");
					
					if (strncmp((pdelimPos + 1),"aws",strlen((pdelimPos + 1))) == 0)
					{
						adt_deletetask_mqtt();
						adt_deletetask_httpd();
						adt_createtask_awsota();
					}
					else if (strncmp((pdelimPos + 1),"auto",strlen((pdelimPos + 1))) == 0)
					{
					}
					else if (strncmp((pdelimPos + 1),"local",strlen((pdelimPos + 1))) == 0)
					{
					}
					else if (strncmp((pdelimPos + 1),"http",strlen((pdelimPos + 1))) == 0) 
					{
					}
					else
					{
						if (strlen((pdelimPos + 1)) > 0)
						{
							if (strchr((pdelimPos + 1),'[') != NULL)
							{
								if (strchr((pdelimPos + 1),']') != NULL)
								{
								}
							}
						}
					}
				}
				else if (strncmp(pcommandString,"FileIDFW",strlen(pcommandString)) == 0) //Firmware file ID required for OTA over HTTP
				{
					//info 20240110 soo, this command is meant for BW16 ota over http download
				}
				else if (strncmp(pcommandString,"debugData",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"eraseData",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"flash",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"485Address",strlen(pcommandString)) == 0)
				{
					unsigned int address;
					int ret;

					ret = sscanf((pdelimPos + 1),"%2X", &address);
					if (ret == 1)
					{
						adt_deviceData.adt_rs485Address = address;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%2X",pcommandString, ADT_C_CMD_DELIM_DATA, adt_deviceData.adt_rs485Address);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						else
						{
						}
					}
				}
				else if (strncmp(pcommandString,"MTQRS",strlen(pcommandString)) == 0)
				{
					char* data = (char*) malloc(256);
					int ret;

					ret = sscanf((pdelimPos + 1),"%s", data);
					if (ret == 1)
					{
						strncpy(adt_deviceData.adt_matterQRString,data,ADT_C_MATTERQRSTRING_BTYESIZE);
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_deviceData.adt_matterQRString);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						else
						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_deviceData.adt_matterQRString);
						}
					}

					free(data);
				}
				else if (strncmp(pcommandString,"PRD",strlen(pcommandString)) == 0)
				{
					char* data = (char*) malloc(256);
					int ret;

					ret = sscanf((pdelimPos + 1),"%s", data);
					if (ret == 1)
					{
						strncpy(adt_deviceData.adt_productName,data,ADT_C_PRODUCT_NAME_BYTESIZE);
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_deviceData.adt_productName);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						else
						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_deviceData.adt_productName);
						}
					}

					free(data);
				}
				else if (strncmp(pcommandString,"DID",strlen(pcommandString)) == 0)
				{
					char* data = (char*) malloc(256);
					int ret;

					ret = sscanf((pdelimPos + 1),"%s", data);
					if (ret == 1)
					{
						strncpy(adt_applicationData.adt_deviceUserID,data,ADT_C_DEVICEUSERID_BTYESIZE);
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_applicationData.adt_deviceUserID);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						else
						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_applicationData.adt_deviceUserID);
						}
					}

					free(data);
				}
				else if (strncmp(pcommandString,"HWV",strlen(pcommandString)) == 0)
				{
					char* data = (char*) malloc(256);
					int ret;

					ret = sscanf((pdelimPos + 1),"%s", data);
					if (ret == 1)
					{
						strncpy(adt_hwVersionString,data,ADT_C_HW_VER_STRING_BYTESIZE);
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_hwVersionString);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						else
						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_hwVersionString);
						}
					}

					free(data);
				}
				else if (strncmp(pcommandString,"SRN",strlen(pcommandString)) == 0)
				{
					char* data = (char*) malloc(ADT_C_SRN_NUM_ARRAYSIZE);
					int ret;

					ret = sscanf((pdelimPos + 1),"%s", data);
					if (ret == 1)
					{
						strncpy(adt_deviceData.adt_serialNumber,data,ADT_C_SRN_NUM_ARRAYSIZE);
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_deviceData.adt_serialNumber);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						else
						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%s",pcommandString, ADT_C_CMD_DELIM_DATA, adt_deviceData.adt_serialNumber);
						}
					}

					free(data);
				}
				else if (strncmp(pcommandString,"Debug0",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"AID",strlen(pcommandString)) == 0)
				{
				}
				else if (strncmp(pcommandString,"facCalibData_Humi_1",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					uint32_t data2;

					ret = sscanf((pdelimPos + 1),"%f,%lX", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_FAC_HUMI_Y1 = data1;
						ADT_C_FAC_HUMI_X1 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%lX", pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_HUMI_Y1, ADT_C_FAC_HUMI_X1);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						//						else
						//						{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%lX", pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_HUMI_Y1, ADT_C_FAC_HUMI_X1);
						//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"facCalibData_Humi_2",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					uint32_t data2;

					ret = sscanf((pdelimPos + 1),"%f,%lX", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_FAC_HUMI_Y2 = data1;
						ADT_C_FAC_HUMI_X2 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%lX",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_HUMI_Y2, ADT_C_FAC_HUMI_X2);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%lX",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_HUMI_Y2, ADT_C_FAC_HUMI_X2);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"facCalibData_Humi_3",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					uint32_t data2;

					ret = sscanf((pdelimPos + 1),"%f,%lX", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_FAC_HUMI_Y3 = data1;
						ADT_C_FAC_HUMI_X3 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%lX",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_HUMI_Y3, ADT_C_FAC_HUMI_X3);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%lX",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_HUMI_Y3, ADT_C_FAC_HUMI_X3);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"facCalibData_Temp_1",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					uint32_t data2;

					ret = sscanf((pdelimPos + 1),"%f,%lX", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_FAC_TEMP_Y1 = data1;
						ADT_C_FAC_TEMP_X1 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%lX",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_TEMP_Y1, ADT_C_FAC_TEMP_X1);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						//						else
						//						{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%lX",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_TEMP_Y1, ADT_C_FAC_TEMP_X1);
						//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"facCalibData_Temp_2",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					uint32_t data2;

					ret = sscanf((pdelimPos + 1),"%f,%lX", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_FAC_TEMP_Y2 = data1;
						ADT_C_FAC_TEMP_X2 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%lX",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_TEMP_Y2, ADT_C_FAC_TEMP_X2);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_TEMP_Y2, ADT_C_FAC_TEMP_X2);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"facCalibData_Temp_3",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					uint32_t data2;

					ret = sscanf((pdelimPos + 1),"%f,%lX", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_FAC_TEMP_Y3 = data1;
						ADT_C_FAC_TEMP_X3 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%lX",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_TEMP_Y3, ADT_C_FAC_TEMP_X3);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_FAC_TEMP_Y3, ADT_C_FAC_TEMP_X3);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"userCalibData_Humi_1",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					float data2;

					ret = sscanf((pdelimPos + 1),"%f,%f", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_USER_HUMI_E1 = data1;
						ADT_C_USER_HUMI_I1 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_HUMI_E1, ADT_C_USER_HUMI_I1);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_HUMI_E1, ADT_C_USER_HUMI_I1);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"userCalibData_Humi_2",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					float data2;

					ret = sscanf((pdelimPos + 1),"%f,%f", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_USER_HUMI_E2 = data1;
						ADT_C_USER_HUMI_I2 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_HUMI_E2, ADT_C_USER_HUMI_I2);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_HUMI_E2, ADT_C_USER_HUMI_I2);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"userCalibData_Humi_3",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					float data2;

					ret = sscanf((pdelimPos + 1),"%f,%f", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_USER_HUMI_E3 = data1;
						ADT_C_USER_HUMI_I3 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_HUMI_E3, ADT_C_USER_HUMI_I3);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_HUMI_E3, ADT_C_USER_HUMI_I3);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"userCalibData_Temp_1",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					float data2;

					ret = sscanf((pdelimPos + 1),"%f,%f", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_USER_TEMP_E1 = data1;
						ADT_C_USER_TEMP_I1 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_TEMP_E1, ADT_C_USER_TEMP_I1);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
							adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_TEMP_E1, ADT_C_USER_TEMP_I1);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"userCalibData_Temp_2",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					float data2;

					ret = sscanf((pdelimPos + 1),"%f,%f", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_USER_TEMP_E2 = data1;
						ADT_C_USER_TEMP_I2 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_TEMP_E2, ADT_C_USER_TEMP_I2);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_TEMP_E2, ADT_C_USER_TEMP_I2);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}
				else if (strncmp(pcommandString,"userCalibData_Temp_3",strlen(pcommandString)) == 0)
				{
					int ret;
					float data1;
					float data2;

					ret = sscanf((pdelimPos + 1),"%f,%f", &data1, &data2);
					if (ret == 2)
					{
						ADT_C_USER_TEMP_E3 = data1;
						ADT_C_USER_TEMP_I3 = data2;
						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_TEMP_E3, ADT_C_USER_TEMP_I3);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
//						else
//						{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%c%f,%f",pcommandString, ADT_C_CMD_DELIM_DATA, ADT_C_USER_TEMP_E3, ADT_C_USER_TEMP_I3);
//						}
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}

				/***			Factory for LED 			***/
				else if (strncmp(pcommandString,"RGB",strlen(pcommandString)) == 0)
				{
					char *RGBchar=pdelimPos+1;
					// adt_util_printf(__LINE__, __FILE_NAME__, "RGB code is %s\n",RGBchar);
					int RGB=*RGBchar - '0';
					// adt_util_printf(__LINE__, __FILE_NAME__, "RGB code is %d\n",RGB);
					adt_eventPost(ADT_EVENT_LED, ADT_EVENT_FACTORY,&RGB,sizeof(int));
					if (RGB==1)
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "Factory Mode LED RGB Test : Red");
					}else if(RGB==2)
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "Factory Mode LED RGB Test : GREEN");
					}else{
						adt_util_printf(__LINE__, __FILE_NAME__, "Factory Mode LED RGB Test : BLUE");
					}
						
					
				}

				/***			IR Action 			***/

				else if (strncmp(pcommandString,"send",strlen(pcommandString)) == 0)
				{
	
				}
				else if (strncmp(pcommandString,"temp",strlen(pcommandString)) == 0)
				{
					int32_t temp;

					adt_util_convertFloatString2Int32((pdelimPos + 1), &temp);
					if (temp < 16)
						temp = 16;

					if (temp > 30)
						temp = 30;

					// kk_controlACPower = 0; // power: power state[0 power on, 1 power off]
					// kk_controlACMode = 2; // mode: mode state[0 cool, 1 heat, 2 auto, 3 air supply, 4 dry]
					kk_controlACTemperature = (int8_t)temp; // temperature: temperature[16-30], pass -1 if the temperature can not be adjusted for the current mode
					// kk_controlACWindSpeeds = -1; // wind_speed: wind_speed[0 auto, 1 low, 2 medium, 3 high], pass -1 if the wind speed can not be adjusted for the current mode
					// kk_controlACWindDirect = 0; // wind_direct: up and down wind direction, please refer to comments of parameter wind_direct_flag of get_ac_info api
					kk_controlACPressedFID = 3; // pressed_fid: the key pressed on physical remote controller [power 1, mode 2, temperature+ 3, temperature- 4, wind speed 5, swing wind 6, fixed wind 7, if there is only one ir code for up and down wind direction, pass 7]
											// you'd better to pass a determined value, if you are not sure, pass 0, but some ac remote controller may have problem

					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
//					else
//					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
//					}
				}
				else if (strncmp(pcommandString,"runStatus",strlen(pcommandString)) == 0)
				{
					adt_util_printf(__LINE__, __FILE_NAME__,"runStatus = %s",(pdelimPos + 1)); 
                    adt_parse_json_runStatus(pdelimPos + 1);
					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);
				}
				else if (strncmp(pcommandString,"irdevconf",strlen(pcommandString)) == 0)
				{
					// adt_util_printf(__LINE__, __FILE_NAME__,"Testing");
					// adt_util_printf(__LINE__, __FILE_NAME__,"Full data received %s",pdelimPos+1);

					// strncpy(adt_applicationData.adt_hexDataIRName[adt_active_irdev], (pdelimPos + 1), (strlen(pdelimPos + 1) + 1));

					// memset(pACHexDataName,'\0',strlen(pACHexDataName));

					// Find the position of the first occurrence of '-' character
    				const char *delimiterPos = strchr(pdelimPos+1, '-');
					if (delimiterPos != NULL) 
					{
						// ------------------Extract AC Hex Data---------------------
						// Calculate the length of the adt_irACHexDataName before the delimiter
						int adt_irACHexDataLength = delimiterPos - (pdelimPos+1);
						
						char *adt_irACHexData = (char *)malloc(adt_irACHexDataLength + 1); // +1 for null terminator
						strncpy(adt_irACHexData, pdelimPos+1, adt_irACHexDataLength);
						adt_irACHexData[adt_irACHexDataLength] = '\0'; // Null terminator
						// adt_util_printf(__LINE__, __FILE_NAME__, "Extracted adt_irACHexData: %s\n", adt_irACHexData);
						strncpy(adt_applicationData.adt_irACHexData[adt_active_irdev], adt_irACHexData, ADT_C_IR_AC_HEX_DATA_BYTESIZE);
						free(adt_irACHexData);

						// -------------------Extract AC Hex Name---------------------
						// Calculate the length of the adt_irACHexDataName after the delimiter
						int adt_irACHexDataNameLength = strlen(delimiterPos + 1);

						char *adt_irACHexDataName = (char *)malloc(adt_irACHexDataNameLength + 1); // +1 for null terminator
						strncpy(adt_irACHexDataName, delimiterPos + 1, adt_irACHexDataNameLength);
						adt_irACHexDataName[adt_irACHexDataNameLength] = '\0'; // Null terminator
						// adt_util_printf(__LINE__, __FILE_NAME__, "Extracted adt_irACHexDataName: %s\n", adt_irACHexDataName);
						strncpy(adt_applicationData.adt_hexDataIRName[adt_active_irdev], adt_irACHexDataName, ADT_C_IR_AC_HEX_DATA_NAME_BYTESIZE);
						free(adt_irACHexDataName);
					} else 
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "Delimiter '-' not found in the text.\n");
						strncpy(adt_applicationData.adt_irACHexData[adt_active_irdev], pdelimPos+1, ADT_C_IR_AC_HEX_DATA_BYTESIZE);
						strncpy(adt_applicationData.adt_hexDataIRName[adt_active_irdev], "No AC Defination Name", ADT_C_IR_AC_HEX_DATA_NAME_BYTESIZE);
					}
					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_GET_AC_DEF,NULL,0);
				}
				else if (strncmp(pcommandString,"auto_detect",strlen(pcommandString)) == 0) // H3.32 Start IRRX
				{
					int ret;
					uint64_t nosignal_timeout;
					int64_t onsignal_timeout;

					ret = sscanf((pdelimPos + 1),"%llu,%lld", &nosignal_timeout, &onsignal_timeout);
					if (ret == 2)
					{
						adt_set_irRx_nosignal_timeout(nosignal_timeout);
						adt_set_irRx_onsignal_timeout(onsignal_timeout);

						adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_AC_AUTO_DETECT,NULL,0);

						if (uartrespond == true)
						{
							adt_data = malloc(128);
							snprintf(adt_data, 128, "3:%s",pcommandString);
							adt_sendData_uarttx(adt_data);
							free(adt_data);
						}
						// else
						// {
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
						// }
					}
					else
					{
						adt_util_printf(__LINE__, __FILE_NAME__, "3:%s%cInvalid!", pcommandString, ADT_C_CMD_DELIM_DATA);
					}
				}


				/************************************************************************************************************************/
				/*
				* @brief New MQTT Command String!!
				* Commands: 1. setState
				*           2. setIRDef
				*           3. getAutoDetectSignal
				*           4. getLearnSignal
				*           5. getDeviceState
				*           6. getDeviceState
				*           7. resetDevice
				*/
				else if (strncmp (pcommandString, "setState", strlen(pcommandString)) == 0)
				{
					adt_util_printf(__LINE__, __FILE_NAME__,"setState = %s",(pdelimPos + 1)); 
                    adt_parse_json_runStatus(pdelimPos + 1);
					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_IR_SEND_CMD,NULL,0);
				}

				else if (strncmp (pcommandString, "setIRDef" , strlen(pcommandString)) == 0)
				// {
				// 	// char *pACHexDataName;
				// 	// pACHexDataName = strchr(pcommandString,'_');
				// 	adt_parse_json_info(pdelimPos + 1);

				// 	strncpy(adt_applicationData.adt_hexDataIRName[adt_active_irdev], (pdelimPos + 1), (strlen(pdelimPos + 1) + 1));

				// 	// memset(pACHexDataName,'\0',strlen(pACHexDataName));
						
				// 	strncpy(adt_applicationData.adt_hexDataIRName[adt_active_irdev], pdelimPos+1, (strlen(pdelimPos+1) + 1));
				// 	//adt_util_printf(__LINE__, __FILE_NAME__,"AC Definition : %s \n", adt_applicationData.adt_irACHexData[adt_active_irdev]);
				// 	// adt_util_printf(__LINE__, __FILE_NAME__,"AC Definition Name : %s \n", adt_applicationData.adt_hexDataIRName[adt_active_irdev]);
				// 	adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_GET_AC_DEF,NULL,0);	
				// }
				{
					adt_util_printf(__LINE__, __FILE_NAME__, "[APP] Free memory: %"PRIu32" bytes", esp_get_free_heap_size());
					// adt_util_printf(__LINE__, __FILE_NAME__,"Testing");
					// adt_util_printf(__LINE__, __FILE_NAME__,"Full data received %s",pdelimPos+1);

					// strncpy(adt_applicationData.adt_hexDataIRName[adt_active_irdev], (pdelimPos + 1), (strlen(pdelimPos + 1) + 1));


					// memset(pACHexDataName,'\0',strlen(pACHexDataName));

					// Find the position of the first occurrence of '-' character
    				// const char *delimiterPos = strchr(pdelimPos+1, '-');
					// if (delimiterPos != NULL) 
					// {
					// 	// ------------------Extract AC Hex Data---------------------
					// 	// Calculate the length of the adt_irACHexDataName before the delimiter
					// 	int adt_irACHexDataLength = delimiterPos - (pdelimPos+1);
						
					// 	char *adt_irACHexData = (char *)malloc(adt_irACHexDataLength + 1); // +1 for null terminator
					// 	strncpy(adt_irACHexData, pdelimPos+1, adt_irACHexDataLength);
					// 	adt_irACHexData[adt_irACHexDataLength] = '\0'; // Null terminator
					// 	// printf("Extracted adt_irACHexData: %s\n", adt_irACHexData);
					// 	strncpy(adt_applicationData.adt_irACHexData[adt_active_irdev], adt_irACHexData, ADT_C_IR_AC_HEX_DATA_BYTESIZE);
					// 	free(adt_irACHexData);

					// 	// -------------------Extract AC Hex Name---------------------
					// 	// Calculate the length of the adt_irACHexDataName after the delimiter
					// 	int adt_irACHexDataNameLength = strlen(delimiterPos + 1);

					// 	char *adt_irACHexDataName = (char *)malloc(adt_irACHexDataNameLength + 1); // +1 for null terminator
					// 	strncpy(adt_irACHexDataName, delimiterPos + 1, adt_irACHexDataNameLength);
					// 	adt_irACHexDataName[adt_irACHexDataNameLength] = '\0'; // Null terminator
					// 	// printf("Extracted adt_irACHexDataName: %s\n", adt_irACHexDataName);
					// 	strncpy(adt_applicationData.adt_hexDataIRName[adt_active_irdev], adt_irACHexDataName, ADT_C_IR_AC_HEX_DATA_NAME_BYTESIZE);
					// 	free(adt_irACHexDataName);
					// } else 
					// {
					// 	printf("Delimiter '-' not found in the text.\n");
					// 	strncpy(adt_applicationData.adt_irACHexData[adt_active_irdev], pdelimPos+1, ADT_C_IR_AC_HEX_DATA_BYTESIZE);
					// 	strncpy(adt_applicationData.adt_hexDataIRName[adt_active_irdev], "No AC Defination Name", ADT_C_IR_AC_HEX_DATA_NAME_BYTESIZE);
					// }
					// adt_util_printf(__LINE__, __FILE_NAME__, "[APP] Free memory: %"PRIu32" bytes", esp_get_free_heap_size());
					// adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_GET_AC_DEF,NULL,0);
				}

				else if (strncmp(pcommandString,"getAutoDetectSignal",strlen(pcommandString)) == 0)
				{
					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_AC_AUTO_DETECT,NULL,0);

					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}
					
					adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
				}

				else if (strncmp(pcommandString,"getLearnSignal",strlen(pcommandString)) == 0)
				{
					// adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_AC_AUTO_DETECT,NULL,0);

					// if (uartrespond == true)
					// {
					// 	adt_data = malloc(128);
					// 	snprintf(adt_data, 128, "3:%s",pcommandString);
					// 	adt_sendData_uarttx(adt_data);
					// 	free(adt_data);
					// }

					adt_util_printf(__LINE__, __FILE_NAME__, "3:%s",pcommandString);
				}

				else if (strncmp(pcommandString,"getDeviceState",strlen(pcommandString)) == 0)
				{
					// add event to send all (data & state & info)
					adt_eventPost(ADT_EVENT_IR_APP,ADT_EVENT_DEVICE_STATE,NULL,0);
				}

				else if (strncmp(pcommandString,"resetDevice",strlen(pcommandString)) == 0) //factoryreset
				{
					if (uartrespond == true)
					{
						adt_data = malloc(128);
						snprintf(adt_data, 128, "3:%s",pcommandString);
						adt_sendData_uarttx(adt_data);
						free(adt_data);
					}

					adt_eventPost(ADT_EVENT_SYSTEM,ADT_EVENT_FACTORY_RESET,NULL,0);

				} 

				/************************************************************************************************************************/

				else if (strncmp(pcommandString,"irtxconf",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"irtxdata",strlen(pcommandString)) == 0)
				{

				}
				else if (strncmp(pcommandString,"irlib",strlen(pcommandString)) == 0)
				{

				}
			}
			break;

		case 4:
			if (strncmp(pcommandString,"null",strlen(pcommandString)) == 0)
			{
			}
			else if (strncmp(pcommandString,"NULL",strlen(pcommandString)) == 0)
			{
			}
			else if (strncmp(pcommandString,"Null",strlen(pcommandString)) == 0)
			{
			}
			else
			{
			}
			break;

		default:
			adt_util_printf(__LINE__, __FILE_NAME__, "Invalid type");
			return 1;
	}

	//memset(pcommandString,'\0',strlen(pcommandString));
//	if (pdelimPos)
//	{
//		free(pdelimPos);
//	}

	// xSemaphoreGive(adtprocesscommand_sema);

	return 0;
}

