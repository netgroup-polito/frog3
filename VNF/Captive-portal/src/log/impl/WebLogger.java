/************************************************************************************
*																					*
*     Copyright notice: please read file license.txt in the project root folder.    *
*                                              								     	*
************************************************************************************/

package log.impl;

import java.io.IOException;
import java.util.logging.FileHandler;
import java.util.logging.Logger;


import log.MyLogManager;

public class WebLogger {
	private static WebLogger singleInstance =  new WebLogger();
	private Logger log;
	private FileHandler fh;

	private WebLogger() {
		log  = Logger.getLogger("WebLogger");
		try {

			@SuppressWarnings("unused")
			String folder = System.getProperty("LogFolder");
			@SuppressWarnings("unused")
			String my_ip = System.getProperty("my_ip");
			
			
			fh = new FileHandler(MyLogManager.getInstance().getLogDirectory()+"web.html");
			fh.setFormatter(new  CustomHTMLFormatter()); 
			log.addHandler(fh);  
		} catch (SecurityException e) {
		} catch (IOException e) {
		}
	}
	//Get instance for class SimpleSingleton
	public static WebLogger getInstance() {
		return singleInstance;
	}

	public Logger getLog() {
		return log;
	}
	public FileHandler getFileHandler() {
		return fh;
	}






}