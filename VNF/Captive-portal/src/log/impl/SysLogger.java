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

public class SysLogger {
	private static SysLogger singleInstance =  new SysLogger();
	private Logger log;
	private FileHandler fh;

	//Marking default constructor private
	//to avoid direct instantiation.
	private SysLogger() {
		log  = Logger.getLogger("SysLogger");
		try {


			
			fh = new FileHandler(MyLogManager.getInstance().getLogDirectory()+"sys.html");
			fh.setFormatter(new CustomHTMLFormatter()); 
			log.addHandler(fh);  
		} catch (SecurityException e) {
		} catch (IOException e) {
		}
	}

	//Get instance for class SimpleSingleton
	public static SysLogger getInstance() {

		return singleInstance;
	}

	public Logger getLog() {
		return log;
	}

	public FileHandler getFileHandler() {
		return this.fh;
		
	}
}