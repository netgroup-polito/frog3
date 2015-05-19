package utils.admin;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.google.gson.Gson;

@WebServlet("/migrate_pex")
public class MigratePex extends HttpServlet {

	/**
	 * 
	 */
	private static final long serialVersionUID = 4586579284435807496L;

	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse resp)
			throws ServletException, IOException {
		/* * * * What do I have to do here?
		 * 
		 * - I need to know the ID of the PEX 								[v]
		 * - I have to get userName and MAC address of the desired PEX		[TODO]
		 * - I have to get the port of the PEX I need to migrate			[TODO]
		 * - I need to know the IP address of the target					[v]
		 * - I have to create a new empty PEX in the remote machine			[v]
		 * - I have to tell to the hypervisor "freeze all the data"			[TODO]
		 * - I have to order the local PEX to migrate						[v]
		 * - I have to notify the hypervisor "pex with ID x now has ID y" 	[TODO]
		 * - I havetto tell to the hypervisor "you can go on, now!"			[TODO]
		 */
		
		// - I need to know the ID of the PEX
		final String myPEXid=request.getParameter("id");
		
		// - I have to get userName and MAC address of the desired PEX
		//TODO do this automatically
		final String myPEXname = request.getParameter("name");
		final String myPEXmacaddr = request.getParameter("macaddr");
		
		// - I have to get the port of the PEX I need to migrate
		final String myPEXPort = new Integer(Integer.parseInt(myPEXid) + 10000).toString();
		
		// - I need to know the IP address of the target
		final String targetIP = request.getParameter("target");
		
		// - I have to create a new empty PEX in the remote machine
		final String targetCreateString = "create_empty_pex?user=" + myPEXname + "&macaddr=" + myPEXmacaddr;

		URL remoteurl = new URL(targetIP + "/" + targetCreateString);
		System.out.println("[DEBUG] Contacting this URL: "+ targetIP + "/" + targetCreateString);
		HttpURLConnection connection = (HttpURLConnection) remoteurl.openConnection();
		connection.setConnectTimeout(15000);
		connection.setReadTimeout(15000);
	    connection.setRequestMethod("GET");
	    connection.connect();
	    
	    int status=connection.getResponseCode();
	    System.out.println("[DEBUG] Return code: " + status);

	    BufferedReader read = new BufferedReader(new InputStreamReader(connection.getInputStream()));

	    String response,fullResponse = "";
	    while((response=read.readLine())!=null)
	    {
	    	fullResponse += response;
		}
		final CreatePexResponse cpr = new Gson().fromJson(fullResponse,CreatePexResponse.class);
		read.close();
		connection.disconnect();
		
		// - I have to order the local PEX to migrate
		URL localPEXurl = new URL("http://127.0.0.1:" + myPEXPort + "/jump?target=" + cpr.address);
		System.out.println("[DEBUG] Contacting this URL: " + "http://127.0.0.1:" + myPEXPort + "/jump?target=" + cpr.address);
		HttpURLConnection migrationConn = (HttpURLConnection) remoteurl.openConnection();
		migrationConn.setConnectTimeout(15000);
		migrationConn.setReadTimeout(15000);
		migrationConn.setRequestMethod("GET");
		migrationConn.connect();
		
		int migrationStatus=connection.getResponseCode();
		System.out.println("[DEBUG] Return code: " + migrationStatus);
	}


}
