/************************************************************************************
*																					*
*     Copyright notice: please read file license.txt in the project root folder.    *
*                                              								     	*
************************************************************************************/

package log;

import java.io.File;

public class MyLogManager {
	private static MyLogManager singleInstance =  new MyLogManager();

	//Marking default constructor private
	//to avoid direct instantiation.
	private MyLogManager() {
	}

	//Get instance for class SimpleSingleton
	public static MyLogManager getInstance() {
		return singleInstance;
	}

	public String getLogDirectory()
	{
		String folder = System.getProperty("LogFolder");
		String my_ip = System.getProperty("my_ip");
		if(folder != null && my_ip != null)
		{
			File directory = new File(folder+ File.separator+my_ip);
			directory.mkdirs();

			return directory.getAbsolutePath()+File.separator;
		}

		return "";

	}
}

