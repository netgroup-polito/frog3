package filter;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;



public class IPtoURL {
	private static IPtoURL singleInstance =  new IPtoURL();


	private Map<String, String> map;
	//Marking default constructor private
	//to avoid direct instantiation.
	private IPtoURL() {
		this.map = new ConcurrentHashMap<String, String>();
	}

	//Get instance for class SimpleSingleton
	public static IPtoURL getInstance() {
		return singleInstance;
	}

	public void put(String key, String url)
	{
		this.map.put(key, url);
	}

	public String get(String key)
	{
		if(map.containsKey(key))
			return map.remove(key);

		else
			return "goto.myfrog";
	}

}